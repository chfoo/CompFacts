# encoding=utf8
'''Service'''
# Copyright 2012 by Christopher Foo <chris.foo@gmail.com>
# Licensed under GPLv3. See COPYING.txt for details.
from compfacts.grammar import FactBuilder
from compfacts.posting import (Database, TwitterAPIService, PostScheduler,
    NullAPIService)
import ConfigParser
import argparse
import logging
import os
import logging.handlers


def main():
    arg_parser = argparse.ArgumentParser(
        description='Runs CompFacts Twitter status updater.')
    arg_parser.add_argument('--log-dir', help='Logging directory')
    arg_parser.add_argument('--config', help='Config file path',
        default='/etc/compfacts.conf')
    arg_parser.add_argument('--simulate', help='Simulate posting',
        action='store_true', default=False)
    arg_parser.add_argument('database', help='Database path')

    args = arg_parser.parse_args()

    if args.log_dir:
        if not os.path.exists(args.log_dir):
            os.makedirs(args.log_dir)

        logger = logging.getLogger()
        logger.setLevel(logging.DEBUG)
        handler = logging.handlers.RotatingFileHandler(os.path.join(
            args.log_dir, 'compfacts.log'), maxBytes=4194304, backupCount=9)
        logger.addHandler(handler)
        formatter = logging.Formatter(
            '%(asctime)s %(name)s %(funcName)s:%(lineno)d %(levelname)s '
            '%(message)s')
        handler.setFormatter(formatter)

    config_parser = ConfigParser.ConfigParser()
    config_parser.read([args.config])

    database = Database(args.database)
    fact_builder = FactBuilder()
    sched_kwargs = {}

    if args.simulate:
        api_service = NullAPIService()
        sched_kwargs['interval'] = 30
        sched_kwargs['deviation'] = 5
        sched_kwargs['retry_delay'] = 5
    else:
        consumer_key = Database(config_parser.get('twitter', 'consumer_key'))

        if consumer_key == u'TODO':
            raise Exception('Please set consumer key')

        consumer_secret = Database(config_parser.get('twitter',
            'consumer_secret'))
        access_token = Database(config_parser.get('twitter', 'access_token'))
        access_token_secret = Database(config_parser.get('twitter',
            'access_token_secret'))
        api_service = TwitterAPIService(consumer_key, consumer_secret,
            access_token, access_token_secret)

    post_sched = PostScheduler(fact_builder, database, api_service,
        **sched_kwargs)

    while True:
        try:
            post_sched.join(timeout=1)
        except KeyboardInterrupt:
            break


if __name__ == '__main__':
    main()
