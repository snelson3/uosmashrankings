import json
from Globals import TNFILENAME

class TournamentWriter:
        def storeTournament(self,tournament,fn):
            '''Writes a TNFILENAME file in JSON that holds the tournament data.
               See the README for a description.
            '''
            if fn == None:
                raise Exception("Output filename cannot be blank")
            fn = fn.split('.')[0]
            out = open(fn+tournament.game+TNFILENAME, "w")

            players = []
            matches = []

            for player in tournament.entrants:
                players.append((player.name,player.place))

            for match in tournament.bracket:
                m = {}
                assert match.player1.name in map(lambda k: k[0], players)
                m['Player1'] = match.player1.name
                assert match.player2.name in map(lambda k: k[0], players)
                m['Player2'] = match.player2.name
                m['rnd'] = match.rnd
                m['number'] = match.number
                m['winner'] = match.winner.name
                matches.append(m)

            jsn = {}
            jsn['Date'] = tournament.date
            jsn['Entrants'] = players
            jsn['Game'] = tournament.game
            jsn['Matches'] = matches

            json.dump(jsn,out,indent=4)
            out.close()
