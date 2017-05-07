from uorank.lib.Tournament import Tournament
from unittest import TestCase

class mockTournament():
    def __init__(self):
        self.t = Tournament('1/1/1970')

    def addEntrants(self):

class TestTournament(TestCase):
    def mockTournament(self):
        return Tournament('1/1/1970')

    def test_getGame(self):
        t = self.mockTournament()
        t.game = 'testgame'
        assert t.getGame() == 'testgame'

    def test_setGame(self):
        t = self.mockTournament()
        t.setGame('testgame')
        assert t.game == 'testgame', t.game
        t.setGame('Test Game')
        assert t.game == 'testgame', t.game
        t.setGame('Test&Game')
        assert t.game == 'testgame', t.game
        t.setGame('')
        assert t.game == '', t.game

    def test_rankPlayers(self):
        entrants = range(24)