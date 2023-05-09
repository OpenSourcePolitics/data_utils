from pprint import pprint
from ..utils import MTB, modify_dict

MESSAGE = 'Enter card id to be modified[Enter -1 if stop wanted]: '

def card_changer(element, path, custom_change=False):
    if not custom_change:
        element_id = int(input(f"Enter new {element} id for migration: "))

    while True:
        card_id = int(input(MESSAGE))
        
        if card_id != -1:
            res = MTB.get(f'/api/card/{card_id}')
        
            if custom_change:
                print("DO YOUR OWN CHANGES")
                pprint(res)
                import pdb; pdb.set_trace()
            else:
                modify_dict(res, path, element_id)

            status_code = MTB.put(f'/api/card/{card_id}',json=res)
            assert status_code == 200
            print(f"card {card_id} changed successfully")
        else:
            break


def db_changer():
    card_changer('database', ['dataset_query','database'])


def model_changer():
    card_changer('model', ['dataset_query', 'query', 'source_table'])

        
def custom_changer():
    card_changer(None, None, True)
