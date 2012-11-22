# encoding=utf8
'''Post facts'''
# Copyright 2012 by Christopher Foo <chris.foo@gmail.com>
# Licensed under GPLv3. See COPYING.txt for details.
import contextlib
import logging
import random
import re
import sched
import sqlite3
import threading
import time
import warnings

try:
    import tweepy.auth
    import tweepy.api
except ImportError as e:
    warnings.warn(str(e))


_logger = logging.getLogger(__name__)


class Database(object):
    def __init__(self, path):
        super(object)

        self._path = path

        self.create_fact_table()

    @contextlib.contextmanager
    def connection(self):
        con = sqlite3.connect(self._path, isolation_level='DEFERRED',
            detect_types=sqlite3.PARSE_DECLTYPES)

        con.row_factory = sqlite3.Row
        con.execute('PRAGMA synchronous=NORMAL')
        con.execute('PRAGMA journal_mode=WAL')
        con.execute('PRAGMA foreign_keys=ON')

        with con:
            yield con

    def create_fact_table(self):
        with self.connection() as con:
            con.execute('CREATE TABLE IF NOT EXISTS '
                'facts (id INTEGER PRIMARY KEY AUTOINCREMENT,'
                "timestamp INTEGER NOT NULL DEFAULT (strftime('%s', 'now')),"
                'fact TEXT NOT NULL)')

    def get_last_timestamp(self):
        with self.connection() as con:
            cursor = con.execute('SELECT MAX(timestamp) FROM facts LIMIT 1')

            timestamp = cursor.fetchone()

        if timestamp and timestamp[0]:
            return timestamp[0]
        else:
            return 0

    def insert_fact(self, fact):
        with self.connection() as con:
            con.execute('INSERT INTO facts (fact) VALUES (?)', [fact])

    def get_facts(self, after_timestamp=None):
        facts = []

        if not after_timestamp:
            after_timestamp = time.time()

        with self.connection() as con:
            cursor = con.execute('SELECT timestamp, fact FROM facts '
                'WHERE timestamp <= ? '
                'ORDER BY id DESC LIMIT 100', [after_timestamp])

            for row in cursor:
                facts.append((row[0], row[1]))

        return facts


class PostScheduler(threading.Thread):
    def __init__(self, fact_builder, database, api_service, interval=3600 * 6,
    deviation=3600 * 2, retry_delay=30):
        threading.Thread.__init__(self)
        self.daemon = True
        self._interval = interval
        self._deviation = deviation
        self._retry_delay = retry_delay
        self._database = database
        self._fact_builder = fact_builder
        self._api_service = api_service
        self._scheduler = sched.scheduler(time.time, time.sleep)
        self._running = False
        self._fail_count = 0

        self.start()

    def run(self):
        _logger.info('Starting scheduler')
        self._running = True
        self._schedule_post()
        self._scheduler.run()
        _logger.info('Scheduler stopped')

    def _schedule_post(self):
        if not self._running:
            return

        timestamp = self.next_post_timestamp()

        _logger.debug('Schedule post at %s', timestamp)

        self._scheduler.enterabs(timestamp, 1, self._post_fact, ())

    def next_post_timestamp(self):
        last_post_timestamp = self._database.get_last_timestamp()
        next_timestamp = last_post_timestamp + self._interval \
            + random.triangular(-self._deviation, self._deviation)

        return next_timestamp

    def _new_fact(self):
        while True:
            fact_text = self._fact_builder.fact()
            escaped_fact_text = escape_for_twitter(fact_text)

            if len(escaped_fact_text) <= 120:
                return(fact_text, escaped_fact_text)

            _logger.debug('Regen fact')
            time.sleep(0.1)

    def _check_min_timestamp(self):
        last_post_timestamp = self._database.get_last_timestamp()
        next_min_timestamp = last_post_timestamp + self._interval - \
            self._deviation

        return time.time() > next_min_timestamp

    def _post_fact(self):
        if not self._running:
            return

        if not self._check_min_timestamp():
            _logger.warning('Attempted to post but too early now=%s past=%s',
                time.time(), self._database.get_last_timestamp())
            self._schedule_post()
            return

        fact_text, escaped_fact_text = self._new_fact()

        try:
            _logger.debug('Try post text')
            self._api_service.post_message(escaped_fact_text)
            _logger.debug('OK posting')
        except Exception:
            self._fail_count += 1
            delay = min(self._retry_delay * self._fail_count, 3600)
            _logger.exception('Post text failed, retry after %s', delay)
            self._scheduler.enter(delay, 1, self._post_fact, ())

            return

        self._fail_count = 0

        _logger.debug('Insert fact into db')
        self._database.insert_fact(fact_text)
        self._schedule_post()

    def stop(self):
        _logger.debug('Stopping')
        self._running = False

        for event in self._scheduler.queue:
            self._scheduler.cancel(event)


class TwitterAPIService(object):
    def __init__(self, consumer_key, consumer_secret, access_token,
    access_token_secret):
        self._auth = tweepy.auth.OAuthHandler(consumer_key, consumer_secret)
        self._auth.apply_auth(access_token, access_token_secret)
        self._api = tweepy.api.API(self._auth)
        self.check_auth()

    def post_message(self, text):
        _logger.debug('Updating status to %s', text)

        self._api.update_status(text)

        _logger.info('Status updated: %s', text)

    def check_auth(self):
        _logger.debug('Check if auth ok')

        user_model = self._api.me()

        if user_model:
            _logger.debug('Check ok name=%s', user_model.name)
            return True
        else:
            _logger.debug('Check auth ok failed')
            return False


class NullAPIService(object):
    def __init__(self, *args, **kwargs):
        pass

    def post_message(self, text):
        _logger.debug('Null post message %s', text)

        if random.random() < 0.5:
            _logger.debug('Null post random exception')
            raise Exception('Null post random exception')


TWITTER_ESCAPE_RE = re.compile(
    r'([@#][\w])|([$][A-Za-z])|([\dA-Za-z]\.[A-Za-z][A-Za-z])',
    flags=re.UNICODE)


def escape_for_twitter(text):
    def escape(match_obj):
        for i in range(3):
            match_text = match_obj.group(i + 1)

            if not match_text:
                continue

            if i in (0, 1):
                return u'%s`%s' % (match_text[0], match_text[1:])
            else:
                return u'%s`%s' % (match_text[0:2], match_text[2:])

    return re.sub(TWITTER_ESCAPE_RE, escape, text)
