from doccano_client.beta import DoccanoClient, controllers
from dotenv import dotenv_values

CONFIG = dotenv_values('data_utils/doccano_import/.env')

def main(): 
    # import pdb; pdb.set_trace()
    client = DoccanoClient(CONFIG['DOCCANO_URL'])
    client.login(
        username=CONFIG['DOCCANO_USERNAME'],
        password=CONFIG['DOCCANO_PASSWORD']
    )

    print('LIST OF ALL PROJECTS')
    print('____________________')
    # import pdb; pdb.set_trace()
    # print(client.list_projects())

