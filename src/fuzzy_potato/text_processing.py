from nltk.tokenize import sent_tokenize
import nltk
from sys import getsizeof

import sys

sys.path.append('..')

from fuzzy_potato.core import TextData, SegmentData, WordData, GramData


class TextDataFactory(object):

    @classmethod
    def _get_segments(cls, text):
        segments = sent_tokenize(text)
        segments_data = []
        for segment_text in segments:
            segments_data.append(SegmentData(segment_text))
        return segments_data

    @classmethod
    def _segment_to_words(cls, segment_text):
        words = nltk.word_tokenize(segment_text)
        words = [word.lower() for word in words if word.isalpha()]
        words_data = []
        for i, word_text in enumerate(words):
            words_data.append(WordData(word_text, i))
        return words_data

    @classmethod
    def _split_to_sufixes(cls, word_text, word_position: int = None):
        SUFIX_LENGTH = 3
        index_from = 0
        grams_data = {}
        for char in word_text:
            gram_text = ''
            if index_from + SUFIX_LENGTH <= len(word_text):
                gram_text = word_text[index_from: index_from + SUFIX_LENGTH]
            if index_from + SUFIX_LENGTH - len(word_text) == 1:
                # last sufix is only two chars long with additional special char
                gram_text = word_text[index_from: index_from + SUFIX_LENGTH] + '#'
            if index_from + SUFIX_LENGTH - len(word_text) > 1:
                break
            grams_data[gram_text] = GramData(gram_text, word_position)
            index_from = index_from + 1
        return grams_data

    @classmethod
    def make(cls, text):
        text_data = TextData()
        text_data.segments = TextDataFactory._get_segments(text)
        print(text_data.segments)
        for segment in text_data.segments:
            segment.words = TextDataFactory._segment_to_words(segment.text)
            for i, word in enumerate(segment.words):
                word.grams = TextDataFactory._split_to_sufixes(word.text, i)
        return text_data
