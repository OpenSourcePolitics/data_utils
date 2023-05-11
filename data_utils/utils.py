from metabase_api import Metabase_API
from rocketchat_API.rocketchat import RocketChat
from requests import sessions
import os


config = os.environ


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
    for chart, created_chart in chart_list:
        res = MTB.post(
            f"/api/dashboard/{dashboard['id']}/cards",
            json={
                'cardId': created_chart['id'],
                'row': chart.row,
                'col': chart.col,
                'size_x': chart.size_x,
                'size_y': chart.size_y
            }
        )
        assert res is not False


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
