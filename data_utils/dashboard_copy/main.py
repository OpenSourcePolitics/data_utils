#from pprint import pprint
#from pdb import set_trace
from ..utils import MTB, modify_dict
import re
import json
import logging

# Setup basic configuration for logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

MESSAGE_DASHBOARD_ID = 'Enter dashboard id to be copied: '
MESSAGE_COLLECTION_ID = 'Enter the collection id where the dashboard will be copied to: '
MESSAGE_DASHBOARD_NAME = 'Enter the new dashboard name: '
MESSAGE_DASHBOARD_DESCRIPTION = 'Optional - Enter the new dashboard description: '
MESSAGE_DASHBOARD_ID_REPLACE_DB = 'Enter dashboard id: '
MESSAGE_NEW_DB = "Enter the id of the database: "
MESSAGE_SCHEMA = "Enter the schema: "


def get_dashboard(dashboard_id):
    return MTB.get(f'/api/dashboard/{dashboard_id}')

def get_all_db_ids(dashboard):
    if 'dashcards' in dashboard and isinstance(dashboard['dashcards'], list):
        return list(set([dashcard['card']['database_id'] for dashcard in dashboard['dashcards'] if 'card' in dashcard and 'database_id' in dashcard['card']]))
    return []

def get_database_info(database_id):
    return MTB.get(f'/api/database/{database_id}?include=tables')

def get_tables_info(database_id, schema=None):
    database_info = get_database_info(database_id)
    if schema: 
        return [{'table_id': table['id'], 'table_name': table['name'], 'schema': table['schema']} for table in database_info['tables'] if table['schema'] == schema]
    else: 
        return [{'table_id': table['id'], 'table_name': table['name'], 'schema': table['schema']} for table in database_info['tables']]


def modify_card_dataset_query(card, db_id, new_table_id):
    modify_dict(card, ['dataset_query', 'database'], db_id)
    modify_dict(card, ['dataset_query', 'query', 'source-table'], new_table_id)

def get_new_field_id(old_field_ids, old_table_id, new_table_id):
    old_table = MTB.get(f'/api/table/{old_table_id}/query_metadata')
    new_table = MTB.get(f'/api/table/{new_table_id}/query_metadata')
    if not old_table:
        logging.error(f"Failed to fetch table metadata for table {old_table_id}")
        return
    elif not new_table:
        logging.error(f"Failed to fetch table metadata for table {new_table_id}")
        return
    field_name_to_new_id = {field['name']: field['id'] for field in new_table['fields']}
    field_id_to_name = {field['id']: field['name'] for field in old_table['fields']}
    new_field_ids = {old_id: field_name_to_new_id[field_id_to_name[old_id]] for old_id in old_field_ids if old_id in field_id_to_name and field_id_to_name[old_id] in field_name_to_new_id}
    return new_field_ids

def update_card_fields(card, card_id, old_table_id, new_table_id):
    card_json_str = json.dumps(card)
    field_ids_to_replace = extract_field_integers(card_json_str)
    new_field_ids = get_new_field_id(field_ids_to_replace, old_table_id, new_table_id)
    
    for field_id in field_ids_to_replace:
        card_json_str = re.sub(rf'"field",\s*{field_id}', f'"field", {new_field_ids[field_id]}', card_json_str)
    
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

def update_dashcard_filters(dashcard, table_id_mapping):
    if dashcard.get("parameter_mappings"):
        old_table_id = dashcard.get("card", {}).get("table_id")
        new_table_id = table_id_mapping.get(old_table_id)
        for mapping in dashcard.get("parameter_mappings", []):
            target_str = json.dumps(mapping.get("target"))
            field_ids_to_replace = extract_field_integers(target_str)
            new_field_ids = get_new_field_id(field_ids_to_replace, old_table_id, new_table_id)
            for field_id in field_ids_to_replace:
                target_str = re.sub(rf'"field",\s*{field_id}', f'"field", {new_field_ids[field_id]}', target_str)
            target = json.loads(target_str)
            mapping["target"] = target
    return dashcard 

def update_dashboard(dashboard_id, dashboard):
    response = MTB.put(f'/api/dashboard/{dashboard_id}', json=dashboard)
    if response:
        logging.info(f"Dashboard {dashboard_id} updated successfully.")
    else:
        logging.error(f"Failed to update dashboard {dashboard_id}")

def replace_dashboard_source_db():
    dashboard_id = input(MESSAGE_DASHBOARD_ID_REPLACE_DB).strip()
    if not dashboard_id.isdigit():
        raise ValueError("The Dashboard ID must be a numeric value.")
    dashboard_id = int(dashboard_id)

    dashboard = get_dashboard(dashboard_id)
    
    old_db_ids = get_all_db_ids(dashboard)
    old_dbs = []
    for db_id in old_db_ids:
        old_dbs.append(
            {
                "db_id": db_id,
                "tables": get_tables_info(db_id)
            }
        )
    
    new_db_id = input(MESSAGE_NEW_DB).strip()
    if not new_db_id.isdigit():
        raise ValueError("The Database ID must be a numeric value.")
    new_db_id = int(new_db_id)
    
    schema_name = input(MESSAGE_SCHEMA).strip()
    if not schema_name:
        raise ValueError("Schema Name is required.")
    
    # we do table mapping
    new_tables = get_tables_info(new_db_id, schema_name) 
    table_id_mapping = {}
    for db in old_dbs:
        old_tables = db['tables']
        for old_table in old_tables:
            for new_table in new_tables:
                if old_table['table_name'] == new_table['table_name'] and old_table['schema'] == new_table['schema']:
                    table_id_mapping[old_table['table_id']] = new_table['table_id']
    

    if 'dashcards' in dashboard and isinstance(dashboard['dashcards'], list):
        for dashcard in dashboard['dashcards']:
            # Check if the dashcard contains a card
            if 'card' in dashcard and 'database_id' in dashcard['card']:
                updated_cards = []
                card = dashcard["card"]
                # We handle the cards that work without join
                if card["table_id"] and card["id"] not in updated_cards: 
                    old_table_id = card["table_id"]
                    new_table_id = table_id_mapping[old_table_id]
                    update_card_db(card["id"], new_db_id, old_table_id, new_table_id)
                    updated_cards.append(card["id"])
                # We handle the cards that work with a join
                dashcard = update_dashcard_filters(dashcard, table_id_mapping)
        update_dashboard(dashboard_id, dashboard)


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

