from citric import Client
import io
import os
import pandas as pd
from ..file_import.main import main as file_importer
import dotenv

def main():
    config = dotenv.dotenv_values('data_utils/ls_import/.env')

    client = Client(
        config["LS_URL"],
        config["LS_USERNAME"],
        config["LS_PASSWORD"]
    )

    print("List of available surveys: ")
    available_surveys = []
    for survey in client.list_surveys(config["LS_USERNAME"]):
        print(f"ID : {survey['sid']} ||| Name : {survey['surveyls_title']}")
        available_surveys.append(survey['sid'])
    
    survey_id = -1
    while survey_id not in available_surveys:
        survey_id = input("Enter a valid survey ID: ")

    df_answers = pd.read_csv(
        io.BytesIO(client.export_responses(survey_id,file_format="csv")),
        delimiter=";",
        parse_dates=["submitdate"],
        index_col="id",
    )

    file_importer(df_answers)
