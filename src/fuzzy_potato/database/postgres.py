
import sys
from fuzzy_potato.core import BaseStorage
import logging
import time
import psycopg2
from .sql import create_db_sql, delete_data_sql, insert_gram_sql, insert_word_sql, insert_segment_sql, begin_insert, end_insert, fuzzy_match_words, fuzzy_match_segments

sys.path.append('..')


class DataBaseConnector():

    def __init__(self):
        self.connection = None
        self.cursor = None

    def connect(self, port, host, username, password, database_name):
        self.port = port
        self.host = host
        self.username = username
        self.password = password
        self.database_name = database_name
        self._connect_self()

    def _connect_self(self):
        try:
            self.connection = psycopg2.connect(
                user=self.username, password=self.password, host=self.host, port=self.port, database=self.database_name)
            self.cursor = self.connection.cursor()
        except (Exception, psycopg2.Error) as error:
            logging.error('Error while connecting to PostgreSQL')
            logging.error(error)
            raise Exception('Error while connecting to PostgreSQL', str(error))

    def disconnect(self):
        if(self.connection):
            self.cursor.close()
            self.connection.close()
            logging.info("Closing PostgreSQL connection")

    def execute_query(self, sql, fetch=False):
        if self.connection.closed > 0:
            self._connect_self()
        try:
            self.cursor.execute(sql)
            self.connection.commit()
            logging.debug('Query finished successfully')
            if fetch:
                return self.cursor.fetchall()
        except (Exception, psycopg2.DatabaseError) as error:
            logging.error('Error while running query: ' + sql)
            self.cursor.execute("ROLLBACK")
            self.connection.commit()
            logging.error(error)
            raise error


class PostgresStorage(BaseStorage):

    def __init__(self, config):
        self.db_connector = DataBaseConnector()
        self.db_connector.connect(
            port=config['port'],
            host=config['host'],
            username=config['username'],
            password=config['password'],
            database_name=config['database_name'],
        )

    def finish(self):
        self.db_connector.disconnect()

    def setup_database(self):
        try:
            self.db_connector.execute_query(create_db_sql)
        except Exception as error:
            logging.error('Failed to setup databse tables')
            logging.error(error)

    def drop_database(self):
        try:
            self.db_connector.execute_query(delete_data_sql)
        except Exception as error:
            logging.error('Failed to setup databse tables')
            logging.error(error)

    def _save_word(self, word):
        sql = insert_word_sql(word.text)
        for key, gram in word.grams.items():
            sql += insert_gram_sql(gram.text)
        return sql

    def _save_segment(self, segment):
        sql = begin_insert()
        sql += insert_segment_sql(segment.text)

        for key, word in segment.words.items():
            sql += self._save_word(word)

        sql += end_insert()
        self.db_connector.execute_query(sql)

    def save_data(self, data):
        try:
            for segment in data.segments:
                self._save_segment(segment)
            logging.info('Text data saved successfully')
        except Exception as error:
            logging.error('Failed to save text data')
            logging.error(error)

    def match_grams_for_words(self, grams, limit=10):
        try:
            start_time = time.time()

            result = self.db_connector.execute_query(
                fuzzy_match_words(grams, limit), fetch=True)

            logging.info("Query executed in:  %s seconds" % (time.time() - start_time))
            logging.info('Query matched')
            return result
        except Exception as error:
            logging.error('Failed to match query')
            logging.error(error)

    def match_grams_for_segments(self, grams, limit=10):
        try:
            import time
            start_time = time.time()

            result = self.db_connector.execute_query(
                fuzzy_match_segments(grams, limit), fetch=True)

            print("--- %s seconds ---" % (time.time() - start_time))

            logging.info('Query matched')
            return result
        except Exception as error:
            logging.error('Failed to match query')
            logging.error(error)
