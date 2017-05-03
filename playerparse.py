from trueskill import TrueSkill
from parseLib.League import League
import sys

for arg in sys.argv[1:]:
    league = League(TrueSkill(), arg)
    league.loadTournaments()
    league.loadPlayers()
    for t in sorted(league.tournaments.keys()):
        league.scoreTournament(league.tournaments[t])
    league.writeRankings()