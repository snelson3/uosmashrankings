#Write something to fix the date string, because right now it includes time and is really unwieldy to look at
#Probably want to add a league class to keep track of all the multitournament records, just so everything is in classes
#to implement the neccessary changes
#change it so place is another value kept by player, calculated at the end
#Players with under 2 games have -1 as place
#Then the site just has to render those with a positive place
#   this will let people like bart/jarod with just one tournament still have a profile
#related at a boolean variable HIDEOLD
#if this is true, do the following
#for each player, look at their last tournament
#compare it to the last 5 entries in the tournaments array
#if its not any of them, make the players place -1 instead of the next yada yada
#that lets 'decay' happen
#
#and I want to make navigating the site less painful
#
#Maybe something to test later is how does resetting the ?sigma? every now and then
#effect ratings, theoretically this would make it easier for people to move up
#if they lost a lot at the beginning. I need to read up on stuff, I'm not sure if this
#is a problem with trueskill

import json
import os
import sys
import trueskill
from trueskill import Rating,rate_1vs1
import operator

GAME = sys.argv[1]
INACTIVETIME = 5; #don't ever set to more than the number of tournaments we have, it might break

env = trueskill.TrueSkill()#sigma=25/3)#draw_probability=0)


class Player:
	#Player class keeping track of all the stats calculated for each player
	def __init__(self,name):
		global env
		self.name = str(name)
		self.rating = env.Rating()
		self.place = 0 #-1 means they are not ranked
		self.oldplace = 0
		self.temprating = env.expose(self.rating)
		self.matches = []
		self.wins = 0
		self.games = 0
		self.tournaments = []
		self.num_tourneys = 0

	def checkActive(self,tourneylist):
		#checks if player has been to the last INACTIVETIME tournaments, this is weird should be rewritten
		for i in range(INACTIVETIME):
			if tourneylist[-(i+1)] in self.tournaments:
				return True
		return False

	def toDict(self):
		#Returns a dictionary containing all of the player's relevent stats, so it can be dumped
		#to a JSON file
		d = dict()
		d['name'] = self.name
		d['rating'] = env.expose(self.rating)
		matches = []
		for match in self.matches:
			m = dict()
			#switch this to not repeat include the players name
			m['Player1'] = match.player1
			m['Player2'] = match.player2
			m['DATE'] = match.date
			m['P1SkillCH'] = match.p1change
			m['P2SkillCH'] = match.p2change
			m['winner'] = match.winner
			matches.append(m)
		d['matches'] = matches
		d['wins'] = self.wins
		d['games'] = self.games
		d['tournaments'] = self.tournaments
		d['num_tourneys'] = self.num_tourneys
		d['game'] = GAME
		return d

def getPlayer(players,name):
	#Given the player's name as a string, return the player instance that matches
	for player in players:
		if player.name == str(name):
			return player

class Tournament:
	#Class to keep track of the data parsed from each tournament
	def __init__(self, f, game):
		#File is the dictionary read from the JSON file with all the relevant information
		self.di = f
		self.entrants = self.getEntrants()
		self.date = str(self.di['Date'])
		self.matches = self.getMatches()
		self.game = str(self.di['Game'])

	def toDict(self):
		d = dict()
		d['Entrants'] = self.entrants
		d['Date'] = self.date
		matches = []
		for match in self.matches:
			matches.append(match.toDict())
		d['Matches'] = matches
		d['Game'] = self.game
		d['g'] = GAME
		return d


	def calc_place(self,entrants):
	#Takes the tournament results and returns the placing of each player.
	#Does not work currently, this code was just an idea I had
		for i in entrants:
			i['fakewins'] = i['fakewins'] + i['wins']
		newlist = sorted(entrants, key=operator.itemgetter('fakewins'))
		place = 0
		oldwins = len(entrants)*3
		for i in newlist:
			if i['wins'] < oldwins:
				place+=1
				oldwins = i['wins']
				i['place'] = place
			else:
				i['place'] = place
		return newlist

	def getEntrants(self):
		entrants = []
		for player in self.di['Entrants']:
			p = dict()
			p['name'] = player
			p['rankchange'] = 0
			p['wins'] = 0
			p['fakewins'] = 0 #maybe used to calculate tournament results
			p['place'] = len(self.di['Entrants'])
			entrants.append(p)
		return entrants

	def getMatches(self):
		matches = []
		for m in self.di['Matches']:
			matches.append(Match(m,self.date))
		return matches

