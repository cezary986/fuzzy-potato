import logging

from fuzzy_potato.database.postgres import PostgresStorage
from fuzzy_potato.text_processing import TextDataFactory
from fuzzy_potato.format import sort_results_by_distance, format_words_results, format_segments_results


class FuzzyPotato(object):

    def __init__(self, config):
        self.config = config
        self._storage = PostgresStorage(config)

    def get_db_statistics(self):
        return self._storage.get_db_statistics()

    def index_text(self, text: str):
        logging.info('Extracting file data')
        text_data = TextDataFactory.make(text)
        logging.info('Saving extracted text data to database')
        self._storage.save_data(text_data)
        logging.info('Text data saved successfully')

    def index_text_file(self, file_path: str):
        logging.info('Start indexing file: ', file_path)
        with open(file_path, 'r') as text_file:
            text = text_file.read()
        self.index_text(text)

    @staticmethod
    def _validate_query(query: str):
        if len(query) < 3:
            logging.error('Query must be at least 3 char long')
            raise ValueError('Query must be at least 3 char long')

    def match_for_words(self, query: str, limit=10):
        self._validate_query(query)
        query_grams = TextDataFactory._split_to_sufixes(query.lower())
        result = self._storage.match_grams_for_words(query_grams, limit=limit)
        result = format_words_results(query, result)
        return sort_results_by_distance(result)

    def match_for_segments(self, query: str, limit=10):
        words_matches = []
        query_parts = query.split(' ')
        for part in query_parts:
            self._validate_query(query)
            words_matches.append(self.match_for_words(part, limit))

        words = []
        for i in range(0, len(words_matches)):
            words.append(words_matches[i][0]['word']['id'])
        db_results = self._storage.match_words_for_segments(words, limit)
        result = format_segments_results(query, db_results)
        return sort_results_by_distance(result)
