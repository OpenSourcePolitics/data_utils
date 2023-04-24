from metabase_api import Metabase_API
import dotenv
import os

config = dotenv.dotenv_values()

mtb = Metabase_API(
    config['METABASE_HOST'],
    config['METABASE_USERNAME'],
    config['METABASE_PASSWORD']
)

def run():
    database_id = int(input("Enter new database id for migration: "))

    while True:
        indicator_id = int(input('Enter card id to be modified[Enter -1 if stop wanted]: '))
        
        if indicator_id != -1:
            res = mtb.get(f'/api/card/{indicator_id}')
            res['dataset_query']['database'] = database_id

            status_code = mtb.put(f'/api/card/{indicator_id}',json=res)
            assert status_code == 200
            print(f"card {indicator_id} changed successfully")
        else:
            break

def model_changer():
    model_id = int(input("Enter ID of new model:"))
    
    while True:
        indicator_id = int(input('Enter card id to be modified[Enter -1 if stop wanted]: '))
        
        if indicator_id != -1:
            res = mtb.get(f'/api/card/{indicator_id}')
            res['dataset_query']['query']['source_table'] = f"card__{model_id}"

            status_code = mtb.put(f'/api/card/{indicator_id}',json=res)
            assert status_code == 200
            print(f"model of card {indicator_id} changed successfully")
        else:
            break