#### TIO Parse ####
#### Sam Nelson ####
#### 15 December 2015 ####
##########################

# This will parse a bracket from tio
# After reading, the parsed brackets are Tournament objects
#   stored in the TournamentReader.tournaments list
# I should probably make these all work together, means breaking like
# Match into it's own file, just cleaner and stuff

#this breaks if two people have the same name
 #If tio allows people with the same name different capitalizations...
#Change where Grand finals are to be after losers Finals in the list

#add error checking and comments where appropriate

import sys
import xml.etree.ElementTree as ET
import operator
import random
import json
from lib.Match import Match
from lib.Tournament import Tournament
from lib.Player import Player
from lib.TournamentWriter import TournamentWriter

class TournamentReader:
    def __init__(self,filename):
        self.filename = filename
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

    def read(self):
        tree = ET.parse(self.filename)
        root = tree.getroot()

        for item in root.iter('Event'):
            self.date = item.find('StartDate').text

        for player in root.iter('Player'):
            p = Player(player.find('Nickname').text)
            p.setId(player.find('ID').text)
            self.players.append(p)
        for tournament in root.iter('Game'):
            t = Tournament(self.date)
            t.game = parseGame(tournament.find('Name').text)
            for entrant in tournament.iter('Entrant'):
                p = self.getPlayer(entrant.find('PlayerID').text)
                t.addPlayer(p)
            for match in tournament.iter('Match'):
                m = Match()
                if (match.find('IsChampionship').text == "True"):
                    if (match.find('IsSecondChampionship').text == "True"):
                        m.setNumber(int(match.find('Number').text)*2+1)
                    else:
                        m.setNumber(int(match.find('Number').text)*2)
                else:
                    m.setNumber(int(match.find('Number').text))
                m.setP1(self.getPlayer(match.find('Player1').text))
                m.setP2(self.getPlayer(match.find('Player2').text))
                m.setWinner(self.getPlayer(match.find('Winner').text))
                m.setWinners(match.find('IsWinners').text)
                m.setRND(match.find('Round').text)
                if(m.isMatch()):
                    t.bracket.append(m)
            t.bracket.sort(key=operator.attrgetter('number'));
            self.tournaments.append(t)

def main():
    reader = TournamentReader(sys.argv[1])
    writer = TournamentWriter()
    reader.read()

    #this means make sure the filename is right
    for tournament in reader.tournaments:
        writer.storeTournament(tournament,sys.argv[1])


def parseGame(st):
    #this is bad but it returns melee if the game starts with an m and a pm if it starts with a p
    if st[0] == "M":
        return "melee"
    elif st[0] == "P":
        return "pm"
    else:
        raise Exception("Event names must start with either Melee or Project")

main()
