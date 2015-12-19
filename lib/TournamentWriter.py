import json
from Globals import TNFILENAME

class TournamentWriter:
        def storeTournament(self,tournament,fn):
            '''Writes a uotn file in JSON that holds the tournament data.
               See the README for a description.
            '''

            fn = fn.split('.')[0]
            out = open(fn+tournament.game+TNFILENAME, "w")

            players = []
            matches = []

            for player in tournament.entrants:
                players.append(player.name)

            for match in tournament.bracket:
                m = {}
                m['Player1'] = match.player1.name
                m['Player2'] = match.player2.name
                m['rnd'] = match.rnd
                m['number'] = match.number
                m['winner'] = match.winner.name
                matches.append(m)

            jsn = {};
            jsn['Date'] = tournament.date
            jsn['Entrants'] = players
            jsn['Game'] = tournament.game
            jsn['Matches'] = matches

            json.dump(jsn,out,indent=4)
            out.close()
