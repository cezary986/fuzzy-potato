
class SearchResult(object):
  pass


class GramData(object):

  def __init__(self, text):
    self.text = text.replace("'", "''")


class WordData(object):

  def __init__(self, text):
    self.text = text.replace("'", "''")
    self.grams = {}

  def add_gram(self, gram):
    if gram.text in self.grams:
      self.grams[gram.text].count += 1
    else:
      self.grams[gram.text] = gram


class SegmentData(object):

  def __init__(self, text):
    self.text = text.replace("'", "''")
    self.words = {}

  def add_word(self, word):
    if word.text in self.words:
      self.words[word.text].count += 1
    else:
      self.words[word.text] = word

      


class TextData(object):

  def __init__(self):
      self.segments = []

  def add_segment(self, segment):
    self.segments.append(segment)


class BaseStorage(object):

  def save_data(self, text_data):
    pass

  def match_query(self, query) -> SearchResult:
    pass
