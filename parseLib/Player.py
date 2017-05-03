import os, json

ACTIVETHRESHOLD = 5

class Player:
    # Player class keeping track of all the stats calculated for each player
    def __init__(self, name, rating, game='Melee'):
        self.name = str(name)
        self.rating = rating
        self.place = -1
        self.oldplace = 0 # Not sure if needed
        self.tournaments = {}
        self.matches = []
        self.game = game
        self.rank_change = ''

    def checkActive(self, tournaments):
        # Returns True if player has been to last ACTIVETHRESHOLD tournaments
        if not filter(lambda k: k in self.tournaments.values(), tournaments.values()[::-1][:ACTIVETHRESHOLD]):
            self.place = -1

    def getWins(self):
        # Returns the number of wins the player has had
        return len(filter(lambda m: m.winner == self.name, self.matches))

    def addTournamentMatch(self, m, newrating):
        self.tournaments[m.tournament.date] = m.tournament
        self.matches.append(m)
        self.setRating(newrating)

    def setRating(self, nr):
        self.rating = nr

    def writeRank(self):
        with open(os.path.join("players",self.game,self.game+"-"+self.name+".json"), "w") as f:
            json.dump(self.toDict(), f, indent=4)

    def getSummary(self):
        return {
            'name': self.game+'-'+self.name,
            'num_tourneys': len(self.tournaments),
            'ELO': self.rating.exposure,
            'GAME': self.game
        }

    def toDict(self):
        # Returns a dictionary containing all of the player's relevent stats
        def getMatchInfo(match):
            m = dict()
            if match.player1 == self.name:
                return {
                    'opponent': match.player2,
                    'opponent_skill_change': match.p2change,
                    'skill_change': match.p1change,
                    'win': True if match.winner is self.name else False
                }
            else:
                return {
                    'opponent': match.player1,
                    'opponent_skill_change': match.p1change,
                    'skill_change': match.p2change,
                    'win': True if match.winner is self.name else False
                }
        return {
            'name': self.name,
            'rating': self.rating.exposure,
            'matches': map(lambda m: getMatchInfo(m), self.matches),
            'wins': self.getWins(),
            'tournaments': sorted(self.tournaments.keys()),
            'game': self.game,
            'rank_change': self.rank_change
        }

