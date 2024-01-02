#!../.venv/bin/python3
import json
import pathlib
import asyncio as aio
import toolbox as tb
from datetime import datetime, timedelta
from models import Credentials
    

async def async_main():
    """For each TrelloList mapping it checks which TrelloCards
    are no longer in the target TrelloList and recreates them
    using the template TrelloList
    """
    # read in the app configs
    path = pathlib.Path(__file__)
    path = path.parent
    path = path.joinpath('app_configs.jsonc')
    app_configs = json.loads(path.read_text())
    credentials = Credentials(**app_configs.get('credentials'))

    # grab the boards
    boards = await tb.get_boards(credentials)

    # loop over the lists on each board and clone from the source to the target
    for board in boards:
        # this part can probably be consolidated into a function and run async
        lists = await tb.get_lists(credentials, board)
        mappings = tb.parse_mappings(lists)
        for m in mappings:
            source_cards = await tb.get_cards(credentials, m.source)
            target_cards = await tb.get_cards(credentials, m.target)
            source_names = {c.name for c in source_cards}
            target_names = {c.name for c in target_cards}
            diff_names = source_names.difference(target_names)
            diff_cards = [c for c in source_cards if c.name in diff_names]
            for card in diff_cards:
                due_date = datetime.now() + timedelta(days=m.interval)
                card.due = card.format_date(due_date)
                await tb.clone_card(credentials, m, card)


if __name__ == '__main__':
    aio.run(async_main())

