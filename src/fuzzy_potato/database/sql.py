
# Creates database tables for storing grams, words and segments
create_db_sql = ''' 
    CREATE TABLE public.gram (
        id integer NOT NULL,
        gram character varying NOT NULL,
        UNIQUE(gram)
    );

    CREATE SEQUENCE public."Gram_id_seq"
        AS integer
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1;

    ALTER SEQUENCE public."Gram_id_seq" OWNED BY public.gram.id;

    CREATE TABLE public.gram_word (
        id integer NOT NULL,
        gram_id integer NOT NULL,
        word_id integer NOT NULL
    );

    CREATE SEQUENCE public."Gram_word_id_seq"
        AS integer
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1;

    ALTER SEQUENCE public."Gram_word_id_seq" OWNED BY public.gram_word.id;

    
    CREATE TABLE public.gram_segment (
        id integer NOT NULL,
        gram_id integer NOT NULL,
        segment_id integer NOT NULL
    );

    CREATE SEQUENCE public."Gram_segment_id_seq"
        AS integer
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1;

    ALTER SEQUENCE public."Gram_segment_id_seq" OWNED BY public.gram_segment.id;

    CREATE TABLE public.segment_word (
        id integer NOT NULL,
        segment_id integer NOT NULL,
        word_id integer NOT NULL
    );

    CREATE SEQUENCE public."Segment_word_id_seq"
        AS integer
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1;

    ALTER SEQUENCE public."Segment_word_id_seq" OWNED BY public.segment_word.id;

    CREATE SEQUENCE public."Segment_Word_segment_id_seq"
        AS integer
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1;

    ALTER SEQUENCE public."Segment_Word_segment_id_seq" OWNED BY public.segment_word.segment_id;

    CREATE SEQUENCE public."Segment_Word_word_id_seq"
        AS integer
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1;

    ALTER SEQUENCE public."Segment_Word_word_id_seq" OWNED BY public.segment_word.word_id;

    CREATE TABLE public.segment (
        id integer NOT NULL,
        segment character varying NOT NULL
    );

    CREATE SEQUENCE public."Segment_id_seq"
        AS integer
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1;

    ALTER SEQUENCE public."Segment_id_seq" OWNED BY public.segment.id;

    CREATE TABLE public.word (
        id integer NOT NULL,
        word character varying NOT NULL UNIQUE
    );

    CREATE SEQUENCE public."Word_id_seq"
        AS integer
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1;

    ALTER SEQUENCE public."Word_id_seq" OWNED BY public.word.id;

    ALTER TABLE ONLY public.gram ALTER COLUMN id SET DEFAULT nextval('public."Gram_id_seq"'::regclass);

    ALTER TABLE ONLY public.segment ALTER COLUMN id SET DEFAULT nextval('public."Segment_id_seq"'::regclass);

    ALTER TABLE ONLY public.segment_word ALTER COLUMN segment_id SET DEFAULT nextval('public."Segment_Word_segment_id_seq"'::regclass);

    ALTER TABLE ONLY public.segment_word ALTER COLUMN word_id SET DEFAULT nextval('public."Segment_Word_word_id_seq"'::regclass);

    ALTER TABLE ONLY public.word ALTER COLUMN id SET DEFAULT nextval('public."Word_id_seq"'::regclass);
    
    ALTER TABLE ONLY public.segment_word ALTER COLUMN id SET DEFAULT nextval('public."Segment_word_id_seq"'::regclass);
        
    ALTER TABLE ONLY public.gram_word ALTER COLUMN id SET DEFAULT nextval('public."Gram_word_id_seq"'::regclass);

    ALTER TABLE ONLY public.gram_segment ALTER COLUMN id SET DEFAULT nextval('public."Gram_segment_id_seq"'::regclass);

'''

delete_data_sql = '''
    DROP TABLE public.gram;
    DROP TABLE public.word;
    DROP TABLE public.segment;
    DROP TABLE public.segment_word;
    DROP TABLE public.gram_word;
    DROP TABLE public.gram_segment;
'''


def begin_insert():
    return '''
        DO $$
        DECLARE new_segment_id integer;
        DECLARE new_word_id integer;
        DECLARE new_gram_id integer;

        BEGIN
        
    '''


def end_insert():
    return '''
        END $$;
    '''


def insert_segment_sql(segment_text):
    return f'''
        INSERT INTO segment (segment) VALUES ('{segment_text.replace("'", "''")}') RETURNING id INTO new_segment_id;
        
        '''


def insert_word_sql(word_text):
    return f'''
        INSERT INTO word (word) VALUES ('{word_text.replace("'", "''")}')
        ON CONFLICT(word) DO NOTHING;
        
        SELECT id INTO new_word_id FROM word WHERE word = '{word_text.replace("'", "''")}';  
        INSERT INTO segment_word (word_id, segment_id) VALUES (new_word_id, new_segment_id);

        '''


def insert_gram_sql(gram_text):
    return f'''
        INSERT INTO gram (gram) VALUES ('{gram_text.replace("'", "''")}') ON CONFLICT(gram) DO NOTHING;
        
        SELECT id INTO new_gram_id FROM gram WHERE gram = '{gram_text.replace("'", "''")}';
        INSERT INTO gram_word (gram_id, word_id) VALUES (new_gram_id, new_word_id);
        INSERT INTO gram_segment (gram_id, segment_id) VALUES (new_gram_id, new_segment_id);
        
        '''


def get_db_statistics():
    return f'''
        SELECT 
            reltuples::bigint AS count 
        FROM  pg_class 
        WHERE  
            oid = 'public.gram'::regclass OR 
            oid = 'public.word'::regclass OR 
            oid = 'public.segment'::regclass OR
            oid = 'public.gram_word'::regclass OR
            oid = 'public.gram_segment'::regclass OR
            oid = 'public.segment_word'::regclass;
        '''

def fuzzy_match_words(grams, limit=10):
    tmp = ''
    i = 0
    for key, gram in grams.items():
        tmp += f"'{gram.text}'"
        if i != len(grams.items()) -1:
            tmp += ', '
        i += 1
    return f'''
        SELECT * FROM word JOIN
            (SELECT gram_word.word_id, COUNT(gram_word.word_id) as word_count from gram_word JOIN
                (SELECT id from gram WHERE  gram IN ({tmp})) GRAMS
            ON gram_word.gram_id = GRAMS.id GROUP BY gram_word.word_id ORDER BY word_count DESC LIMIT {limit}) WORDS_IDS
        ON word.id = WORDS_IDS.word_id
    '''


def fuzzy_match_segments(grams, limit=10):
    tmp = ''
    i = 0
    for key, gram in grams.items():
        tmp += f"'{gram.text}'"
        if i != len(grams.items()) -1:
            tmp += ', '
        i += 1
    res = f'''
    
       SELECT * FROM segment JOIN
            (SELECT gram_segment.segment_id, COUNT(gram_segment.segment_id) as segment_count from gram_segment JOIN
                (SELECT id from gram WHERE  gram IN ({tmp})) GRAMS
            ON gram_segment.gram_id = GRAMS.id GROUP BY gram_segment.segment_id ORDER BY segment_count DESC LIMIT {limit}) SEGMENTS_IDS
        ON segment.id = SEGMENTS_IDS.segment_id
    '''
    return res
