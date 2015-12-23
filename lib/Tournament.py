import operator

class Tournament:
    ''' Tournament object contains all information about a tournament's results '''
    def __init__(self,date):
        self.entrants = []
        self.bracket = []
        self.date = date
        self.game = None

    def setGame(self,game):
        '''Set the game to be lowercase alphanumeric characters only'''
        g = game.lower().split(" ")
        st = ""
        for i in g:
            st+=i
        self.game = st

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
        raise Exception("Error Player " + str(name) + "not in entrants list")

    def removeMatch(self,match):
       self.bracket.remove(match)

    def rankPlayers(self):
        ''' Assigns standings based on the results of the bracket '''
        gf = self.bracket[-1]
        gf.getWinner().setPlace(1)
        gf.getLoser().setPlace(2)
        gf.printResults()
        losers = []
        for m in self.bracket:
            if m.isWinners():
                continue
            else:
                losers.append(m)
        rnd = losers[-1]
        pl = 3
        cntr = 0
        for i in range(len(losers)):
            m = losers[-i-1]
            if m.isBye() or m.isNDone():
                continue
            if rnd == m.rnd:
                m.getLoser().setPlace(pl)
                cntr += 1
            else:
                pl += cntr
                cntr = 1
                rnd = m.rnd
                m.getLoser().setPlace(pl)
