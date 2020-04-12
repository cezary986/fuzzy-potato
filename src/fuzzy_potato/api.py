import logging 

from Levenshtein import distance as levenshtein_distance
from fuzzy_potato.database.postgres import PostgresStorage
from fuzzy_potato.text_processing import TextDataFactory 

class FuzzyPotato(object):

  def __init__(self, config):
    self.config = config
    self._storage = PostgresStorage(config)

  def index_text(self, text: str):
    text_data = TextDataFactory.make(text)
    logging.info('Saving extracted text data to database')
    self._storage.save_data(text_data)
    logging.info('Text data saved successfully')

  def index_text_file(self, file_path: str):
    text = None
    with open(file_path, 'r') as text_file:
      text = text_file.read()
    self.index_text(text)

  def _prepare_results(self, query: str, db_results):
    results = []
    tmp = None
    for db_result in db_results:
      tmp = {}
      tmp['segment'] = {}
      tmp['segment']['id'] = db_result[0]
      tmp['segment']['text'] = db_result[1]
      tmp['word'] = {}
      tmp['word']['id'] = db_result[5]
      tmp['word']['text'] = db_result[6]
      tmp['word']['distance'] = levenshtein_distance(db_result[6], query)
      results.append(tmp)
    results.sort(key=lambda element : element['word']['distance'])
    return results

  def _validate_query(self, query: str):
    if len(query) < 3:
      logging.error('Query must be at least 3 char long')
      raise ValueError('Query must be at least 3 char long')

  def match_for_words(self, query: str, limit=10):
    self._validate_query(query)
    query_grams = TextDataFactory._split_to_sufixes(query)
    result = self._storage.match_grams_for_segments(query_grams, limit=limit)
    return self._prepare_results(query, result)

  def match_for_segments(self, query: str, limit=10):
    self._validate_query(query)
    query_grams = TextDataFactory._split_to_sufixes(query)
    result = self._storage.match_grams_for_segments(query_grams, limit=limit)
    return self._prepare_results(query, result)
    