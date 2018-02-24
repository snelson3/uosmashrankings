#### CHALLONGE Parse ####
#### Sam Nelson ####
#### 4 January 2016  ####
##########################

import sys
import challonge
import random
import json, os, shutil
from uorank.lib.Match import Match
from uorank.lib.Tournament import Tournament
from uorank.lib.Player import Player
from uorank.lib.TournamentWriter import TournamentWriter

class TournamentReader:
    def __init__(self, tid, game='melee'):
        if tid == None:
            raise Exception("Must provide a tournament Name")
        self.id = tid
        self.file = None
        self.players = []
        self.tournaments = []
        self.date = None
        self.game = game

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
        '''split date on T and return first part formatted YYYY/MM/DD'''
        d = date.date().isoformat().split('-')
        return d[0]+"/"+d[1]+"/"+d[2]

    def getDate(self):
        '''
        return date in yyyymmdd format
        '''
        d = self.date.split('/')
        return d[0]+d[1]+d[2]

    def read(self):
        '''Read the results of a Challonge bracket into a Tournament object '''
        print("reading")
        tournament = challonge.tournaments.show(self.id)
        self.date  = self.parseDate(tournament["started-at"])
        participants = challonge.participants.index(self.id)
        t = Tournament(self.date)
        t.setGame(self.game)
        for entrant in participants:
            p = Player(entrant['display-name'])
            p.setId(entrant['id'])
            t.addPlayer(p)
            self.players.append(p)
        matches = challonge.matches.index(self.id)
        i = 1
        for match in matches:
            m = Match()
            m.setP1(self.getPlayer(match['player1-id']))
            m.setP2(self.getPlayer(match['player2-id']))
            winner = match['winner-id'];
            if winner == None:
                raise Exception(
                    "Match of {}-{} has no winner".format(m.getPlayer1().name,m.getPlayer2().name)
                )
            m.setWinner(self.getPlayer(match['winner-id']))
            m.setRND(match['round'])
            m.setNumber(i)
            t.bracket.append(m)
        self.tournaments.append(t)

def cleanDir(game):
    rank_folder = os.path.join("ranking-data", "{}-files".format(game))
    paths_to_delete = ["players", "raw", "updated", "aliasmap.json", "playerlist.json", "tournamentlist.json"]
    if os.path.exists(rank_folder):
        for p in paths_to_delete:
            fn = os.path.join(rank_folder,p)
            if os.path.exists(fn):
                if os.path.isdir(fn):
                    shutil.rmtree(fn)
                    os.mkdir(fn)
                else:
                    os.remove(fn)


def main():
    assert os.path.isfile('/challongekey')
    with open('/challongekey') as f:
        CN, CK = f.read().split()
    challonge.set_credentials(CN, CK)
    assert len(sys.argv) > 1
    bracket_ids = []
    if os.path.isfile(sys.argv[1]):
        print "reading bracketcodes"
        # Pointing to a list of bracketcodes
        with open(sys.argv[1]) as f:
            for line in f:
                bracket_ids.append(line.strip())
    else:
            bracket_ids.append(sys.argv[1])
    if sys.argv[3] == '-d':
        print '-d'
        cleanDir(sys.argv[2])
    for id in bracket_ids:
        print id
        reader = TournamentReader(id, sys.argv[2])
        writer = TournamentWriter()
        reader.read()

        for tournament in reader.tournaments:
            tournament.rankPlayers()
            writer.storeTournament(tournament,reader.getDate())

main()

# Usage (NOTE: if under a subdomain like uosmash.challonge... use subdomain-bracketcode)
# python parse.challonge.py bracketcode game
# or
# python parse.challonge.py bracketlinks.dat game
# add -d to the end to empty the ranking-data folder first