from metabase_api import Metabase_API
from rocketchat_API.rocketchat import RocketChat
from requests import sessions
import sqlalchemy
import os
import re
import sys


config = os.environ
if not (
    config.get('METABASE_HOST') and
    config.get('METABASE_USERNAME') and
    config.get('METABASE_PASSWORD')
):
    raise AssertionError("Env variables not correctly set")

MTB = Metabase_API(
    config['METABASE_HOST'],
    config['METABASE_USERNAME'],
    config['METABASE_PASSWORD']
)


def dig(dict, keys_list):
    if len(keys_list) == 1:
        return dict.get(keys_list[0])
    else:
        if dict.get(keys_list[0]):
            new_dict = dict[keys_list[0]]
            return dig(new_dict, keys_list[1:])
        else:
            return {}


def modify_dict(original_dict, keys_list, value):
    working_dict = original_dict
    for key in keys_list[:-1]:
        working_dict = working_dict[key]
    working_dict[keys_list[-1]] = value


def send_rc_message(config, message, channel):
    assert config.get('ROCKETCHAT_USERNAME')
    assert config.get('ROCKETCHAT_PASSWORD')
    assert config.get('ROCKETCHAT_URL')
    with sessions.Session() as session:
        rocket = RocketChat(
            config.ROCKETCHAT_USERNAME,
            config.ROCKETCHAT_PASSWORD,
            server_url=config.ROCKETCHAT_URL,
            session=session
        )

    rocket.chat_post_message(
        message,
        channel=channel
    )


def create_dashboard(name, collection_id):
    res = MTB.post(
        "/api/dashboard",
        json={
            'name': name,
            'collection_id': collection_id,
            'collection_position': 1
        }
    )

    return res


def add_cards_to_dashboard(dashboard, chart_list):
    cards_json = {'cards':[], 'ordered_tabs':[]}
    counter = 0
    for chart, created_chart in chart_list:
        counter -= 1
        card_infos_for_dashboard = {
            'id': counter,
            'card_id': created_chart['id'],
            'row': chart.row,
            'col': chart.col,
            'size_x': chart.size_x,
            'size_y': chart.size_y
        }
        cards_json['cards'].append(card_infos_for_dashboard)
    import pdb; pdb.set_trace()
    res = MTB.put(
        f"/api/dashboard/{dashboard['id']}/cards",
        json=cards_json
    )
    assert res == 200

    print(f"Cards added to dashboard {dashboard['id']}")


def get_customer_collection_id(name):
    return MTB.get_item_id('collection', name)


def get_answer_model_id(
    customer_name, model_name='Réponses aux questionnaires'
):
    models_collection = MTB.get_item_id(
        'collection',
        f'MODÈLES - {customer_name}', collection_name=customer_name
    )
    return MTB.get_item_id('card', model_name, collection_id=models_collection)


def to_snake(name):
    name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()


def get_database_connection(
    db_name,
    db_schema_wanted='public',
    table_name=None
):
    config = os.environ

    try:
        db_host_and_port = (
            f"{config['DATABASE_HOST']}:{config['DATABASE_PORT']}"
        )
        db_password = config['DATABASE_PASSWORD']
        db_username = config['DATABASE_USERNAME']
    except KeyError:
        db_host_and_port = input(
            "Enter database host and port (ex: 255.42.3.12:5432): "
        )
        db_password = input("Enter Postgres database password: ")
        db_username = input("Enter Postgres database username: ")

    db_name = db_name or input("Enter Postgres database name: ")
    table_name = table_name or db_schema_wanted

    connection = sqlalchemy.create_engine(
        f"postgresql://{db_username}:{db_password}"
        f"@{db_host_and_port}"
        f"/{db_name}",
        connect_args={'options': f'-csearch_path={db_schema_wanted},public'}
    )

    connection.connect()
    return connection, db_schema_wanted, table_name


def log(message):
    old_stdout = sys.stdout
    log_file = open("data_utils.log", "w")
    sys.stdout = log_file
    print(message)
    sys.stdout = old_stdout
    log_file.close()

def get_collection_cards(collection_name):
    collection_id = MTB.get_item_id('collection', collection_name)
    cards = MTB.get('/api/card', params={"f": "all"})
    filtered_cards = []
    # Filter cards to be analyzed
    if collection_id:
        filtered_cards = list(
            filter(
                lambda card: (
                    str(collection_id) in dig(
                        card,
                        ['collection', 'location']
                    ) or
                    dig(
                        card,
                        ['collection', 'id']
                    ) == collection_id
                ),
                cards
            )
        )
    else:
        filtered_cards = cards
    return filtered_cards
