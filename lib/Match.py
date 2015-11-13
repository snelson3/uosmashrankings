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

