import unittest
import sys
sys.path.insert(0, '..')
from fuzzy_potato.database.sql import create_db_sql
from fuzzy_potato.database.postgres import PostgresStorage
from fuzzy_potato.text_processing import TextDataFactory


print('Creating db tables...')
storage = PostgresStorage({
            'host': 'localhost',
            'port': '5432',
            'username': 'postgres',
            'password': 'postgres',
            'database_name': 'fuzzy_kitten_test'
        })

storage.drop_database()
storage.finish()


storage.setup_database()

print('Extracting text data...')
text = None
with open('../../data/little_woman.txt', 'r') as myfile:
    text = myfile.read()

text_data = TextDataFactory.make(text)

print('Saving text data to db...')
storage.save_data(text_data)
#
