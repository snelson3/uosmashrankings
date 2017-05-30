from trueskill import TrueSkill
from uorank.parseLib.League import League
import sys

assert len(sys.argv) > 1
for arg in sys.argv[1:]:
    league = League(TrueSkill(draw_probability=0.0), arg)
    league.loadTournaments()
    league.loadPlayers()
    for t in sorted(league.tournaments.keys()):
        league.scoreTournament(league.tournaments[t])
    league.writeRankings()