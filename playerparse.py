from trueskill import TrueSkill
from parseLib.League import League
import sys

for arg in sys.argv[1:]:
    league = League(TrueSkill(), arg)
    league.loadTournaments()
    league.loadPlayers()
    for t in league.tournaments.values():
        league.scoreTournament(t)
    league.writeRankings()