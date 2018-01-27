import responses
import unittest 
from unittest.mock import patch
from services import Database

class TestDatabase(unittest.TestCase):
    
    @classmethod
    @patch('firebase')
    def setUp(cls, firebase):
        cls.db = Database(firebase)

    @responses.activate
    def test_get(self):
        self.db

