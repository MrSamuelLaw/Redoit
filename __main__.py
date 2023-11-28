#!../.venv/bin/python3
import json
import pathlib
import asyncio as aio
from typing import List, Dict
from datetime import datetime, timedelta
import aiohttp
from models import TrelloList, TrelloCard


async def get_board_lists(base_params: Dict, boardId: str) -> List[TrelloList]:
	"""Returns the TrelloLists on the board"""
	async with aiohttp.ClientSession() as session:  
		url = f'https://api.trello.com/1/boards/{boardId}/lists'
		params = {**base_params}
		headers = {'Accept': 'application/json'}
		async with session.get(url, headers=headers, params=params) as response:
			array = await response.json()
			for idx, obj in enumerate(array):
				array[idx] = TrelloList(**obj)
			return array


async def get_list_cards(base_params: Dict, trello_lists: List[TrelloList]) -> None:
	"""For each TrelloList reads the TrelloCards on the TrelloList 
	and assigns them to the TrelloList.
	
	"""
	# define the coro for each list
	async def _get_list_cards(session: aiohttp.ClientSession, trello_list: TrelloList) -> TrelloList:
		url = f'https://api.trello.com/1/lists/{trello_list.id}/cards'
		params = {**base_params}
		headers = {'Accept': 'application/json'}
		async with session.get(url, headers=headers, params=params) as response:
			array = await response.json()
			for idx, obj in enumerate(array):
				array[idx] = TrelloCard(**obj)
			trello_list.cards = array
	# run the coros
	async with aiohttp.ClientSession() as session: 
		coros = [_get_list_cards(session, tl) for tl in trello_lists]
		await aio.gather(*coros)


async def clone_card(base_params: Dict, from_list: TrelloList, to_list:TrelloList, card: TrelloCard) -> None:
	"""Clones the TrelloCard from one TrelloList to another TrelloList"""
	async with aiohttp.ClientSession() as session:
		url = 'https://api.trello.com/1/cards' 
		params = {**base_params}
		params['due'] = card.due
		params['idList'] = to_list.id
		params['idCardSource'] = card.id
		headers = {'Accept': 'application/json'}
		async with session.post(url, headers=headers, params=params) as response:
				obj = await response.json()
				new_card = TrelloCard(**obj)
				to_list.cards.append(new_card)


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
	base_params = app_configs['base_params']

	for bm in app_configs['board_mappings']:
		boardId = bm['boardId']

		# get the string sets from the mapping
		list_mapping = bm['list_mapping']
		list_names = {lm['origin'] for lm in list_mapping}
		list_names = list_names.union({lm['target'] for lm in list_mapping})

		# read in the lists
		trello_lists = await get_board_lists(base_params, boardId)
		trello_lists = {tl.name: tl for tl in trello_lists if tl.name in list_names}
		
		# assign cards to the trello_lists
		await get_list_cards(base_params, trello_lists.values())
		# loop over and clone cards
		for obj in list_mapping:
			# compute the difference
			template_list = trello_lists[obj['origin']]
			template_card_names = {c.name for c in template_list.cards}
			target_list = trello_lists[obj['target']]
			target_card_names = {c.name for c in target_list.cards}
			done_card_names = template_card_names - target_card_names
			# set the due dates
			delta = timedelta(days=obj['interval'])
			done_cards = [c for c in template_list.cards if c.name in done_card_names]
			# create the cards, note, we don't want to use async as trello can't keep up
			for card in done_cards:
				card.due = card.format_date(datetime.now() + delta)
				await clone_card(base_params, template_list, target_list, card)


if __name__ == '__main__':
	aio.run(async_main())

