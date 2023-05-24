import sqlalchemy
import pandas as pd

from ..utils import MTB, get_database_connection


def main():
    connection, table_name, schema = get_database_connection()
    file_name = input("Enter file path with extension: ")

    if '.xlsx' in file_name:
        df = pd.read_excel(file_name)
    elif '.csv' in file_name:
        delimiter = input("Enter delimiter of the file (default:,): ")
        if not delimiter:
            delimiter = ','
        df = pd.read_csv(file_name, delimiter=delimiter)
    elif '.json' in file_name:
        df = pd.read_json(file_name)
    else:
        raise NotImplementedError("None implemented error")

    df.to_sql(
        table_name,
        connection,
        if_exists='replace',
        index=False
    )
    print(f'{file_name} successfully sent to Metabase to provided database')

    try:
        db_name = connection.engine.url.database
        db_id = MTB.get_item_id('database', db_name)
        MTB.post(f'/api/database/{db_id}/sync_schema')
        print(
            f"Database {db_name} with ID {db_id} successfully synchronized, "
            f"you should now see the imported tables in the schema {schema} "
            f" and table named {table_name}. "
            f"Click here : {MTB.domain}/browse/{db_id}"
        )
    except Exception:
        print(f"No database found named {db_name}")
    
    
