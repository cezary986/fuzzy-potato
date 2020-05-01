from Levenshtein import distance as levenshtein_distance
from fuzzy_potato.text_processing import TextDataFactory


def sort_results_by_distance(db_results: list) -> list:
    db_results.sort(key=lambda element: element['distance'])
    return db_results


def format_words_results(query: str, db_results) -> dict:
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


def format_segments_results(query: str, db_results):
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
