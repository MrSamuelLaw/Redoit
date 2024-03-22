import re
import json
import aiohttp
import pathlib
import asyncio as aio
from typing import List
from datetime import (datetime,
                      timedelta)
from common import (get_boards,
                    get_lists, 
                    get_cards)
from models import (Credentials,
                    TrelloList,
                    TrelloCard,
                    ListMapping)


async def clone_card(credentials: Credentials, mapping: ListMapping, card: TrelloCard) -> TrelloCard:
    """Clones the TrelloCard from one TrelloList to another TrelloList
    """
    async with aiohttp.ClientSession() as session:
        url = 'https://api.trello.com/1/cards'
        params = {
            'key': credentials.key,
            'token': credentials.token,
            'due': card.due,
            'idList': mapping.target.id,
            'idCardSource': card.id}
        headers = {'Accept': 'application/json'}
        async with session.post(url, headers=headers, params=params) as response:
            obj = await response.json()
            new_card = TrelloCard(**obj)
    return new_card


def parse_mappings(lists: List[TrelloList]) -> List[ListMapping]:
    pattern = r"({.*})"
    mappings: List[ListMapping] = []
    for list_ in lists:
        matches = re.findall(pattern, list_.name)
        if matches:
            try:
                obj = json.loads(matches[0])
                interval, target = obj.get('interval'), obj.get('target')
                target_list = [b for b in lists if b.name == target][0]
                lm = ListMapping(source=list_, target=target_list, interval=interval)
                mappings.append(lm)
            except:
                pass
    return mappings


async def async_main():
    """For each TrelloList mapping it checks which TrelloCards
    are no longer in the target TrelloList and recreates them
    using the template TrelloList
    """
    print('Attempting to clone cards...', flush=True)
    try:
        # read in the app configs
        path = pathlib.Path(__file__)
        path = path.parent
        path = path.joinpath('my_app_configs.jsonc')
        app_configs = json.loads(path.read_text())
        credentials = Credentials(**app_configs.get('credentials'))

        # grab the boards
        boards = await get_boards(credentials)

        # loop over the lists on each board and clone from the source to the target
        for board in boards:
            # this part can probably be consolidated into a function and run async
            lists = await get_lists(credentials, board)
            mappings = parse_mappings(lists)
            for m in mappings:
                source_cards = await get_cards(credentials, m.source)
                target_cards = await get_cards(credentials, m.target)
                source_names = {c.name for c in source_cards}
                target_names = {c.name for c in target_cards}
                diff_names = source_names.difference(target_names)
                diff_cards = [c for c in source_cards if c.name in diff_names]
                for card in diff_cards:
                    due_date = datetime.now() + timedelta(days=m.interval - 1)
                    card.due = card.format_date(due_date)
                    await clone_card(credentials, m, card)
        print('...Successfully cloned cards', flush=True)
    except Exception as e:
        print(f'... Failed to clone cards with error {e}', flush=True)

if __name__ == '__main__':
    aio.run(async_main())




