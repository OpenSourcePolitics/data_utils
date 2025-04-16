from sqlalchemy import create_engine, text
import pandas as pd
import os

def make_form_filters():
    db_name = input("Enter the client database name: ")
    questionnaire_id = int(input("Enter the ID of the questionnaire to filter: "))

    fetch_and_dump(db_name, questionnaire_id)

def get_postgres_connection(db_name):

    try:
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
        connection = engine.connect()
        print("Successfully connected to the PostgreSQL database")
        return connection
    
    except Exception as e:
        print(f"Failed to connect to PostgreSQL: {e}")
        raise

def retrieve_form_answers(questionnaire_id, connection):
    query = f"""
                SELECT 
                    session_token,
                    question_type,
                    question_title,
                    answer,
                    decidim_questionnaire_id,
                    position
                FROM prod.forms_answers
                WHERE question_type = 'single_option'
                AND decidim_questionnaire_id = {questionnaire_id}
            """

    form_answers = pd.read_sql(query, connection)

    if form_answers.empty:
        raise AssertionError(f"No questionnaire found for {db_name} with id {questionnaire_id}")
    
    return form_answers

def answers_to_filters(form_answers):
    "Pivots a form_answers dataframe in order to generate a table to use in Metabase as questionnaire filters"
    
    form_answers['filter_name'] = form_answers['position'].astype(str) + '. ' + form_answers['question_title']
    form_filters = form_answers.pivot(index='session_token', columns='filter_name', values='answer')

    return form_filters

def dump_df_to_postgresql(questionnaire_id, connection, form_filters):
    "Dump a form_filters dataframe to a PostgreSQL table"
    table_name = f'questionnaire{questionnaire_id}_filters'

    try:
        form_filters.to_sql(table_name, connection, if_exists='append', index=False)
        print(f"Data for {table_name} dumped successfully into the table.")
    except Exception as e:
        print(f"Failed to dump data into {table_name}: {e}")

def fetch_and_dump(db_name, questionnaire_id):
    connection = get_postgres_connection(db_name)

    form_answers = retrieve_form_answers(questionnaire_id, connection)

    form_filters = answers_to_filters(form_answers)

    dump_df_to_postgresql(questionnaire_id, connection, form_filters)

    connection.close()