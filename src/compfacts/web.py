# encoding=utf8
'''RSS and web status'''
# Copyright 2012 by Christopher Foo <chris.foo@gmail.com>
# Licensed under GPLv3. See COPYING.txt for details.
from compfacts.posting import Database
import argparse
import datetime
import time
import tornado.web
import uuid


class AtomFeedHandler(tornado.web.RequestHandler):
    NAMESPACE_UUID = uuid.UUID('fe2c3efb-81e9-4da6-8f25-212453406050')

    def get(self):
        db = self.application.db
        timestamp = int(self.get_argument('before', time.time()))
        facts = []

        for fact_timestamp, fact, fact_id in db.get_facts(timestamp):
            fact_date = datetime.datetime.utcfromtimestamp(fact_timestamp)
            fact_uuid = uuid.uuid5(self.NAMESPACE_UUID,
                '%s.%s' % (fact_id, fact_timestamp))

            facts.append((fact_uuid, fact_date, fact))

        self.render('compfacts.atom', facts=facts)


class Application(tornado.web.Application):
    def __init__(self, database):
        self.db = database
        tornado.web.Application.__init__(self, [
                (r'/compfacts/compfacts.atom', AtomFeedHandler),
            ],
        )


def run_web_server():
    arg_parser = argparse.ArgumentParser(
        description='CompFacts info web server.')
    arg_parser.add_argument('database', help='Database path')

    args = arg_parser.parse_args()

    app = Application(Database(args.database))
    app.listen(9804, 'localhost', xheaders=True)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    run_web_server()
