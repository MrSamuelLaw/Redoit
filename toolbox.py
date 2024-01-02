#!../.venv/bin/python3
import re
import json
import aiohttp
from typing import List
from models import (Credentials, 
                    TrelloBoard, 
                    TrelloList, 
                    TrelloCard, 
                    ListMapping)



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

            
    


