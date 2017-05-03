import os, json
from Player import Player
from Tournament import Tournament

class League:
    def __init__(self, env, game='Melee'):
        self.env = env
        self.game = game
        self.tournaments = {}
        self.players = {} # Player name is the key

    def loadTournaments(self, dir='.'):
        # They need to be loaded in order but testing right now
        for fn in os.listdir(os.path.join(dir,"tournaments",self.game)):
            self.tournaments[fn] = Tournament(os.path.join("tournaments",self.game,fn))


    def loadPlayers(self):
        for t in self.tournaments.values():
            for e in t.entrants:
                self.players[e['name']] = Player(e['name'], self.env.Rating(), self)

    def scoreTournament(self, t):
        print "DATE " + str(t.date)
        for match in t.matches:
            if match.isBye():
                continue
            self.scoreMatch(match)
        self.updatePlacings()
        self.updateRanks(t.entrants, t)
        t.writeUpdatedTournament()

    def getPlayer(self, name):
        assert name in self.players.keys()
        return self.players[name]

    def scoreMatch(self, m):
        # it would be nice if the match had a link t
        if m.isBye():
            return # Not sure what this is for
        winner, loser = self.getPlayer(m.player1), self.getPlayer(m.player2)
        winner_newrat, loser_newrat = self.env.rate_1vs1( winner.rating, loser.rating)
        m.setChange(winner_newrat.exposure - winner.rating.exposure, loser_newrat.exposure - loser.rating.exposure)
        winner.addTournamentMatch(m, winner_newrat)
        loser.addTournamentMatch(m, loser_newrat)

    def updatePlacings(self):
        for player in self.players.values():
            player.temprating = player.rating.exposure
        newlist = sorted(self.players.values(), key=lambda x: x.temprating, reverse=True)
        for e in self.players.values():
            if len(e.tournaments) < 2 or not e.checkActive(self.tournaments) or e.name == 'BYE':
                e.place = -1
                newlist.remove(e) # what is this for
        for i in range(len(newlist)):
            newlist[i].place = i+1
        # Not sure if this method is relevant

    def updateRanks(self, entrants, tournament):
        for p in entrants:
            player = self.players[p['name']]
            if (player.oldplace == -1) and (player.place != -1):
                p['rank_change'] = 'Ranked!'
            else:
                p['rank_change'] = player.oldplace-player.place
            player.oldplace = player.place
            player.earnMedals(tournament)

    def writeRankings(self):
        playerlist = []
        for player in self.players.values():
            if player.name == 'BYE':
                continue
            player.checkActive(self.tournaments)
            player.writeRank()
            playerlist.append(player.getSummary())
            with open(os.path.join("players",self.game+"-playerlist.json"),"w") as f:
                json.dump(playerlist, f, indent=4)
            # Pretty sure I also need to generate a tournament list