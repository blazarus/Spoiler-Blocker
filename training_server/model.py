from BeautifulSoup import *
import pdb
class Event:
	def __init__(self, id, start, team1, team2, loc, score=None):
		"""
		team1, team2 (Team)
		score (Score)
		"""
		self.id = id
		self.start = start
		self.team1 = team1
		self.team2 = team2
		self.loc = loc
		self.score = score # A score object

	@staticmethod
	def get_all(db):
		"""
		Retrieves all of the events in the db
		Returns a list of Event objects
		"""
		curs = db.execute("SELECT events.id, start, location, score, teams1.id, teams1.loc, \
			teams1.name, teams2.id, teams2.loc, teams2.name FROM events, teams AS teams1,\
			 teams AS teams2 WHERE team1 = teams1.id AND team2 = teams2.id;")

		events = []

		for id, start, loc, score, teams1_id, teams1_loc, teams1_name, teams2_id, teams2_loc, teams2_name in curs.fetchall():
			team1 = Team(teams1_id, teams1_loc, teams1_name)
			team2 = Team(teams2_id, teams2_loc, teams2_name)
			evt = Event(id, start, team1, team2, loc)
			events.append(evt)

		print "events:", events[0].__dict__

		return events

	def toJSON(self):
		d = self.__dict__
		d['team1'] = self.team1.toJSON()
		d['team2'] = self.team2.toJSON()

		if self.score:
			d['score'] = self.score.toJSON()
		return d

class Score:
	def __init__(self, team1_score, team2_score):
		self.team1_score = team1_score
		self.team2_score = team2_score

	def toJSON(self):
		return self.__dict__

class Team:
	def __init__(self, id, loc, name):
		self.id = id
		self.name = name
		self.loc = loc

	def __str__(self):
		return self.loc + " " + self.name

	def toJSON(self):
		return self.__dict__

	@staticmethod
	def get_all(db):
		"""
		Retrieves all of the teams in the db
		Returns a list of Team objects
		"""
		curs = db.execute("SELECT id, loc, name FROM teams;")

		teams = []

		for id, loc, name in curs.fetchall():
			teams.append(Team(id,loc, name))

		return teams

class Document:
	def __init__(self, id, url, content):
		if id == None:
			self.id = -1
		else:
			self.id = id
		self.url = url
		self.content = content

	def add_to_db(self, db):
		try:
			db.execute("INSERT INTO documents (url, content) VALUES (?,?);", (self.url, self.content))
			curs = db.execute("SELECT last_insert_rowid()")
			self.id = curs.fetchone()[0]
			db.commit()
			return True
		except:
			print "This already exists in the DB"
			return False
	@staticmethod
	def get_from_db(db, url, content):
		curs = db.execute("SELECT * FROM documents WHERE url=? AND content=?;", (url, content))
		row = curs.fetchone()
		id, url, content, date = row
		return Document(id, url, content)

	def get_words(self):
		soup = BeautifulSoup(self.content)
		text = self.get_text(soup)
		words = self.split_text(text)
		print "Words:", words
		return words

	def get_text(self, soup):
		v = soup.string
		if v == None:
			c = soup.contents
			resulttext = ""
			for t in c:
				print "t:", type(t)
				if hasattr(t, 'name') and t.name not in ['script', 'head', 'style']:
					print "ok we want this node"
					subtext = self.get_text(t)
					resulttext += subtext+"\n"
				else:
					print "this is a script, head or style"
			return resulttext
		else:
			return v.strip()

	def split_text(self, text):
		splitter = re.compile("\\W*")
		words = [s.lower() for s in splitter.split(text) if s != '']
		return words



	def __str__(self):
		return self.url

		
