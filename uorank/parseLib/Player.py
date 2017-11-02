import os, json
from collections import defaultdict

ACTIVETHRESHOLD = 5

class Player:
    # Player class keeping track of all the stats calculated for each player
    def __init__(self, name, league, game='Melee', ):
        self.name = name.replace(" ", "").lower()
        self.aliases = [name]
        self.rating = league.env.Rating()
        self.place = -1
        self.oldplace = 0 # Not sure if needed
        self.tournaments = {}
        self.matches = []
        self.game = game
        self.rank_change = ''
        self.medals = {}
        self.league = league
        self.medalsProgress = {
            'old_rating': 0,
            'better_beats': 0,
            'better_losses': 0,
            'better_beats_overall': 0,
            'better_losses_overall': 0
        }

    def translateMedal(self,name,short):
        medals = {
            "games_50": {
                "desc": 'Play 50 games.',
                "seq": "020",
                "title": 'Veteran I'
            },
            "games_100": {
                "desc": 'Play 100 games',
                "seq": "030",
                "title": 'Veteran II'
            },
            "games_1000": {
                "desc": 'Play 1000 games',
                "seq": "040",
                "title": 'Veteran III'
            },
            "tournaments_10": {
                "desc": 'Play in 10 tournaments',
                "seq": "050",
                "title": 'Grinder I'
            },
            "tournaments_50": {
                "desc": 'Play in 50 tournaments',
                "seq": "060",
                "title": 'Grinder II'
            },
            "tournaments_100": {
                "desc": 'Play in 100 tournaments',
                "seq": "070",
                "title": 'Grinder III'
            },
            "every_tournament": {
                "desc": 'Enter every tournament',
                "seq": "080",
                "title": 'Dedicated Tournamentgoer'
            },
            "wins_1": {
                "desc": 'Win 1 game',
                "seq": "100",
                "title": 'Winner I'
            },
            "wins_10": {
                "desc": "Win 10 games",
                "seq": "103",
                "title": "Winner II"
            },
            "wins_50": {
                "desc": 'Win 50 games',
                "seq": "110",
                "title": 'Winner III'
            },
            "wins_100": {
                "desc": 'Win 100 games',
                "seq": "120",
                "title": 'Winner IV'
            },
            "t8s_1": {
                "desc": 'Get Top 8 at 1 tournament',
                "seq": "140",
                "title": 'Approaching the Top I'
            },
            "t8s_10": {
                "desc": 'Get Top 8 at 10 tournaments',
                "seq": "150",
                "title": 'Approaching the Top II'
            },
            "t8s_25": {
                "desc": 'Get Top 8 at 25 tournaments',
                "seq": "160",
                "title": 'Approaching the Top III'
            },
            "tournament_wins_1": {
                "desc": 'Win 1 tournament',
                "seq": "170",
                "title": 'Am I the best yet? I'
            },
            "tournament_wins_5": {
                "desc": 'Win 5 tournaments',
                "seq": "180",
                "title": 'Am I the best yet? II'
            },
            "tournament_wins_25": {
                "desc": 'Win 25 tournaments',
                "seq": "190",
                "title": 'Am I the best yet? III'
            },
            "majority_tournament_wins": {
                "desc": 'Win the majority of the tournaments you enter',
                "seq": "200",
                "title": 'King of the Bracket'
            },
            "multiple_tournament_wins_while_undefeated": {
                "desc": 'Win more than one tournament and have 0 losses',
                "seq": "210",
                "title": 'Undisputed Champion'
            },
            "10_consecutive_tournament_wins": {
                "desc": 'Win 10 tournaments in a row',
                "seq": "220",
                "title": 'Cannot be Stopped'
            },
            "no_longer_dominated": {
                "desc": 'Beat a player after they had beat you at least 3 times in a row',
                "seq": "224",
                "title": "Showing Improvement"
            },
            "dominating": {
                "desc": 'Beat the same player at least 3 times in a row',
                "seq": "225",
                "title": "Dominating"
            },
            "beat_good_players_usually": {
                "desc": 'Beat players ranked above you more often than you lose to them',
                "seq": "230",
                "title": 'Am I unranked trash?'
            },
            "win_from_losers": {
                "desc": 'Win a tournament from the losers bracket',
                "seq": "000",
                "title": 'Winning the Hard Way'
            },
            "undefeated_win": {
                "desc": 'Win a tournament without losing a match',
                "seq": "240",
                "title": 'Easy $$$'
            },
            "early_loss_top_4": {
                "desc": 'Lose in the first round and make top 4',
                "seq": "250",
                "title": 'Losers run'
            },
            "beat_3_better_players": {
                "desc": 'Beat 3 players ranked higher than you in one tournament',
                "seq": "260",
                "title": 'Hidden Boss'
            }
        }
        sname = name if '&' not in name else name[:name.index('&')]
        md = {
            "short": short,
            "seq": medals[sname]['seq']
        }
        try:
            md['long'] = medals[sname]['desc']
            md['title'] = medals[sname]['title']
        except:
            md['long'] = ''
            md['title'] = sname
        if '&' in name:
            md['title'] += name[name.index('&')+1:]
        return md

    def getName(self,entrants):
        # Given a list of entrants, return the name the player used there, or -1
        e = map(lambda k: k.lower().replace(" ",""), entrants)
        a = map(lambda k: k.lower().replace(" ",""), self.aliases)
        for n in range(len(e)):
            if e[n] in a:
                return entrants[n]
        return -1

    def addAlias(self,a):
        if a not in self.aliases:
            self.aliases.append(a)

    def getAliases(self):
        return self.aliases

    def getTrueName(self):
        return self.name

    def isName(self,name):
        if name in self.getAliases():
            return True
        return False

    def isRanked(self):
        check_is_bye = lambda k: len(k.replace(' ', '')) >= 3 and k.replace(' ', '')[:3].lower() == 'bye' and (
        len(k.replace(' ', '')) == 3 or (k.replace(' ', '')[3:] in [str(i) for i in range(100)]))
        if check_is_bye(self.name):
            return False
        if len(self.tournaments) < 2:
            return False
        # No reason to support this right now., can probably rewrite it to be better
        # if len(filter(lambda k: k in self.tournaments.values(), self.league.tournaments.values()[::-1][:ACTIVETHRESHOLD])) < 1:
        #     return False
        return True

    def getWins(self):
        # Returns the number of wins the player has had
        return len(filter(lambda m: m.winner in self.getAliases(), self.matches))

    def addTournamentMatch(self, m, newrating):
        if m.tournament.date not in self.tournaments:
            self.tournaments[m.tournament.date] = m.tournament
        self.matches.append(m)
        self.setRating(newrating)
        self.progressMedals(m)

    def getRating(self):
        return self.rating.exposure

    def calculateRating(self):
        if self.isRanked():
            return self.getRating()
        return 'Unranked'

    def setRating(self, nr):
        self.rating = nr

    def writeRank(self):
        with open(os.path.join(self.league.gamepath,"players",self.getAliases()[0]+".json"), "w") as f:
            json.dump(self.toDict(), f, indent=4)

    def getSummary(self):
        return {
            'name': self.getAliases()[0],
            'num_tourneys': len(self.tournaments),
            'ELO': self.rating.exposure
        }

    def getOpponent(self,match):
        if self.isName(match.player1):
            return match.player2
        return match.player1

    def toDict(self):
        # Returns a dictionary containing all of the player's relevent stats
        def getMatchInfo(match):
            m = dict()
            if self.isName(match.player1):
                return {
                    'opponent': match.player2,
                    'opponent_skill_change': match.p2change,
                    'opponent_real_name': self.league.getPlayer(match.player2).getAliases()[0],
                    'skill_change': match.p1change,
                    'win': True if self.isName(match.winner) else False,
                    'date': match.tournament.date
                }
            else:
                return {
                    'opponent': match.player1,
                    'opponent_skill_change': match.p1change,
                    'opponent_real_name': self.league.getPlayer(match.player1).getAliases()[0],
                    'skill_change': match.p2change,
                    'win': True if self.isName(match.winner) else False,
                    'date': match.tournament.date
                }
        return {
            'name': self.getAliases()[0],
            'aliases': self.getAliases()[1:],
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
        self.medals[medal] = self.translateMedal(medal,str(date) + str(msg))

    def getTournamentMatches(self,tournament):
        # Return all of the players matches from tournament
        return filter(lambda k: k.tournament.date == tournament.date, self.matches)

    def progressMedals(self,match):
        def _addMedal(medal, date=match.tournament.date, msg=''):
            self.addMedal(medal, date, msg)
        # Called after scoring each match
        if self.isName(match.winner):
            loser = self.league.getPlayer(match.getLoser(self))
            if loser.medalsProgress['oldrating'] > self.medalsProgress['oldrating']:
                self.medalsProgress['better_beats'] += 1
                self.medalsProgress['better_beats_overall'] += 1
        else:
            winner = self.league.getPlayer(match.getWinner(self))
            if winner.medalsProgress['oldrating'] > self.medalsProgress['oldrating']:
                self.medalsProgress['better_losses_overall'] += 1
                self.medalsProgress['better_losses_overall'] += 1


    def earnMedals(self, tournament):
        # Called at the end of each tournament
        tournaments = len(self.tournaments)
        def _addMedal(medal, date=tournament.date, msg=''):
            self.addMedal(medal, date, msg)
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
        losses = 0
        for t in self.tournaments:
            tm = self.getTournamentMatches(tournament)
            for match in tm:
                if not self.isName(match.winner):
                    losses += 1
            tmp = filter(lambda k: k.date == t, self.league.tournaments.values())
            assert len(tmp) == 1
            tourney = tmp[0]
            ed = tourney.getEntrantsDict()
            tws += 1 if ed[self.getName(ed.keys())] == 1 else 0 # Tournament Wins
            t8s += 1 if ed[self.getName(ed.keys())] <= 8 else 0 # Top 8s
        if tws >= 1:
            _addMedal('tournament_wins_1')
        if tws >= 5:
            _addMedal('tournament_wins_5')
        if tws >= 25:
            _addMedal('tournament_wins_25')
        if t8s >= 1:
            _addMedal('t8s_1')
        if t8s >= 10:
            _addMedal('t8s_10')
        if t8s >= 25:
            _addMedal('t8s_25')
        tourney_matches = self.getTournamentMatches(tournament)
        if tournament.getEntrantsDict()[self.getName(tournament.getEntrantsDict().keys())] == 1:
            # Player won the tournament
            losses = 0
            for match in tourney_matches:
                if not self.isName(match.winner):
                    losses += 1
                    if tournament.getHighestRound() != match.round:
                        _addMedal('win_from_losers& of '+tournament.date)
            if losses == 0:
                _addMedal('undefeated_win& of '+tournament.date)
        else:
            losses = []
            for match in tourney_matches:
                if self.isName(match.winner):
                    loser = self.league.getPlayer(match.getLoser(self))
                if not self.isName(match.winner):
                    if match.round in [1,2]:
                        if tournament.getEntrantsDict()[self.getName(tournament.getEntrantsDict())] <= 4:
                            _addMedal('early_loss_top_4& of '+tournament.date)
                    losses.append(match)
            assert len(losses) == 2
        # if self.medalsProgress['better_beats'] >= 3:
        #     _addMedal('beat_3_better_players& of '+tournament.date) I think this is broken
        self.medalsProgress['better_beats'] = 0

    def addFinalMedals(self):
        if len(self.matches) == 0:
            return # fuck this
        def _addMedal(medal, date=self.matches[-1].date, msg=''):
            self.addMedal(medal, date, msg)
        # Called after all the rankings are in
        # This one needs to be unit tested well
        # if self.medalsProgress['better_beats_overall'] > self.medalsProgress['better_losses_overall']:
        #     _addMedal('beat_good_players_usually')
        wiar = 0
        twins = 0
        tlosses = 0
        losses = 0
        for t in map(lambda k: self.tournaments[k], sorted(self.tournaments.keys())):
            for match in self.getTournamentMatches(t):
                if not self.isName(match.winner):
                    losses += 1
            if self.isName(t.getWinner()['name']):
                twins += 1
                wiar += 1
                if wiar == 10:
                    _addMedal('10_consecutive_tournament_wins', t.date)
            else:
                wiar = 0
                tlosses += 1

        if twins > 1 and losses == 0:
            _addMedal('multiple_tournament_wins_while_undefeated')
        if twins > tlosses:
            _addMedal('majority_tournament_wins')

        opponents = defaultdict(list)
        for m in reversed(self.matches):
            opponents[self.getOpponent(m)].append('w' if self.isName(m.winner) else 'l')
        for o in opponents.keys():
            matches = opponents[o]
            if len(matches) >= 3:
                if matches[0] == 'w' and matches[1] == 'w' and matches[2] == 'w':
                    # dominating
                    _addMedal('dominating& '+o)
            if len(matches) >= 4:
                if matches[0] == 'w' and matches[1] == 'l' and matches[2] == 'l' and matches[3] == 'l':
                    # no longer dominated
                    _addMedal('no_longer_dominated& over '+o)


