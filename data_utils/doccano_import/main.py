from doccano_client import DoccanoClient
from dotenv import dotenv_values

CONFIG = dotenv_values('data_utils/doccano_import/.env')

def main(): 
    client = DoccanoClient(CONFIG['DOCCANO_URL'])
    client.login(
        username=CONFIG['DOCCANO_USERNAME'],
        password=CONFIG['DOCCANO_PASSWORD']
    )
