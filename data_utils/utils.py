from metabase_api import Metabase_API
from rocketchat_API.rocketchat import RocketChat
from requests import sessions
import dotenv

config = dotenv.dotenv_values()

MTB =  Metabase_API(
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
            return dig(new_dict,keys_list[1:])
        else:
            return None


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

def load_yaml(filename):
    with open(filename,'r') as file:
        return safe_load(file)