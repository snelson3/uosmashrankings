class Match:
    # Class to keep track of information for each match in a tournament
    def __init__(self,m, tournament):
        # Makes more sense to record as winner, loser
        # Also encode whether it's winners into the round
        self.player1 = str(m['Player1'])
        self.player2 = str(m['Player2'])
        self.winner = str(m['winner'])
        self.round = str(m['rnd'])
        self.matchnum = str(m['number'])
        self.tournament = tournament
        self.p1change = 0
        self.p2change = 0
        self.date = tournament.date

    def isBye(self):
        if self.player1 == 'BYE' or self.player2 == 'BYE':
            return True
        return False

    def getResults(self,p1,p2):
        # return winner, loser
        assert self.winner in [p1.name, p2.name]
        if self.winner == p1.name:
            return p1, p2
        return p2, p1

    def setChange(self, winner, loser):
        # Records the change in skill for each player
        if self.player1 == self.winner:
            self.p1change = winner
            self.p2change = loser
        else:
            self.p2change = winner
            self.p1change = loser

    def toDict(self):
        return {
            'player1': self.player1,
            'player2': self.player2,
            'winner': self.winner,
            'rnd': self.round,
            'number': self.matchnum,
            'p1_skill_change': self.p1change,
            'p2_skill_change': self.p2change
        }