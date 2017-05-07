#### TIO Parse ####
#### Sam Nelson ####
#### 19 December 2015 ####
##########################

import sys
import xml.etree.ElementTree as ET
import operator
import json
from uorank.lib.Match import Match
from uorank.lib.Tournament import Tournament
from uorank.lib.Player import Player
from uorank.lib.TournamentWriter import TournamentWriter

class TournamentReader:
    def __init__(self,filename):
        if filename == None:
            raise Exception("Must provide a filename to a TIO file")
        self.filename = filename
        self.file = None
        self.players = []
        self.tournaments = []
        self.date = None
        self.game = ""

    def getPlayer(self,ID):
        ''' Return the Player associated with the given ID '''
        if (ID == '00000001-0001-0001-0101-010101010101'):
            return Player('BYE')
        if (ID == '00000000-0000-0000-0000-000000000000'):
            return Player('NDONE')
        for player in self.players:
            if (player.id == ID):
                return player
        raise Exception("ID " + str(ID) + " Does not match a player")

    def read(self):
        ''' Read a TIO file into a Tournament object '''
        tree = ET.parse(self.filename)
        root = tree.getroot()

        for item in root.iter('Event'):
            self.date = item.find('StartDate').text
        for player in root.iter('Player'):
            name = player.find('Name').text.strip()
            if name == "":
                name = player.find('Nickname').text
            p = Player(name)
            p.setId(player.find('ID').text)
            self.players.append(p)
        for tournament in root.iter('Game'):
            t = Tournament(self.date)
            t.setGame(str(tournament.find('Name').text))
            for entrant in tournament.iter('Entrant'):
                p = self.getPlayer(entrant.find('PlayerID').text)
                t.addPlayer(p)
            for match in tournament.iter('Match'):
                m = Match()
                ''' TIO stores the GF Set 1 at the end of Winners,
                    This needs to be moved to be the second to last match '''
                if (match.find('IsChampionship').text == "True"):
                    if (match.find('IsSecondChampionship').text == "True"):
                        m.setNumber(match.find('Number').text*2+1)
                    else:
                        m.setNumber(match.find('Number').text*2)
                else:
                    m.setNumber(match.find('Number').text)
                m.setP1(self.getPlayer(match.find('Player1').text))
                m.setP2(self.getPlayer(match.find('Player2').text))
                m.setWinner(self.getPlayer(match.find('Winner').text))
                m.setRND(match.find('Round').text)
                if(m.isMatch()):
                    t.bracket.append(m)
            t.bracket.sort(key=operator.attrgetter('number'));
            ''' Swap the position of the GF sets '''
            set1 = t.bracket.pop()
            set2 = t.bracket.pop()
            set1.setNumber(set2.number)
            set2.setNumber(set2.number+1)
            t.bracket.append(set1)
            t.bracket.append(set2)
            self.tournaments.append(t)

def main():
    reader = TournamentReader(sys.argv[1])
    writer = TournamentWriter()
    reader.read()

    for tournament in reader.tournaments:
        tournament.rankPlayers()
        writer.storeTournament(tournament,sys.argv[1])

main()
