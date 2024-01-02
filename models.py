from typing import List, Tuple, Self
from datetime import datetime
from pydantic import BaseModel, ConfigDict


class Credentials(BaseModel):
    key: str
    token: str
    usernames: Tuple[str, ...]


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

    def __eq__(self, card: Self) -> bool:
        return self.id == card.id


class TrelloList(BaseModel):
    """Class that represents a list model from a trello board.

    Note, that the fields on this model are not exaustive.
    the model ignores extra fields.
    """

    id: str
    name: str
    cards: List[TrelloCard] = []

    def __eq__(self, list_: Self) -> bool:
        return self.id == list_.id


class TrelloBoard(BaseModel):
    id: str
    name: str
    lists: List[TrelloList] = []

    def __eq__(self, board: Self) -> bool:
        return self.id == board.id


class ListMapping(BaseModel):
    source: TrelloList
    target: TrelloList
    interval: int  # days