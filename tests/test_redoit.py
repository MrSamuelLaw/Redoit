import unittest
import redoit as tb
from models import TrelloBoard, TrelloList, TrelloCard, Credentials



class TestToolbox(unittest.IsolatedAsyncioTestCase):

    def test_generate_mappings(self):
        # setup the board
        board = TrelloBoard(id='123', name='Chores')
        target = TrelloList(id='456', name='target')
        source = TrelloList(id='789', name='source {"interval": 7, "target": "target"}')
        board.lists.extend((target, source))

        # generate the mappings
        credentials = Credentials(key='key', token='token', usernames=['s.law'])
        mappings = tb.parse_mappings(credentials, board)
        lm = mappings[0]
        self.assertEqual(lm.source.id, source.id)
        self.assertEqual(lm.target.id, target.id)
        self.assertEqual(lm.interval, 7)


if __name__ == '__main__':
    unittest.main(verbosity=2)