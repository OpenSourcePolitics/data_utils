import sqlalchemy
import pandas as pd

from ..utils import MTB


def main():
    connection, table_name = get_database_connection()
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

    db_id = int(input("Enter database ID on Metabase: "))
    MTB.post(f'/api/database/{db_id}/sync_schema')
    print(
        "Database successfully synchronized, "
        "you should now see the imported tables"
    )


def get_database_connection():
    db_host_and_port = input(
        "Enter database host and port (ex: 255.42.3.12:5432): "
    )
    db_password = input("Enter Postgres database password: ")
    db_username = input("Enter Postgres database username: ")
    db_name = input("Enter Postgres database name: ")

    dbschema_wanted = (
        input("Enter name of the wanted schema[default: public]: ")
        or 'public'
    )
    table_name = (
        input("Enter table_name(default : same as schema name): ")
        or dbschema_wanted
    )

    connection = sqlalchemy.create_engine(
        f"postgresql://{db_username}:{db_password}"
        f"@{db_host_and_port}"
        f"/{db_name}",
        connect_args={'options': f'-csearch_path={dbschema_wanted},public'}
    )

    connection.connect()
    return connection, table_name
