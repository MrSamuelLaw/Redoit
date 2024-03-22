import aiohttp
from typing import List
from models import (Credentials,
                    TrelloBoard,
                    TrelloList,
                    TrelloCard)


async def get_boards(credentials: Credentials) -> List[TrelloBoard]:
    """Gets all the boards the user belongs to.
    """
    async with aiohttp.ClientSession() as session:
        template = 'https://api.trello.com/1/members/{}/boards'
        params = {
            'key': credentials.key,
            'token': credentials.token,
        }
        headers = {'Accept': 'application/json'}
        boards: TrelloBoard = []
        for uname in credentials.usernames:
            url = template.format(uname)
            async with session.get(url, headers=headers, params=params) as response:
                array = await response.json()
                for obj in array:
                    board = TrelloBoard(**obj)
                    if not any([b.id == board.id for b in boards]):
                        boards.append(board)
    return boards


async def get_lists(credentials: Credentials, board: TrelloBoard) -> List[TrelloList]:
    """Returns the TrelloLists on the board provided.
    """
    async with aiohttp.ClientSession() as session:
        url = f'https://api.trello.com/1/boards/{board.id}/lists'
        params = {
            'key': credentials.key,
            'token': credentials.token}
        headers = {'Accept': 'application/json'}
        async with session.get(url, headers=headers, params=params) as response:
            array = await response.json()
            for idx, obj in enumerate(array):
                array[idx] = TrelloList(**obj)
    return array


async def get_cards(credentials: Credentials, source: TrelloList) -> List[TrelloCard]:
    """Reads the cards that belong to a list an returns them
    """

    # run the coros
    async with aiohttp.ClientSession() as session:
        url = f'https://api.trello.com/1/lists/{source.id}/cards'
        params = {
            'key': credentials.key,
            'token': credentials.token,}
        headers = {'Accept': 'application/json'}
        async with session.get(url, headers=headers, params=params) as response:
            array = await response.json()
            for idx, obj in enumerate(array):
                array[idx] = TrelloCard(**obj)
    return array


async def move_card(credentials: Credentials, card: TrelloCard, target: TrelloList) -> TrelloCard:
     # run the coros
    async with aiohttp.ClientSession() as session:
        url = f'https://api.trello.com/1/cards/{card.id}'
        params = {
            'key': credentials.key,
            'token': credentials.token,
            'idList': target.id}
        headers = {'Accept': 'application/json'}
        async with session.put(url, headers=headers, params=params) as response:
            obj = await response.json()
            card = TrelloCard(**obj)
    return card
