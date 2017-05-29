import json, operator,os
from Match import Match

class Tournament:
    # Class to keep track of the data parsed from each tournament
    def __init__(self,fn,league):
        self.league = league
        self.fn = fn
        self.di = self.readUOTN(fn)
        self.entrants = self.getEntrants()
        self.date = self.di['Date'][:10]
        self.matches = self.getMatches()
        self.game = self.di['Game']
        pass

    def readUOTN(self,fn):
        f = open(fn)
        t = json.load(f)
        f.close()
        return t

    def getHighestRound(self):
        i = -1
        for m in self.matches:
            i = max(i, m.round)
        return i

    def writeUpdatedTournament(self):
        with open(os.path.join("updatedtournaments",self.game,self.fn),"w") as f:
            json.dump(self.toDict(),f,indent=4)

    def toDict(self):
        # Should ideally output in the uotn format
        ne = self.entrants
        for e in ne:
            e['real_name'] = self.league.getPlayer(e['name']).getAliases()[0]
        return {
            'entrants': ne,
            'date': self.date,
            'matches': map(lambda m: m.toDict(), self.matches),
            'game': self.game
        }

    def calc_place(self,entrants):
        # Returns the placing of each player
        # Broken/Obsolete
        for i in entrants:
            i['fakewins'] = i['fakewins'] + i['wins']
        newlist = sorted(entrants, key=operator.itemgetter('fakewins'))
        place = 0
        oldwins = len(entrants)*3
        for i in newlist:
            if i['wins'] < oldwins:
                place += 1
                oldwins = i['wins']
                i['place'] = place
            else:
                i['place'] = place
        return newlist

    def getEntrants(self):
        entrants = []
        for player in self.di['Entrants']:
            p = dict()
            p['name'] = player[0]
            p['place'] = player[1]
            entrants.append(p)
        return entrants

    def getEntrantsDict(self):
        entrants = {}
        for player in self.di['Entrants']:
            entrants[player[0].replace(" ","").lower()] = player[1]
        return entrants

    def getMatches(self):
        matches = []
        for m in self.di['Matches']:
            matches.append(Match(m, self))
        return matches

    def getWinner(self):
        w =  filter(lambda k: k['place'] == 1, self.entrants)
        assert len(w) == 1
        return w