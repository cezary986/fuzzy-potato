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
    text_data = TextDataFactory.make(text)
    logging.info('Saving extracted text data to database')
    self._storage.save_data(text_data)
    logging.info('Text data saved successfully')

  def index_text_file(self, file_path: str):
    text = None
    with open(file_path, 'r') as text_file:
      text = text_file.read()
    self.index_text(text)

  def _sort_results(self, query: str, db_results):
    for element in db_results:
      first = True
      print(element['words'])
      for word in element['words'].values():
        if not first:
          element['match']['text'] += ' '
        element['match']['text'] += word['text']
        first = False
          
      element['match']['distance'] = levenshtein_distance(element['match']['text'], query)
    db_results.sort(key=lambda element : element['match']['distance'])
    return db_results

  def _format_result(self, query: str, db_results):
    results = []
    for element in db_results:
      tmp = {}
      tmp['segment'] = {}
      tmp['segment']['id'] = element[0]
      tmp['segment']['text'] = element[1]
      tmp['match'] = {
        'text': '',
        'distance': None
      }
      tmp['words'] = {
        element[2]: {
          'id': element[3],
          'text':  element[2]
        }
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
    result = self._format_result(query, result)
    return self._sort_results(query, result)

  def match_for_segments(self, query: str, limit=10):
    self._validate_query(query)
    query_grams = TextDataFactory._split_to_sufixes(query.lower())
    result = self._storage.match_grams_for_segments(query_grams, limit=limit)
    result = self._format_result(query, result)
    return result
