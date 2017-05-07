class Match:
    ''' The Match class contains the information to do with a tournament set
        between two players '''
    def __init__(self):
        self.player1 = None;
        self.player2 = None;
        self.rnd = None;
        self.number = None;
        self.winner = None;

    def getPlayer1(self):
        return self.player1

    def getPlayer2(self):
        return self.player2

    def getRND(self):
        return self.rnd

    def isWinners(self):
        return self.rnd > 0

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

    def setRND(self,rnd):
        self.rnd = int(rnd)

    def setNumber(self,n):
        self.number = int(n)

    def getLoser(self):
        if self.player1 == self.winner:
            return self.player2
        return self.player1

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
        return False

    def isMatch(self):
        if (self.player1.getID() == '00000000-0000-0000-0000-000000000000'):
            if (self.player2.getID() == '00000000-0000-0000-0000-000000000000'):
                return False
        return True

    def printResults(self):
        print(str(self.number) + "   " + str(self.rnd))
        print("\t"+self.winner.name+" !!!!")
        print("\t"+self.getLoser().name)
        print("")
