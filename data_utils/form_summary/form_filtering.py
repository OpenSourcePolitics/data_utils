from sqlalchemy import create_engine, text
import pandas as pd
import os
import logging

logging.basicConfig()
logging.getLogger('sqlalchemy.engine').setLevel(logging.DEBUG)

def make_form_filters():
    db_name = input("Enter the client database name: ")
    questionnaire_id = int(input("Enter the ID of the questionnaire to filter: "))

    fetch_and_dump(db_name, questionnaire_id)

def get_postgres_engine(db_name):

    config = os.environ
    if not (
        config.get('DATABASE_USERNAME') and
        config.get('DATABASE_PASSWORD') and
        config.get('DATABASE_HOST') and
        config.get('DATABASE_PORT')
    ):
        raise AssertionError("Env variables not correctly set")

    user = config['DATABASE_USERNAME']
    password = config['DATABASE_PASSWORD']
    host =  config['DATABASE_HOST']
    port = config['DATABASE_PORT']
    engine = create_engine(f"postgresql://{user}:{password}@{host}:{port}/{db_name}")
    return engine

def connect_to_postgres(engine):
    try:
        connection = engine.connect()
        print("Successfully connected to the PostgreSQL database")
        return connection
    
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        raise

def retrieve_form_answers(questionnaire_id, engine):
    query = f"""
                SELECT 
                    body,
                    question_type,
                    answer,
                    decidim_questionnaire_id,
                    position
                FROM prod.forms_answers
                WHERE question_type = 'single_option'
                AND decidim_questionnaire_id = {questionnaire_id}
            """
    connection = engine.connect()
    form_answers = pd.read_sql(query, connection)
    connection.close()

    if form_answers.empty:
        raise AssertionError(f"No questionnaire found with id {questionnaire_id}")
    
    return form_answers

def concat_multiple_answers(form_answers):
    "Concatenates multiple answers per question into a single answer"

    df = form_answers.copy()

    df['answer'] = df.\
        groupby(['session_token', 'position'])['answer'].\
        transform(lambda x : ' '.join(x))
    df = df.drop_duplicates(subset=['session_token', 'position', 'answer'])

    return df

def pivot_filters(form_answers):
    "Pivots a form_answers dataframe in order to generate a table to use in Metabase as questionnaire filters"
    
    form_answers['filter_name'] = form_answers['position'].astype(str) + '. ' + form_answers['question_title']
    form_filters = form_answers.pivot(index='session_token', columns='filter_name', values='answer')
    form_filters.columns=form_filters.columns.str.lower().str.replace(' ','_').str.replace("'","_")
    form_filters=form_filters.reset_index()

    return form_filters

def dump_df_to_postgresql(questionnaire_id, engine, form_filters):
    "Dump a form_filters dataframe to a PostgreSQL table"
    table_name = f'questionnaire_{questionnaire_id}_filters'

    try:
        connection = engine.connect()
        form_filters.to_sql(table_name, connection, schema='forms', if_exists='replace', index=False)
        print(f"Data for {table_name} dumped successfully into the table.")
        connection.close()
    except Exception as e:
        print(f"Failed to dump data into {table_name}: {e}")

def fetch_and_dump(db_name, questionnaire_id):
    engine = get_postgres_engine(db_name)

    form_answers = retrieve_form_answers(questionnaire_id, engine)

    form_unique_answers = concat_multiple_answers(form_answers)

    form_filters = pivot_filters(form_unique_answers)

    dump_df_to_postgresql(questionnaire_id, engine, form_filters)