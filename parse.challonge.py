#### TIO TO CHALLONGE ####
#### V0.03 Sam Nelson ####
#### 8 January 2015      ####
##########################

#this breaks if two people have the same name 

#ideally it would be cool to have it check for alternate names, and list everybody who hasn't done a tournament before
    #ask if changes should be made
         #need an id, so that people can still have stuff stored
             #probably want to integrate this more with playerparse, idk how databases work

                        #the other thing that has to be done before playerparse is grand finals needs to be calculated after losers finals

#so now the process for adding a tournament is
  #dl the bracket from mat
  #rename it to <date>.tio
  #run 'python tiotochallonge.py <date>.tio'
  #check for unfinished tournaments that need to be changed
  #check for when people get dq'd and need matches deleted
  #check for merging player names
  #switch grandfinals to be parsed at the end
  #move the tournaments to backuptournaments/xxx
  #run update.sh a few times
  #move the files to the right spot
  #update the pasttournaments.json file
  #reupload the data folder or something is simplest


import sys
import xml.etree.ElementTree as ET
import challonge
import random
import json

CHALLONGE_USERNAME = "thundrio"
CHALLONGE_KEY = "cIXoy4tOCZohRn7Atj0Ft7Y5SuD2iWmBXPZDjzWR"

class Match:
    def __init__(self):
        self.player1 = None;
        self.player2 = None;
        self.rnd = None;
        self.winners = True;
        self.number = None;
        self.winner = None;


    def getPlayer1(self):
        return self.player1

    def getPlayer2(self):
        return self.player2

    def getRND(self):
        return self.rnd

    def getWinners(self):
        return self.winners

    def getNumber(self):
        return self.number

    def getWinner(self):
        return self.winner

    def setWinner(self,w):
        self.winner = w

    def setP2(self,p2):
        self.player2 = p2
    
    def setP1(self,p1):
        self.player1 = p1

    def setWinners(self,w):
        self.winners = w

    def setRND(self,rnd):
        self.rnd = rnd

    def setNumber(self,n):
        self.number = n

    def isBye(self):
        if (self.player1.getID() == '00000001-0001-0001-0101-010101010101'):
            return True
        elif (self.player2.getID() == '00000001-0001-0001-0101-010101010101'):
            return True
        return False

    def isNDone(self):
        if (self.player1.getID() == '00000000-0000-0000-0000-000000000000'):
            return True
        elif (self.player2.getID() == '00000000-0000-0000-0000-000000000000'):
            return True
        return false

    def isMatch(self):
        if (self.player1.getID() == '00000000-0000-0000-0000-000000000000'):
            if (self.player2.getID() == '00000000-0000-0000-0000-000000000000'):
                return False
        return True


class Player:
    def __init__(self,name):
        self.name = name
        self.seed = None
        self.id = None
        self.cid = None;

    def getCID(self):
        return self.cid

    def setCID(self,cid):
        self.cid = cid

    def getName(self):
        return self.name

    def getSeed(self):
        return self.seed

    def getID(self):
        return self.id

    def setName(self,name):
        self.name = name

    def setSeed(self,seed):
        self.seed = seed
    
    def setId(self, ID):
    	self.id = ID

class Tournament:
    def __init__(self):
        self.entrants = []
        self.bracket = []
        self.game = None

    def setGame(self,game):
        self.game = game

    def getGame(self):
        return self.game

    def addMatch(self,match):
        self.bracket.append(match)

    def addPlayer(self,p):
        self.entrants.append(p)

    def getPlayer(self,name):
        for player in self.entrants:
            if (player.name == name):
                return player
        return "ERR NAME NOT FOUND"

    def getPlayerByCID(self,CID):
        for player in self.entrants:
            if (player.cid == CID):
                return player
        return "ERR CID NOT FOUND"

    def removeMatch(self,match):
       self.bracket.remove(match)

    def findMatch(self,match):
        ###This maybe breaks if people play each other once in winners and again in losers
        ###On the other hand the losers match wont be ready until the winners is erased
        ###I think I'm wrong but I think it will work right for the initial pitch
        for m in self.bracket:
            if (m.getPlayer1().getCID() == match.get('player1-id')):
                if (m.getPlayer2().getCID() == match.get('player2-id')):
                    return m
            if (m.getPlayer2().getCID() == match.get('player1-id')):
                if (m.getPlayer1().getCID() == match.get('player2-id')):
                    return m

    def hasPlayers(self,match):
        for m in self.bracket:
            if (m.getPlayer1().getCID() == match.get('player1-id')):
                if (m.getPlayer2().getCID() == match.get('player2-id')):
                    return True
            if (m.getPlayer2().getCID() == match.get('player1-id')):
                if (m.getPlayer1().getCID() == match.get('player2-id')):
                    return True
        return False



class TournamentReader:
    def __init__(self,filename):
        self.filename = filename
        self.file = None
        self.players = []
        self.tournaments = []
        self.date = None
        self.game = ""

    def test(self):
        print("ALL PLAYERS")
        for player in self.players:
            print(player.getName())
            print(player.getSeed())
            print(player.getID())
            print("")
        print("")
        for tournament in self.tournaments:
            print("TOURNAMENT X")
            print("")
            print(" ENTRANTS")
            for player in tournament.entrants:
                print("Name  " + str(player.getName()))
                print("Seed  " + str(player.getSeed()))
                print("ID  " + str(player.getID()))
                print("")
            print("")
            print(" MATCHES")
            for match in tournament.bracket:
                print("Number  " + str(match.getNumber()))
                print("Player1  " + str(match.getPlayer1().getName()))
                print("Player2  " + str(match.getPlayer2().getName()))
                print("Winner  " + str(match.getWinner().getName()))
                print("Winners  " + str(match.getWinners()))
                print("RND  " + str(match.getRND()))


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
    uploadTournament(bob.tournaments[0])
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
    