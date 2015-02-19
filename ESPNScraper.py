import requests
import re
#sport format must match espnURL-- nfl, nba
class ESPNScraper:
    '''
	accepts either nfl or nba as a string for 'sport'. returns a 
	dict : key - divisions, values - (teams, schedule)
    '''
    def __init__(self, sport):
	self.teamsurl = 'http://espn.go.com/'+sport+'/teams'
	self.teamreq = requests.get(self.teamsurl)
	self.raw = self.teamreq.text
	self.sport = sport
        self.results = {}

    def parse(self):
	self.divisionHomes = [m.start() for m in re.finditer('class="span-2', self.raw)]
	if self.sport == 'nfl':
	    self.divisionHomes.pop()
	i=0
	split1 = []
	while i < len(self.divisionHomes)-1:
	    split1.append(self.raw[self.divisionHomes[i]:self.divisionHomes[i+1]])
	    i += 1

	for div in split1:
	    divTeamResults = []
	    thisDiv = div[div.find('<h4>')+4:]
	    thisDiv = thisDiv[:thisDiv.find('</h4>')]
	    if self.sport == 'nfl':
		thisDiv = thisDiv[:thisDiv.find('<')]
	    divTeams = div.split('<h5 >')[1:]
	    for team in divTeams:
		thisTeam = team[team.find('>')+1:]
		thisTeam = thisTeam[:thisTeam.find('<')]
		teamSched = team[team.find('|')+1:]
		teamSched = teamSched[teamSched.find('"')+1:teamSched.find('>')-1]
		divTeamResults.append((thisTeam,teamSched))
	    self.results[thisDiv] = divTeamResults
       
	return self.results		
	
 
class ESPNScheduleScraper:
    def __init__(self,sport, sportDict):
	self.baseURL = 'http://espn.go.com'
	self.sport = sport
	self.sportDict = sportDict
	self.follies = []
	self.results = {}

	def hasNumbers(string):
	    return any(char.isdigit() for char in string)
	
	for div in self.sportDict:
	    thisDiv = div
	    thisDivTeamsTuple = self.sportDict[thisDiv]
	    self.teamResults = {}
	    for team in thisDivTeamsTuple:
	    	thisTeam = team[0]
		thisTeamSchedUrl = self.baseURL + team[1]
		thisSchedule = []
	        thisRequest = requests.get(thisTeamSchedUrl)
	        thisRequestRaw = thisRequest.text[thisRequest.text.find('<table'):thisRequest.text.find('</table>')].split('<tr')
		i=3
		while i <= len(thisRequestRaw):
		    try: 
			thisGameRaw = thisRequestRaw[i]
		        if self.sport == 'nfl':
			    thisGameDate = thisGameRaw[[m.start() for m in re.finditer('<td>', thisGameRaw)][1]+4:[m.start() for m in re.finditer('</td>', thisGameRaw)][1]]
			elif self.sport == 'nba':
			    thisGameDate = thisGameRaw[thisGameRaw.find('td>')+3:thisGameRaw.find('</td')]
		        thisGameOpponent = thisGameRaw[[m.start() for m in re.finditer('<a href=',thisGameRaw)][1]:[m.start() for m in re.finditer('</a>', thisGameRaw)][1]]
		        thisGameOpponent = thisGameOpponent[thisGameOpponent.find('>')+1:]
			try:
		            thisGameResult = thisGameRaw[[m.start() for m in re.finditer('game-status', thisGameRaw)][1]:]
		            thisGameResult = thisGameResult[[m.start() for m in re.finditer('>',thisGameResult)][1]+1:[m.start() for m in re.finditer('<', thisGameResult)][1]]
			except:
			    thisGameResult = 'Pending'
		        thisSchedule.append((thisGameDate, thisGameOpponent, thisGameResult))
		        i += 1
		    except Exception as oops:
			self.follies.append(thisRequestRaw)
			i += 1
	        self.teamResults[thisTeam] = {'schedule' : thisSchedule}
	    self.results[thisDiv] = {'teams' : self.teamResults}


class MyError(Exception):
    def __init__(self, value):
	self.value = value
    def __str__(self):
	return repr(self.value)

if __name__ == "__name__":
    pass
