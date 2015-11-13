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
