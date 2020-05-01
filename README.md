# Fuzzy Potato
#### Fuzzy matching python library based on PostgreSQL

### Installation

in `/src` directory:
```bash
pip install -r ./requirements.txt
```

You also need to install PostgreSQL, everything was tested on version 11.5.

### Storage and data representation

Fuzzy Potato before being able to perform matching must index the text. The 
process consists of two stages:
* text data extraction 
* saving data to database

At the first stage Fuzzy Potato breaks down text recursively to smaller
and smaller pieces. First it extract `segments` - in most of the cases those will 
be equal to sentences (tokenizing by dots, exclamation marks etc.). `Segments` further break downs
to `words`. And finally `words` are break down to `grams`. `Grams` here means sufixes. Fuzzy Potato 
uses sufixes with a length of three characters. For example for word potato its `grams` will be:
* pot
* ota
* tat
* ato
* to# - where # is a symbol of the end of word

### Usage

> To use it you need already created PostgreSQL database

First you need to setup database by creating all the tables, indexes and so on. You 
can do this with following code:
```python
from fuzzy_potato.database.postgres import PostgresStorage


storage = PostgresStorage({
            'host': 'yourHost',
            'port': 'yourPort',
            'username': 'yourUsername',
            'password': 'yourPassword',
            'database_name': 'yourDatabaseName'
        })
storage.setup_database()
storage.finish()
```

Before being able to fuzzy much you need to index text. This process may take a while especially for 
big texts (few minutes for a decent size book - 759 pages). There are two methods for this:
* `index_text(text: str)` - index text variables
* `index_text_file(path: str)` - index text content of the file given the path. Note that it must be a plain text file.
```python
from fuzzy_potato.api import FuzzyPotato


potato = FuzzyPotato(config={
            'storage': 'postgres',
            'host': 'localhost',
            'port': '5432',
            'username': 'postgres',
            'password': 'postgres',
            'database_name': 'fuzzy_kitten_test'
        })

potato.index_text('Your text to index.')
# or
potato.index_text_file('./text_file.txt')
``` 

Now everything is ready for some fuzzy matching. Fuzzy Potato has two methods for this:
* `match_for_words(query: str, limit=10)` - find best matching words
* `match_for_segments(query: str, limit=10)` - find best matching segments

### How the matching works?

For words matching it just search for the word with the highest number of matching `grams` - sufixes. At the
end it calculate Levenshtein distance on the given results to sort them.

For segments matching it first perform word matching for every word in query. Then it match the best fitting 
words for segments saving the words position in segments. It stores the lowest and highest position and
using them extract the substring from the segment. For example for segment:
`Lorem ipsum dolor sit amet, consectetur adipiscing elit`
where matching words are:
* `ipsum` - position 2
* `amet`- position 5
it will create a substring:
`ipsum dolor sit amet`
Then at the end it calculate Levenshtein distance between query and such substring for every result. The results are then
sorted by this distance ascending.