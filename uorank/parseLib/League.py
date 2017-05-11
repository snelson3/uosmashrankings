import os, json
from Player import Player
from Tournament import Tournament

class League:
    def __init__(self, env, game='Melee'):
        self.env = env
        self.game = game
        self.tournaments = {}
        self.players = {} # Player name is the key

    def getPlayerNames(self):
        return self.players.keys()

    def getPlayers(self):
        return self.players.values()

    def loadTournaments(self, dir='.'):
        # They need to be loaded in order but testing right now
        for fn in os.listdir(os.path.join(dir,"tournaments",self.game)):
            self.tournaments[fn] = Tournament(os.path.join("tournaments",self.game,fn))

    def getPlayer(self, name):
        try:
            return self.players[name.replace(" ", "").lower()]
        except KeyError:
            for p in self.getPlayers():
                if name in p.getAliases():
                    return p
        return -1

    def addPlayer(self,name):
        self.players[name.replace(" ","").lower()] = Player(name,self)

    def addName(self, name):
        if self.getPlayer(name) == -1:
            self.addPlayer(name)
        else:
            self.getPlayer(name).addAlias(name)
        return self.getPlayer(name)

    def loadPlayers(self):
        if os.path.isfile("aliases.txt"):
            with open("aliases.txt") as f:
                # name, alias1, alias2, alias3
                for line in f:
                    line = line.strip().split(',')
                    name = line[0]
                    aliases = line[1:]
                    player = self.addName(name)
                    for n in aliases:
                        player.addAlias(n)
        for t in self.tournaments.values():
            for e in t.entrants:
                self.addName(e['name'])

    def scoreTournament(self, t):
        print "DATE " + str(t.date)
        for match in t.matches:
            if match.isBye():
                continue
            self.scoreMatch(match)
        self.updatePlacings()
        self.updateRanks(t.entrants, t)
        t.writeUpdatedTournament()

    def scoreMatch(self, m):
        # it would be nice if the match had a link t
        if m.isBye():
            return # Not sure what this is for
        p1 = self.getPlayer(m.player1)
        p2 = self.getPlayer(m.player2)
        p1.medalsProgress['oldrating'] = p1.getRating()
        p2.medalsProgress['oldrating'] = p2.getRating()
        winner, loser = m.getResults(self.getPlayer(m.player1), self.getPlayer(m.player2))
        winner_newrat, loser_newrat = self.env.rate_1vs1( winner.rating, loser.rating)
        m.setChange(winner_newrat.exposure - winner.rating.exposure, loser_newrat.exposure - loser.rating.exposure)
        winner.addTournamentMatch(m, winner_newrat)
        loser.addTournamentMatch(m, loser_newrat)

    def updatePlacings(self):
        for player in self.getPlayers():
            player.temprating = player.rating.exposure
        newlist = sorted(self.getPlayers(), key=lambda x: x.temprating, reverse=True)
        for e in self.getPlayers():
            if len(e.tournaments) < 2 or not e.checkActive(self.tournaments) or e.name == 'BYE':
                e.place = -1
                newlist.remove(e) # what is this for
        for i in range(len(newlist)):
            newlist[i].place = i+1
        # Not sure if this method is doing anything

    def getRankDict(self):
        player_ranks = {}
        sorted_ranks = sorted(self.getPlayers(), key=lambda k: k.getRating())
        for r in range(len(sorted_ranks)):
            player_ranks[sorted_ranks[r]] = r+1
        return player_ranks

    def updateRanks(self, entrants, tournament):
        for p in entrants:
            player = self.getPlayer(p['name'])
            if (player.oldplace == -1) and (player.place != -1):
                p['rank_change'] = 'Ranked!'
            else:
                p['rank_change'] = player.oldplace-player.place
            player.oldplace = player.place
            player.earnMedals(tournament)

    def writeRankings(self):
        playerlist = []
        for player in self.getPlayers():
            player.addFinalMedals()
            if player.name == 'BYE':
                continue
            player.checkActive(self.tournaments) # ...
            player.writeRank()
            playerlist.append(player.getSummary())
            with open(os.path.join("players",self.game+"-playerlist.json"),"w") as f:
                json.dump(playerlist, f, indent=4)
            # Pretty sure I also need to generate a tournament list