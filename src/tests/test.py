import unittest
import sys
sys.path.insert(0, '..')
from fuzzy_potato.database.sql import create_db_sql
from fuzzy_potato.database.postgres import PostgresStorage
from fuzzy_potato.text_processing import TextDataFactory


class TestFuzzyKitten(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        TestFuzzyKitten.storage = PostgresStorage({
            'host': 'localhost',
            'port': '5432',
            'username': 'postgres',
            'password': 'postgres',
            'database_name': 'fuzzy_kitten_test'
        })

    # @classmethod
    # def tearDownClass(cls):
    #     TestFuzzyKitten.storage.drop_database()
    #     TestFuzzyKitten.storage.finish()

    def test_matching(self):
        try:
          TestFuzzyKitten.storage.setup_database()

          text = None
          with open('../../data/little_woman.txt', 'r') as myfile:
            text = myfile.read()

          text_data = TextDataFactory.make(text)
          TestFuzzyKitten.storage.save_data(text_data)
          
          QUERY = 'Dashw'
          query_grams = TextDataFactory._split_to_sufixes(QUERY)
          result = TestFuzzyKitten.storage.match_grams(query_grams)
          print('MATCHING: ')
          print(result)

          a = input()
        except Exception as error:
            self.fail('Failed with error: ' + str(error))


if __name__ == '__main__':
    unittest.main()
