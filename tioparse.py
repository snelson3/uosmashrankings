#### TIO Parse ####
#### Sam Nelson ####
#### 17 July 2015 ####
##########################

#This will parse a bracket from tio and return a Tournament class
# I should probably make these all work together, means breaking like 
# Match into it's own file, just cleaner and stuff

#this breaks if two people have the same name 

#ideally it would be cool to have it check for alternate names, and list everybody who hasn't done a tournament before
    #ask if changes should be made
         #need an id, so that people can still have stuff stored
             #probably want to integrate this more with playerparse, idk how databases work
                        #the other thing that has to be done before playerparse is grand finals needs to be calculated after losers finals

import sys
import xml.etree.ElementTree as ET
import challonge
import random
import json
from lib.Match import Match 
from lib.Tournament import Tournament 
from lib.Player import Player

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
        
        #This is cheating
        for item in root.iter('Event'):
            self.date = item.find('StartDate').text
        #self.date = root.iter('Event')[0].find('StartDate').text
        
        for player in root.iter('Player'):
            #print("player")
            #print(player.find('Nickname').text)
            #print(player.find('ID').text)

            #this is where you would do the logic to check for the proper player name
            p = Player(player.find('Nickname').text)
            p.setId(player.find('ID').text)
            self.players.append(p)
        for tournament in root.iter('Game'):
            t = Tournament()
            t.game = parseGame(tournament.find('Name').text)
            for entrant in tournament.iter('Entrant'):
                p = self.getPlayer(entrant.find('PlayerID').text)
                p.setSeed(entrant.find('Seed').text)
                t.addPlayer(p)
            for match in tournament.iter('Match'):
                m = Match()
                if (match.find('IsChampionship').text == True):
                    if (match.find('IsSecondChampionship').text == True):
                        m.setNumber(str(int(match.find('Number').text)*2+1))
                    else:
                        m.setNumber(str(int(match.find('Number').text)*2))
                else:        
                    m.setNumber(match.find('Number').text)

                print("Match Number")
                print(match.find('Number').text)
                m.setP1(self.getPlayer(match.find('Player1').text))
                m.setP2(self.getPlayer(match.find('Player2').text))
                m.setWinner(self.getPlayer(match.find('Winner').text))
                m.setWinners(match.find('IsWinners').text)
                m.setRND(match.find('Round').text)
                if(m.isMatch()):
                    t.bracket.append(m)
            self.tournaments.append(t)

    def storeTournament(self,tournament,fn):
        #The following data should be stored
        #Final Standings
        #each match
        #date
        #game
        jsn = {
        };

        fn = fn.split('.')[0]

        out = open(fn+tournament.game+".json", "w")

        players = []
        matches = []

        for player in tournament.entrants:
            players.append(player.name)

        self.player1 = None;
        self.player2 = None;
        self.rnd = None;
        self.winners = True;
        self.number = None;
        self.winner = None;

        for match in tournament.bracket:
            m = {}
            m['Player1'] = match.player1.name
            m['Player2'] = match.player2.name
            m['rnd'] = match.rnd
            m['winners'] = match.winners
            m['number'] = match.number
            m['winner'] = match.winner.name
            matches.append(m)


        jsn['Date'] = self.date
        jsn['Entrants'] = players
        jsn['Game'] = tournament.game
        jsn['Matches'] = matches

        json.dump(jsn,out,indent=4)
        out.close()



def uploadTournament(parsed_tournament):
    challonge.set_credentials(CHALLONGE_USERNAME,CHALLONGE_KEY)
    ID = random.randint(1,146783226)
    tournament = challonge.tournaments.create("TEST3", ID, tournament_type="double elimination", description="test Tournament",
        show_rounds=True, private=True )#may want to add sequential_pairings=True but that creates issues with BYES
    for player in parsed_tournament.entrants:
        print(player.id)
        challonge.participants.create(ID,player.getName())
    for player in challonge.participants.index(ID):
        p = parsed_tournament.getPlayer(player.get('name'))
        p.setCID(player.get('id')) 
        challonge.participants.update(ID,p.getCID(), seed=max(1,int(p.getSeed())+1))#tio starts seeds at 0 challonge starts at 1
    #for player in challonge.participants.index(ID):
        #debug info
    #    print(player.get('seed'))
    challonge.tournaments.start(ID)
    for match in parsed_tournament.bracket:
        if (match.isBye()):
            parsed_tournament.removeMatch(match)
    while (len(parsed_tournament.bracket) > 0):
        for match in challonge.matches.index(ID):
            if (parsed_tournament.hasPlayers(match)):
                m = parsed_tournament.findMatch(match)
                print("PLAYER1",m.getPlayer1().getCID(),"CHALLONGEP1",match.get('player1-id'))
                print("PLAYER2",m.getPlayer2().getCID(),"CHALLONGEP2",match.get('player2-id'))
                print("WINNER",m.getWinner().getCID())
                print(match)
                #I think its an issue with when the HTTP requests happen, its not updating the most recent match?
                #all I can think of atm, I think this has to be the issue
                ###FIX THIS ISSUE WHERE LB MAtCHES WONT UPDATE
                #try:
                #   challonge.matches.update(ID,match.get('id'),scores_csv="1-0",winner_id=m.getWinner().getCID())
                #except:
                challonge.matches.update(ID,match.get('id'),scores_csv="1-0",winner_id=match.get('player2-id'))
                parsed_tournament.removeMatch(m)
        print("BRACKET LEN", len(parsed_tournament.bracket))


    # for match in challonge.matches.index(ID):
    #    print("ID",match.get('id'))
    #    print("WinnerID",match.get('winner-id'))
    #    print("STATE",match.get('state'))
    #    try:
    #        print("P1-ID",match.get('player1-id'),parsed_tournament.getPlayerByCID(match.get('player1-id')).getName())
    #    except:
    #        print("P1-ID","NONE")
    #    print("LoserID",match.get('loser-id'))
    #    try:
    #        print("P2-ID",match.get('player2-id'),parsed_tournament.getPlayerByCID(match.get('player2-id')).getName())
    #    except:
    #        print("P2-ID","NONE")
    #    print("RND",match.get('round'))'''

def main():
    print("hi")
    bob = TournamentReader(sys.argv[1])
    bob.read()
    bob.test()
    #this means make sure the filename is right
    for tournament in bob.tournaments:
        bob.storeTournament(tournament,sys.argv[1])
    #uploadTournament(bob.tournaments[0])
    #bob.storeTournament(sys.argv[1])
    #uploadTournament(bob.tournaments[0])

    #challonge.tournaments.destroy(ID)

def parseGame(st):
    #this is bad but it returns melee if the game starts with an m and a pm if it starts with a p
    if st[0] == "M":
        return "melee"
    elif st[0] == "P":
        return "pm"
    else:
        raise Exception("Event names must start with either Melee or Project")

main()
    
