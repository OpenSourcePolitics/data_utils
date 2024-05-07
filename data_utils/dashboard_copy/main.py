from pprint import pprint
from pdb import set_trace
from ..utils import MTB, modify_dict
import pandas as pd
import re
import json
import logging

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MESSAGE_DASHBOARD_ID = 'Enter dashboard id to be copied: '
MESSAGE_COLLECTION_ID = 'Enter the collection id where the dashboard will be copied to: '
MESSAGE_DASHBOARD_NAME = 'Enter the new dashboard name: '
MESSAGE_DASHBOARD_DESCRIPTION = 'Optional - Enter the new dashboard description: '


def get_dashboard(dashboard_id):
    return MTB.get(f'/api/dashboard/{dashboard_id}')

def filter_cards(dashboard):
    if 'dashcards' in dashboard and isinstance(dashboard['dashcards'], list):
        filtered_cards = []
        for dashcard in dashboard['dashcards']:
            if 'card' in dashcard and 'database_id' in dashcard['card']:
                card = dashcard['card']
                filtered_cards.append({
                    'id': card['id'],
                    'name': card['name'],
                    'database_id': card['database_id'],
                    'old_table_id': card.get('table_id', None)
                })
        return filtered_cards
    return []

def get_database_info(database_id):
    return MTB.get(f'/api/database/{database_id}?include=tables')

def merge_cards_with_tables(cards, database_id):
    database_info = get_database_info(database_id)
    tables_info = [{'old_table_id': table['id'], 'table_name': table['name']} for table in database_info['tables']]
    tables_df = pd.DataFrame(tables_info)
    return pd.merge(cards, tables_df, on='old_table_id', how='left')

def update_cards_dataframe(cards_df):
    if 'table_name_x' in cards_df.columns:
        cards_df['table_name'] = cards_df['table_name_x'].combine_first(cards_df['table_name_y'])

        cards_df.drop(['table_name_x', 'table_name_y'], axis=1, inplace=True)
    return cards_df

def get_prod_tables_info(database_id):
    database_info = get_database_info(database_id)
    return [{'new_table_id': table['id'], 'new_table_name': table['name']} for table in database_info['tables'] if table['schema'] == 'prod']

def modify_card_dataset_query(card, db_id, new_table_id):
    modify_dict(card, ['dataset_query', 'database'], db_id)
    modify_dict(card, ['dataset_query', 'query', 'source-table'], new_table_id)


def update_card_fields(card, card_id, old_table_id, new_table_id):
    old_table = MTB.get(f'/api/table/{old_table_id}/query_metadata')
    new_table = MTB.get(f'/api/table/{new_table_id}/query_metadata')
    if not old_table or not new_table:
        logging.error(f"Failed to fetch table metadata for card {card_id}")
        return
    card_json_str = json.dumps(card)
    field_ids_to_replace = extract_field_integers(card_json_str)
    field_name_to_new_id = {field['name']: field['id'] for field in new_table['fields']}
    field_id_to_name = {field['id']: field['name'] for field in old_table['fields']}
    #updated_field_ids = [field_name_to_new_id[field_id_to_name[field_id]] for field_id in field_ids_to_replace if field_id_to_name[field_id] in field_name_to_new_id]
    

    for field_id in field_ids_to_replace:
        card_json_str = re.sub(rf'"field",\s*{field_id}', f'"field", {field_name_to_new_id[field_id_to_name[field_id]]}', card_json_str)
    
    card = json.loads(card_json_str)
    return card

def update_card_db(card_id, db_id, old_table_id, new_table_id):
    try:
        card_to_update = MTB.get(f'/api/card/{card_id}')
        
        if not card_to_update:
            logging.error(f"Failed to fetch card {card_id}")
            return
        
        modify_card_dataset_query(card_to_update, db_id, new_table_id)
        card_to_update = update_card_fields(card_to_update, card_id, old_table_id, new_table_id)
        
        response = MTB.put(f'/api/card/{card_id}', json=card_to_update)
        if response:
            logging.info(f"Card {card_id} updated successfully.")
        else:
            logging.error(f"Failed to update card {card_id}")
    except Exception as e:
        logging.error(f"Unexpected error during card update: {str(e)}")

def extract_field_integers(json_str):
    field_values = []
    matches = re.findall(r'"field",\s*(\d+)', json_str)
    for match in matches:
        field_values.append(int(match))
    field_values = list(set(field_values))
    return field_values

def replace_dashboard_source_db():
    dashboard_id = int(input(MESSAGE_DASHBOARD_ID))
    dashboard = get_dashboard(dashboard_id)
    filtered_cards = filter_cards(dashboard)
    cards_df = pd.DataFrame(filtered_cards)
    
    unique_database_ids = cards_df['database_id'].unique()
    for database_id in unique_database_ids:
        cards_df = merge_cards_with_tables(cards_df, database_id)
        cards_df = update_cards_dataframe(cards_df)
    
    db_id = int(input("Enter the id of the database: "))
    tables_info = get_prod_tables_info(db_id)
    tables_df = pd.DataFrame(tables_info)
    cards_df = pd.merge(cards_df, tables_df, left_on='table_name', right_on='new_table_name', how='left')
    print(cards_df)
    
    for index, row in cards_df.iterrows():
        card_id = row['id']
        new_table_id = row['new_table_id']
        old_table_id = row['old_table_id']
        update_card_db(card_id, db_id, old_table_id, new_table_id)

def dashboard_copy():
    try:
        dashboard_id = input(MESSAGE_DASHBOARD_ID).strip()
        if not dashboard_id.isdigit():
            raise ValueError("Dashboard ID must be a numeric value.")
        dashboard_id = int(dashboard_id)

        collection_id = input(MESSAGE_COLLECTION_ID).strip()
        if not collection_id.isdigit():
            raise ValueError("Collection ID must be a numeric value.")
        collection_id = int(collection_id)

        dashboard_name = input(MESSAGE_DASHBOARD_NAME).strip()
        if not dashboard_name:
            raise ValueError("Dashboard Name is required.")

        dashboard_description = input(MESSAGE_DASHBOARD_DESCRIPTION).strip()

        payload = {
            "name": dashboard_name,
            "description": dashboard_description,
            "collection_id": collection_id,
            "is_deep_copy": True
        }

        response = MTB.post(f'/api/dashboard/{dashboard_id}/copy', json=payload)
        if response:
            logging.info("Dashboard copied successfully.")
        else:
            logging.error(f"Failed to copy dashboard: {dashboard_id}")
    except ValueError as ve:
        logging.error(f"Input error: {str(ve)}")
    except Exception as e:
        logging.error(f"Unexpected error: {str(e)}")

