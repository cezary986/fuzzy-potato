import logging

from Levenshtein import distance as levenshtein_distance
from fuzzy_potato.database.postgres import PostgresStorage
from fuzzy_potato.text_processing import TextDataFactory


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
        text = None
        with open(file_path, 'r') as text_file:
            text = text_file.read()
        self.index_text(text)

    def _sort_results(self, query: str, db_results):
        db_results.sort(key=lambda element: element['distance'])
        return db_results

    def _format_result(self, query: str, db_results):
        results = []
        for element in db_results:
            words = TextDataFactory._segment_to_words(element[1])
            match = ''
            for i in range(element[3], element[4] + 1):
                match += (words[i].text + ' ')
            tmp = {
                'segment': {
                    'id': element[0],
                    'text': element[1],
                },
                'distance': levenshtein_distance(query, match)
            }
            results.append(tmp)
        return results

    def _format_words_result(self, query: str, db_results):
        results = []
        for element in db_results:
            tmp = {'word': {
                'id': element[0],
                'text': element[1],
            },
                'distance': levenshtein_distance(query, element[1])
            }
            results.append(tmp)
        return results

    def _reduce_results(self, db_results):
        results = {}
        for element in db_results:
            segment_id = element['segment']['id']
            if segment_id in results:
                results[segment_id]['words'] = {**results[segment_id]['words'], **element['words']}
                print('reduce')
            else:
                results[segment_id] = element
        return list(results.values())

    def _validate_query(self, query: str):
        if len(query) < 3:
            logging.error('Query must be at least 3 char long')
            raise ValueError('Query must be at least 3 char long')

    def match_for_words(self, query: str, limit=10):
        self._validate_query(query)
        query_grams = TextDataFactory._split_to_sufixes(query.lower())
        result = self._storage.match_grams_for_words(query_grams, limit=limit)
        result = self._format_words_result(query, result)
        return self._sort_results(query, result)

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
        result = self._format_result(query, db_results)
        return self._sort_results(query, result)