class Match:
	#class to keep track of information for each match in a tournament.
	def __init__(self,m,date):
		#m is a dictionary with the information in the match
		self.player1 = str(m['Player1'])
		self.player2 = str(m['Player2'])
		self.winner = str(m['winner'])
		self.winners = str(m['winners'])
		self.round = str(m['rnd'])
		self.matchnum = str(m['number'])
		self.p1change = 0
		self.p2change = 0
		self.date = date

	def isBye(self):
		if self.player1 == 'BYE' or self.player2 == 'BYE':
			return True
		return False

	def getResults(self,p1,p2):
		#figures out which player won and which player lost (returns winner, loser)
		if self.winner == p1.name:
			return p1, p2
		if self.winner == p2.name:
			return p2,p1
		else:
			print("ERROR COULD NOT PARSE MATCH RESULTS")
			exit(-1)

	def setChange(self,winner,loser):
		#Records the change in skill for each player
		if self.player1 == self.winner:
			self.p1change = winner
			self.p2change = loser
		else:
			self.p2change = winner
			self.p1change = loser

	def toDict(self):
		di = dict()
		# number  winners P1SkillCH P2SkillCH
		di['Player1'] = self.player1
		di['Player2'] = self.player2
		di['winner'] = self.winner
		di['winners'] = self.winners
		di['rnd'] = self.round
		di['number'] = self.matchnum
		di['P1SkillCH'] = self.p1change
		di['P2SkillCH'] = self.p2change
		return di

def updateplacings(entrants,tourneylist):
	#entrants is a list of all the players, need to expose all the ratings
	global env
	for player in entrants:
		player.temprating = env.expose(player.rating)
	newlist = sorted(entrants, key=lambda x: x.temprating, reverse = True)
	for e in entrants:
		if (len(e.tournaments)<2) or (e.checkActive(tourneylist) == False) or (e.name == 'BYE'):
			e.place = 0
			newlist.remove(e)
	for i in range(len(newlist)):
		newlist[i].place = i+1

def main():
	tempplayers = set()
	players = []
	files = []

	#get a list of all the players who have competed in a tournament for GAME
	for fn in os.listdir('tournaments/'+GAME):
		files.append(fn)
		f = open("tournaments/"+GAME+"/"+fn,"r")
		di = json.load(f)
		f.close()
		for e in di['Entrants']:
			P = e
			tempplayers.add(P)

	for player in tempplayers:
		players.append(Player(player))

	tourneylist = []
	files.sort()
	for fn in files:
		fo = open("tournaments/"+GAME+"/"+fn,"r")
		di = json.load(fo)
		fo.close()
		t = Tournament(di,GAME)
		tourneylist.append(t.date)

		print("DATE",str(t.date))
		for match in t.matches:
			if match.isBye():
				continue
			p1 = getPlayer(players,match.player1)
			p2 = getPlayer(players,match.player2)
			#print(p1.name,p2.name)
			if t.date not in p1.tournaments:
				p1.tournaments.append(t.date)
			if t.date not in p2.tournaments:
				p2.tournaments.append(t.date)
			winner, loser = match.getResults(p1,p2)
			newp1, newp2 = env.rate_1vs1( winner.rating, loser.rating)
			winner.wins+=1
			winner.games+=1
			loser.games+=1
			match.setChange(env.expose(newp1) - env.expose(winner.rating), env.expose(newp2) - env.expose(loser.rating))
			winner.rating = newp1
			loser.rating = newp2

			p1.matches.append(match)
			p2.matches.append(match)

			for p in t.entrants:
				if p['name'] == match.winner:
					p['wins']+=1

		updateplacings(players,tourneylist)

		for p in t.entrants:
			player = getPlayer(players,p['name'])
			if (player.oldplace == 0) and (player.place is not 0):
				p['rankchange'] = 'Ranked!'
			else:
				p['rankchange'] = player.oldplace-player.place
			if player.name == 'Thundrio':
				print(player.place,player.oldplace)
			player.oldplace = player.place
			#need to get the difference between the players old place and new place
			#Do I need to do something to remove players like Keith who is in entrants list for PM but doesnt play it?

		t.entrants = t.calc_place(t.entrants)
		f = open("updatedtournaments/"+GAME+"/"+fn,"w")
		json.dump(t.toDict(),f,indent=4)

	#make each players json file
	for player in players:
		player.num_tourneys = len(player.tournaments)
		#player.game = GAME
		if (player.name == 'BYE' ):
			continue
		if (player.num_tourneys < 2):
			continue
		if (player.checkActive(tourneylist) == False): #this needs to be changed because of functionality changes
			continue
		#print(player.name)
		f = open("players/"+GAME+"/"+GAME+"-"+player.name+".json","w")
		json.dump(player.toDict(),f,indent=4)
		f.close()

	playerlist = []
	ps = {}

	#sorted_names = []

	#Debugging info
	# print(GAME)
	# for player in players:
	# 	sorted_names.append(player.name)
		#print(env.expose(player.rating),player.name)

	#sorted_names.sort()
	#for player in sorted_names:
	#	print(player)
	for player in players:
		if (player.name == 'BYE' ):
			continue
		if (player.num_tourneys < 2):
			continue
		if (player.checkActive(tourneylist) == False): #this needs to be changed because of functionality changes
			continue
		power = dict()
		power['name'] = GAME+"-"+player.name
		power['num_tourneys'] = len(player.tournaments)
		power['ELO'] = str(env.expose(player.rating))
		power['GAME'] = GAME
		playerlist.append(power)
	out = open("players/"+GAME+"-playerlist.json","w")
	ps['players'] = playerlist
	json.dump(playerlist,out,indent=4)
	out.close()


main()
