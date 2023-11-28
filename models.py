from typing import List
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class TrelloCard(BaseModel):
	"""Class that represents a card model card on a trello list.

	Note, that the fields on this model are not exaustive.
	the model ignores extra fields.
	"""

	model_config = ConfigDict(extra='allow')

	due: str | None = None
	id: str
	name: str

	@classmethod
	def format_date(cls, dt: datetime) -> str:
		format = r'%Y-%m-%dT%H:%M:%SZ'
		date_str = dt.strftime(format)
		return date_str


class TrelloList(BaseModel):
	"""Class that represents a list model from a trello board.

	Note, that the fields on this model are not exaustive.
	the model ignores extra fields.
	"""

	id: str
	name: str
	cards: List[TrelloCard] = None




