#### CHALLONGE Parse ####
#### Sam Nelson ####
#### 4 January 2016  ####
##########################

import sys
import challonge
import random
import json
from lib.Match import Match
from lib.Tournament import Tournament
from lib.Player import Player
from lib.TournamentWriter import TournamentWriter

CHALLONGE_USERNAME = "thundrio"
CHALLONGE_KEY = "cIXoy4tOCZohRn7Atj0Ft7Y5SuD2iWmBXPZDjzWR"

class TournamentReader:
    def __init__(self,tid):
        if tid == None:
            raise Exception("Must provide a tournament Name")
        self.id = tid
        self.file = None
        self.players = []
        self.tournaments = []
        self.date = None
        self.game = ""

    def getPlayer(self,ID):
        if (ID == '00000001-0001-0001-0101-010101010101'):
            return Player('BYE')
        if (ID == '00000000-0000-0000-0000-000000000000'):
            return Player('NDONE')
        for player in self.players:
            if (player.id == ID):
                return player
        raise Exception("ID Not Found "+ str(ID))

    def parseDate(self,date):
        '''YYYY-MM-DDT16:57:17-05:00'''
        '''split date on T and return first part formatted MM/DD/YYYY'''
        d = date.split('T')[0].split('-')
        return d[1]+"/"+d[2]+"/"+d[0]

    def getDate(self):
        '''return date in yyyymmdd format'''
        d = self.date.split('/')
        return d[0]+d[1]+d[2]

    def read(self):
        '''Read the results of a Challonge bracket into a Tournament object '''
        print("reading")
        tournament = challonge.tournaments.show(self.id)
        self.date  = self.parseDate(tournament["started-at"])
        participants = challonge.participants.index(self.id)
        t = Tournament(self.date)
        t.setGame(tournament['game-name'])
        for entrant in participants:
            p = Player(entrant['display-name'])
            p.setId(entrant['id'])
            t.addPlayer(p)
            self.players.append(p)
        matches = challonge.matches.index(self.id)
        i = 1;
        for match in matches:
            m = Match()
            m.setP1(self.getPlayer(match['player1-id']))
            m.setP2(self.getPlayer(match['player2-id']))
            m.setWinner(self.getPlayer(match['winner-id']))
            m.setRND(match['round'])
            m.setNumber(i)
            t.bracket.append(m)
        self.tournaments.append(t)

def main():
    challonge.set_credentials(CHALLONGE_USERNAME,CHALLONGE_KEY)
    reader = TournamentReader(sys.argv[1])
    writer = TournamentWriter()
    reader.read()

    for tournament in reader.tournaments:
        tournament.rankPlayers()
        writer.storeTournament(tournament,reader.getDate())


main()
