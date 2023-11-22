import pandas as pd
from ..utils import MTB, get_database_connection, log


def get_data():
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

    return df


def main(df=pd.DataFrame(), db_name=None, db_schema_wanted='public', table_name='main'):
    db_schema_wanted = input('Enter schema wanted: ')
    table_name = input('Enter table name (if none, default is "main"): ') or table_name
    message = ""
    connection, schema, table = get_database_connection(
        db_name,
        db_schema_wanted=db_schema_wanted,
        table_name=table_name
    )
    exported_df = df if not df.empty else get_data()
    exported_df.to_sql(
        table,
        connection,
        if_exists='replace',
        index=False
    )
    message += "Data successfully sent to Metabase to provided database"

    try:
        db_name = connection.engine.url.database
        db_id = MTB.get_item_id('database', db_name)
        MTB.post(f'/api/database/{db_id}/sync_schema')
        message += (
            f"Database {db_name} with ID {db_id} successfully synchronized, "
            f"you should now see the imported tables in the schema {schema} "
            f" and table named {table}. "
            f"Click here : {MTB.domain}/browse/{db_id}"
        )
    except Exception:
        message += f"No database found named {db_name}"

    log(message)
