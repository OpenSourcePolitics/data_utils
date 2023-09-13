from citric import Client
import io
import pandas as pd
from ..file_import.main import main as file_importer
import dotenv
import sys


def main():
    config = dotenv.dotenv_values('data_utils/ls_import/.env')

    client = Client(
        config["LS_URL"],
        config["LS_USERNAME"],
        config["LS_PASSWORD"]
    )
    if len(sys.argv) < 2:
        print("List of available surveys: ")
        available_surveys = []
        for survey in client.list_surveys(config["LS_USERNAME"]):
            print(
                f"ID : {survey['sid']} ||| Name : {survey['surveyls_title']}"
            )
            available_surveys.append(survey['sid'])

        survey_id = -1
        while survey_id not in available_surveys:
            survey_id = input("Enter a valid survey ID: ")
    else:
        survey_id = str(sys.argv[1])
        db_name = str(sys.argv[2])

    df_answers = pd.read_csv(
        io.BytesIO(client.export_responses(survey_id, file_format="csv")),
        delimiter=";",
        parse_dates=["submitdate"],
        index_col="id",
    )

    file_importer(
        df_answers,
        db_name=db_name,
        db_schema_wanted='limesurvey',
        table_name='limesurvey'
    )
