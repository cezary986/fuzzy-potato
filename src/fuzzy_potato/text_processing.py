from nltk.tokenize import sent_tokenize
import nltk 
from sys import getsizeof

import sys
sys.path.append('..')

from fuzzy_potato.core import TextData, SegmentData, WordData, GramData


class TextDataFactory(object):

    @classmethod
    def _get_segments(clss, text):
        segments = sent_tokenize(text)
        segments_data = []
        for segment_text in segments:
            segments_data.append(SegmentData(segment_text))
        return segments_data

    @classmethod
    def _segment_to_words(clss, segment_text):
        words = nltk.word_tokenize(segment_text)
        words=[word.lower() for word in words if word.isalpha()]
        words_data = {}
        for word_text in words:
            if word_text not in words_data:
                words_data[word_text] = WordData(word_text)
        return words_data

    @classmethod
    def _split_to_sufixes(clss, word_text):
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
            grams_data[gram_text] = GramData(gram_text)
            index_from = index_from + 1
        return grams_data

    @classmethod
    def make(clss, text):
        text_data = TextData()
        text_data.segments = TextDataFactory._get_segments(text)
        print(text_data.segments)
        for segment in text_data.segments:
            segment.words = TextDataFactory._segment_to_words(segment.text)
            for key, word in segment.words.items():
                word.grams = TextDataFactory._split_to_sufixes(word.text)
        return text_data


