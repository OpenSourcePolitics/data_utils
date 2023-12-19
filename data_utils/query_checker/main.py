from ..utils import MTB, send_rc_message, dig
import progressbar
from concurrent.futures import ThreadPoolExecutor, as_completed
import os
import sys

class MetabaseQueryChecker:
    def __init__(self, collection):
        self.collection = collection

    def create_progressbar(self, value):
        widgets = [
            ' [',
            progressbar.Timer(format='elapsed time: %(elapsed)s'),
            '] ',
            progressbar.Bar('*'), ' (',
            progressbar.ETA(), ') ',
        ]

        bar = progressbar.ProgressBar(
            max_value=value,
            widgets=widgets
        ).start()

        return bar

    def query_parser(self):
        cards = MTB.get('/api/card', params={"f": "all"})
        filtered_cards = []
        # Filter cards to be analyzed
        if self.collection:
            filtered_cards = list(
                filter(
                    lambda card: (
                        str(self.collection) in dig(
                            card,
                            ['collection', 'location']
                        ) or
                        dig(
                            card,
                            ['collection', 'id']
                        ) == self.collection
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
        print(message)
        bar = self.create_progressbar(len(filtered_cards))

        # Check if card is working
        card_map = {}

        def check_card(card):
            card_id = card['id']
            query_response = MTB.post(f"/api/card/{card_id}/query")
            status = query_response['status']
            if status == 'failed':
                card_map[card_id] = {
                    'status': status,
                    'error_type': query_response['error_type'],
                    'error': query_response['error']
                }


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
                    f"click here {MTB.domain}/card/{card_id} to correct\n"
                    f"Error type: {infos['error_type']}\n"
                    f"Error: {infos['error']}\n\n"
                )

        return '\n'.join(message)

    def check_queries(self):
        message = self.query_parser()
        print(message)
        try:
            send_rc_message(
                message,
                "dev"
            )
            print("Sending notification to Rocket.Chat worked!")
        except Exception:
            print("Sending notification failed")


def start():
    if len(sys.argv) == 2:
        collection_value = sys.argv[1]
    else:
        collection_value = input("Enter collection name or ID you want to analyze: ")

    if collection_value.isdigit():
        collection_id = int(collection_value)
    else:
        collection_id = MTB.get_item_id('collection', collection_value)
    mb_qc = MetabaseQueryChecker(collection_id)
    mb_qc.check_queries()
