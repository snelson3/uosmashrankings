import os, json, shutil
from Player import Player
from Tournament import Tournament


CLEANUP = True

class League:
    def __init__(self, env, game='melee'):
        self.env = env
        self.game = game
        assert os.path.isdir('ranking-data') and os.path.isdir(os.path.join('ranking-data',game+'-files')), 'no rankings to read from!'
        self.gamepath = os.path.join('ranking-data',game + '-files')

        if CLEANUP:
            # Clean up old files, but leave the raw tournaments folder
            if os.path.exists(os.path.join(self.gamepath,'updated')):
                shutil.rmtree(os.path.join(self.gamepath,'updated'))
            if os.path.exists(os.path.join(self.gamepath,'players')):
                shutil.rmtree(os.path.join(self.gamepath,'players'))
            if os.path.exists(os.path.join(self.gamepath,'playerlist.json')):
                os.remove(os.path.join(self.gamepath,'playerlist.json'))
            if os.path.exists(os.path.join(self.gamepath,'tournamentlist.json')):
                os.remove(os.path.join(self.gamepath,'tournamentlist.json'))
            if os.path.exists(os.path.join(self.gamepath,'aliasmap.json')):
                os.remove(os.path.join(self.gamepath,'aliasmap.json'))

        os.mkdir(os.path.join(self.gamepath,'updated'))
        os.mkdir(os.path.join(self.gamepath,'players'))
        self.tournaments = {}
        self.players = {} # Player name is the key

    def getPlayerNames(self):
        return self.players.keys()

    def getPlayers(self):
        return self.players.values()

    def loadTournaments(self, dir='.'):
        # They need to be loaded in order but testing right now
        for fn in os.listdir(os.path.join(dir,self.gamepath,"raw")):
            if ".uotn" not in fn:
                print "ignoring " + fn
                continue
            self.tournaments[fn] = Tournament(fn,self)

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
        if os.path.isfile(os.path.join(self.gamepath,"aliases.txt")):
            with open(os.path.join(self.gamepath,"aliases.txt")) as f:
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
        self.penalizeMissingPlayers(t)

    def penalizeMissingPlayers(self,t):
        for player in self.getPlayers():
            if player.name not in t.getEntrantsDict():
                if player.name=='thundrio':
                    print player.name
                player.rating = self.env.Rating(mu=player.rating.mu, sigma=player.rating.sigma)


    def scoreMatch(self, m):
        # it would be nice if the match had a link somewhere
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
            if not e.isRanked():
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
        # Why am I taking two things?
        for p in entrants:
            player = self.getPlayer(p['name'])
            if (player.oldplace == -1) and (player.place != -1):
                p['rank_change'] = 'Ranked!'
            elif not player.isRanked():
                p['rank_change'] = 'Unranked'
            else:
                change = 0
                for match in tournament.matches:
                    if p['name'] == match.player1:
                        change += match.p1change
                    elif p['name'] == match.player2:
                        change += match.p2change
                p['rank_change'] = change
            player.oldplace = player.place
            player.earnMedals(tournament)

    def getTournaments(self):
        return self.tournaments.values()

    def writeRankings(self):
        playerlist = []
        aliasMap = {}
        for player in self.getPlayers():
            player.addFinalMedals()
            if player.name == 'BYE':
                continue
            if not player.isRanked():
                player.place = -1
            if len(player.tournaments) == 0:
                continue
            player.writeRank()
            if player.isRanked():
                playerlist.append(player.getSummary())
            aliasMap[player.name] = player.getAliases()
        with open(os.path.join(self.gamepath,"playerlist.json"),"w") as f:
            json.dump(playerlist, f, indent=4)
        with open(os.path.join(self.gamepath,"aliasmap.json"), "w") as f:
            json.dump(aliasMap, f, indent=4)
        tournamentlist = []
        for tournament in self.getTournaments():
            tournamentlist.append({
                "date": tournament.date,
                "entrants": len(tournament.getEntrants()),
                "winner": tournament.getWinner()
            })
        with open(os.path.join(self.gamepath,"tournamentlist.json"), "w") as f:
            json.dump(tournamentlist, f, indent=4)