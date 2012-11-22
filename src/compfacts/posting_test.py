from compfacts.grammar import FactBuilder
from compfacts.posting import Database, escape_for_twitter, PostScheduler
import shutil
import tempfile
import threading
import time
import unittest


class MockAPIService(object):
    def post_message(self, text):
        raise NotImplementedError()


class TestDatabase(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_database(self):
        '''It should insert and get facts'''

        database = Database(self.temp_dir + '/test.db')

        self.assertFalse(database.get_last_timestamp())

        database.insert_fact(u'kittens')
        database.insert_fact(u'hi')
        database.insert_fact(u'hello')
        facts = database.get_facts()

        self.assertTrue(facts)
        self.assertEqual(facts[0][1], u'hello')
        self.assertEqual(facts[1][1], u'hi')
        self.assertEqual(facts[2][1], u'kittens')

        self.assertAlmostEqual(database.get_last_timestamp(), time.time(),
            delta=2.0)
        self.assertGreaterEqual(facts[0][0], facts[1][0])


class TestEscape(unittest.TestCase):
    def test_at_symbol(self):
        self.assertEqual(escape_for_twitter(u'''something @kitten function'''),
            u'''something @`kitten function''')

    def test_hash_symbol(self):
        self.assertEqual(escape_for_twitter(u'''something #kitten function'''),
            u'''something #`kitten function''')

    def test_dollar_symbol(self):
        self.assertEqual(escape_for_twitter(u'''something $kitten function'''),
            u'''something $`kitten function''')

    def test_domain_similar(self):
        self.assertEqual(escape_for_twitter(u'''I love my Game.com device!'''),
            u'''I love my Game.`com device!''')

    def test_multi(self):
        self.assertEqual(escape_for_twitter(u'''Game.com $uper f@ntastic'''),
            u'''Game.`com $`uper f@`ntastic''')

    def test_numerics(self):
        self.assertEqual(escape_for_twitter(
            u'''$123.456 money #1 person @0x0000'''),
            u'''$123.456 money #`1 person @`0x0000''')


class TestPostScheduler(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.db = Database(self.temp_dir + '/test.db')

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_post(self):
        event = threading.Event()
        api_service = MockAPIService()
        fact_builder = FactBuilder()

        api_service.texts = []
        api_service.tested_error = False

        def post_message(text):
            if len(api_service.texts) == 1 and not api_service.tested_error:
                api_service.tested_error = True
                raise Exception('testing')

            api_service.texts.append(text)

            if len(api_service.texts) > 4:
                event.set()
                post_sched.stop()

        api_service.post_message = post_message

        post_sched = PostScheduler(fact_builder, self.db, api_service,
            interval=0.2, deviation=0.01, retry_delay=0.1)

        event.wait(timeout=5)
        post_sched.stop()
        post_sched.join(timeout=1)

        self.assertEqual(len(api_service.texts), 5)
        self.assertEqual(len(self.db.get_facts()), 5)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
