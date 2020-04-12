
# Creates database tables for storing grams, words and segments
create_db_sql = ''' 
    CREATE TABLE public.gram (
        id integer NOT NULL,
        gram character varying NOT NULL,
        word_id integer NOT NULL
    );

    CREATE SEQUENCE public."Gram_id_seq"
        AS integer
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1;

    ALTER SEQUENCE public."Gram_id_seq" OWNED BY public.gram.id;

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

    CREATE SEQUENCE public.gram_word_id_seq
        AS integer
        START WITH 1
        INCREMENT BY 1
        NO MINVALUE
        NO MAXVALUE
        CACHE 1;

    ALTER SEQUENCE public.gram_word_id_seq OWNED BY public.gram.word_id;

    ALTER TABLE ONLY public.gram ALTER COLUMN id SET DEFAULT nextval('public."Gram_id_seq"'::regclass);

    ALTER TABLE ONLY public.gram ALTER COLUMN word_id SET DEFAULT nextval('public.gram_word_id_seq'::regclass);

    ALTER TABLE ONLY public.segment ALTER COLUMN id SET DEFAULT nextval('public."Segment_id_seq"'::regclass);

    ALTER TABLE ONLY public.segment_word ALTER COLUMN segment_id SET DEFAULT nextval('public."Segment_Word_segment_id_seq"'::regclass);

    ALTER TABLE ONLY public.segment_word ALTER COLUMN word_id SET DEFAULT nextval('public."Segment_Word_word_id_seq"'::regclass);

    ALTER TABLE ONLY public.word ALTER COLUMN id SET DEFAULT nextval('public."Word_id_seq"'::regclass);
    
    ALTER TABLE ONLY public.segment_word ALTER COLUMN id SET DEFAULT nextval('public."Segment_word_id_seq"'::regclass);

'''

delete_data_sql = '''
    DROP TABLE public.gram;
    DROP TABLE public.word;
    DROP TABLE public.segment;
    DROP TABLE public.segment_word;
'''

def begin_insert():
    return '''
        DO $$
        DECLARE new_segment_id integer;
        DECLARE new_word_id integer;

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
        ON CONFLICT(word) DO UPDATE SET word=EXCLUDED.word 
        RETURNING id INTO new_word_id;

        INSERT INTO segment_word (word_id, segment_id) VALUES (new_word_id, new_segment_id);

        '''

def insert_gram_sql(gram_text):
    return f'''
        INSERT INTO gram (gram, word_id) VALUES ('{gram_text.replace("'", "''")}', new_word_id);
        
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
        SELECT word, word_count FROM word JOIN 
        (SELECT word_id, COUNT(word_id) as word_count FROM gram 
        WHERE gram.gram IN ({tmp})
        GROUP BY word_id) RESULTS
        ON word.id = RESULTS.word_id
        ORDER BY word_count DESC
        LIMIT {limit}

    '''

def fuzzy_match_segments(grams, limit=10):
    tmp = ''
    i = 0
    for key, gram in grams.items():
        tmp += f"'{gram.text}'"
        if i != len(grams.items()) -1:
            tmp += ', '
        i += 1
    return f'''
        SELECT * FROM segment JOIN (
            SELECT DISTINCT  ON (segment_word.word_id) * FROM segment_word JOIN (
                SELECT word.id as word_id, word, word_count FROM word JOIN 
                (SELECT word_id, COUNT(word_id) as word_count FROM gram 
                WHERE gram.gram IN ({tmp})
                GROUP BY word_id) RESULTS
                ON word.id = RESULTS.word_id
                ORDER BY word_count DESC
                LIMIT {limit}
            ) MATCHES ON segment_word.word_id = MATCHES.word_id ORDER BY segment_word.word_id
        ) TMP ON segment.id = TMP.segment_id
        ORDER BY word_count DESC LIMIT {limit}
    '''

