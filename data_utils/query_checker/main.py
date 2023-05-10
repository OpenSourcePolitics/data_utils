from metabase_api import Metabase_API
from importlib import import_module
from ..utils import MTB, send_rc_message, dig
import progressbar
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

class MetabaseQueryChecker:
    def __init__(self, collection):
        self.collection = collection

    def create_progressbar(self, value):
        widgets = [' [',
                progressbar.Timer(format= 'elapsed time: %(elapsed)s'),
                '] ',
                progressbar.Bar('*'),' (',
                progressbar.ETA(), ') ',
        ]

        bar = progressbar.ProgressBar(
            max_value=value, 
            widgets=widgets
        ).start()

        return bar

    def query_parser(self):
        cards = MTB.get('/api/card', params={"f":"all"})
        filtered_cards = []
        # Filter cards to be analyzed
        if self.collection:
            filtered_cards = list(
                filter(
                    lambda card: (
                        str(self.collection) in dig(card, ['collection','location']) or
                        dig(card, ['collection', 'id']) == self.collection
                    ),
                    cards
                )
            )
        else:
            filtered_cards = cards

        message = [
            f"Analyzing cards from {MTB.domain}",
            f"{len(filtered_cards)} cards to be analyzed\n"
        ]
        bar = self.create_progressbar(len(filtered_cards))

        # Check if card is working
        card_map = {}
        
        def check_card(card):
            card_id = card['id']
            query_response = MTB.post(f"/api/card/{card_id}/query")
            status = query_response['status']
            if status != 'completed':
                card_map[card_id] = {'status': status}

        def runner():
            threads = []
            with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                for i, card in enumerate(filtered_cards):
                    threads.append(executor.submit(check_card, card))
                for j, task in enumerate(as_completed(threads)):
                    bar.update(j)

        runner()

        if len(card_map) == 0:
            message.append("All clear! All cards worked fine!")
        else:
            for card_id, infos in card_map.items():
                message.append(
                    f"Card's of ID {card_id} status is {infos['status']}:"
                    f"click here {MTB.domain}/card/{card_id} to correct"
                )

        return '\n'.join(message)

    def check_queries(self):
        message = self.query_parser()
        print(message) 
        try:
            send_rc_message(
                self.config,
                message,
                self.config.ROCKETCHAT_CHANNEL
            )
            print("Sending notification to Rocket.Chat worked!")
        except Exception:
            print("Sending notification failed")

def start():
    collection_name = input("Enter collection name you want to analyze: ")
    
    mb_qc = MetabaseQueryChecker(MTB.get_item_id('collection', collection_name))
    mb_qc.check_queries()
