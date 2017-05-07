import os, json

ACTIVETHRESHOLD = 5

class Player:
    # Player class keeping track of all the stats calculated for each player
    def __init__(self, name, rating, league, game='Melee', ):
        self.name = str(name)
        self.rating = rating
        self.place = -1
        self.oldplace = 0 # Not sure if needed
        self.tournaments = {}
        self.matches = []
        self.game = game
        self.rank_change = ''
        self.medals = {}
        self.league = league

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
                    'win': True if match.winner == self.name else False
                }
            else:
                return {
                    'opponent': match.player1,
                    'opponent_skill_change': match.p1change,
                    'skill_change': match.p2change,
                    'win': True if match.winner == self.name else False
                }
        return {
            'name': self.name,
            'rating': self.rating.exposure,
            'matches': map(lambda m: getMatchInfo(m), self.matches),
            'wins': self.getWins(),
            'tournaments': sorted(self.tournaments.keys()),
            'game': self.game,
            'rank_change': self.rank_change,
            'medals': self.medals
        }

    def addMedal(self, medal, date, msg=''):
        if medal in self.medals.keys():
            return
        self.medals[medal] = "Achieved on " + str(date) + str(msg)

    def getTournamentMatches(self,tournament):
        # Return all of the players matches from tournament
        return filter(lambda k: k.tournament.date == tournament.date, self.matches)

    def earnMedals(self, tournament, league):
        tournaments = len(self.tournaments)
        def _addMedal(medal, msg=''):
            self.addMedal(medal, tournament.date, msg)
        if len(self.league.tournaments) == tournaments:
            _addMedal('every_tournament')
        # if len(self.league.rankedtournaments) == rankedtournaments:
        #   _addMedal('every_ranked_tournament')
        if tournaments >= 10:
            _addMedal('tournaments_10')
        if tournaments >= 50:
            _addMedal('tournaments_50')
        if tournaments >= 100:
            _addMedal('tournaments_100')
        games = len(self.matches)
        if games >= 50:
            _addMedal('games_50')
        if games >= 100:
            _addMedal('games_100')
        if games >= 1000:
            _addMedal('games_1000')
        wins = self.getWins()
        if wins >= 1:
            _addMedal('wins_1')
        if wins >= 10:
            _addMedal('wins_10')
        if wins >= 50:
            _addMedal('wins_50')
        if wins >= 100:
            _addMedal('wins_100')
        tws = 0
        t8s = 0
        for t in self.tournaments:
            tmp = filter(lambda k: k.date == t, league.tournaments.values())
            assert len(tmp) == 1
            tourney = tmp[0]
            tws += 1 if tourney.entrantsDict[self.name] == 1 else 0 # Tournament Wins
            t8s += 1 if tourney.entrantsDict[self.name] <= 8 else 0 # Top 8s
        if tws >= 1:
            _addMedal('tournament_wins_1')
        if tws >= 5:
            _addMedal('tournament_wins_5')
        if tws >= 25:
            _addMedal('tournament_wins_25')
        if tws > tournaments-tws:
            _addMedal('majority_tournament_wins')
        if t8s >= 1:
            _addMedal('t8s_1')
        if t8s >= 10:
            _addMedal('t8s_10')
        if t8s >= 25:
            _addMedal('t8s_25')
        tourney_matches = self.getTournamentMatches(tournament)
        # if tournament.entrantsDict[self.name] == 1:
        #     # Player won the tournament
        #     losses = 0
        #     for match in tourney_matches:
        #         if match.winner != self.name:
        #             losses += 1
        #     if losses == 0:
        #         _addMedal('undefeated_win')
