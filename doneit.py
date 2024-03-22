import json
import pathlib
import asyncio as aio
from common import (get_boards,
                    get_lists,
                    get_cards,
                    move_card)
from models import Credentials


async def async_main():
    """For each trello card in a list not labeled done,
    move the cards that are completed to the done list
    """
    print('Attempting to move completed cards...', flush=True)
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
            done_list = [l for l in lists if l.name == 'Done']
            if done_list:
                done_list = lists.pop(lists.index(done_list[0]))
                for lst in lists:
                    cards = await get_cards(credentials, lst)
                    for card in cards:
                        if card.dueComplete:
                            card.idLists = done_list.id
                            await move_card(credentials, card, done_list)


        print('...Successfully moved completed cards', flush=True)
    except Exception as e:
        print(f'... Failed to move completed cards with error {e}', flush=True)

if __name__ == '__main__':
    aio.run(async_main())




