from nltk.tokenize import sent_tokenize
import nltk 
from tinydb import TinyDB, Query
from sys import getsizeof

from storage import WordSearchStorage
from core import save_sufixes, text_to_sufixes

import time


# save_sufixes(db, sufixes)



with open('./text.txt', 'r') as file:
    text = file.read().replace('\n', '')

start_time = time.time()
sufixes = text_to_sufixes(text)
tmp_sufixes = list(text_to_sufixes('Ecst').keys())

print(getsizeof(sufixes))


results = {}

for s in tmp_sufixes:
    words = sufixes.get(s, None)
    if words != None:
        for word in words:
            count = results.get(word, None)
            if count == None:
                results[word] = 1
            else: 
                results[word] = count + 1
print("--- %s seconds ---" % (time.time() - start_time))
print(results)