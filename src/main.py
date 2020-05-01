from fuzzy_potato.api import FuzzyPotato

potato = FuzzyPotato(config={
            'storage': 'postgres',
            'host': 'localhost',
            'port': '5432',
            'username': 'postgres',
            'password': 'postgres',
            'database_name': 'fuzzy_kitten_test'
        })

print(potato.get_db_statistics())

print('write your query:')
query = input()
import time
start_time = time.time()
results = potato.match_for_words(query, limit=10)
print("Matched in:  %s seconds" % (time.time() - start_time))
print('Matches: ')
import json
print(json.dumps(results, sort_keys=True, indent=2))


