from BeautifulSoup import *
from datetime import datetime
import pdb, traceback

class Event(object):
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

    def add_to_db(self, db):
        """
        start -> a Datetime object
        Inserts a new event record into db and returns a new Event obj
        """
        try:
            db.execute("INSERT INTO events (start, team1, team2, \
                                location) VALUES (?,?,?,?);",\
                (self.start.toordinal(), self.team1.id, self.team2.id, self.loc))
            curs = db.execute("SELECT last_insert_rowid()")
            self.id = curs.fetchone()[0]
            db.commit()
            return True
        except Exception as e:
            print "Exception:", e
            traceback.print_exc()
            print "This already exists in the DB"
            return False

    def update_score(self, db, score):
        """
        score -> a Score object
        Updates score in DB, stores string rep of score in DB
        """
        try:
            self.score = score
            db.execute("UPDATE events SET score=? WHERE id=?;", (str(score), self.id))
            db.commit()
            return True
        except Exception as e:
            print "Exception:", e
            traceback.print_exc()
            return False

    def __str__(self):
        return str(self.team1) + " vs. " + str(self.team2) + " at " + self.loc \
            + ", " + str(self.start) + ", " + str(self.score if self.score != None else "No score")

    @staticmethod
    def from_id(db, evt_id):
        curs = db.execute("SELECT events.id, start, location, score, teams1.id, teams1.loc, \
            teams1.name, teams2.id, teams2.loc, teams2.name FROM events, teams AS teams1,\
             teams AS teams2 WHERE team1 = teams1.id AND team2 = teams2.id AND events.id=?;",(evt_id,))
        id, start, loc, score, teams1_id, teams1_loc, teams1_name, teams2_id, teams2_loc, teams2_name = curs.fetchone()
        team1 = Team(teams1_id, teams1_loc, teams1_name)
        team2 = Team(teams2_id, teams2_loc, teams2_name)
        start = datetime.fromordinal(start)
        evt = Event(id, start, team1, team2, loc)

        return evt

        
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
            start = datetime.fromordinal(start)
            evt = Event(id, start, team1, team2, loc)
            events.append(evt)

        return events

    def toJSON(self):
        d = self.__dict__
        d['team1'] = self.team1.toJSON()
        d['team2'] = self.team2.toJSON()

        d['start'] = self.start.toordinal()

        if self.score:
            d['score'] = self.score.toJSON()
        return d

class NFL_Game(Event):
    def __init__(self, id, week, start, team1, team2, loc, score=None):
        
        super(NFL_Game, self).__init__(id, start, team1, team2, loc, score)
        
        if int(week) > 0 and int(week) < 18:
            self.week = int(week)

    def __str__(self):
        return "Week " + str(self.week) + ": " + super(NFL_Game, self).__str__()

    def toJSON(self):
        d = super(NFL_Game, self).toJSON()
        d['week'] = self.week
        return d

    def add_to_db(self, db):
        """
        start -> a Datetime object
        Inserts a new event record into db and returns a new Event obj
        """
        # First add to events, then to nfl_games
        super(NFL_Game, self).add_to_db(db)

        try:
            db.execute("INSERT INTO nfl_games (id, week) VALUES (?,?);",\
                (self.id, self.week))
            db.commit()
            return True
        except Exception as e:
            print "Exception:", e
            traceback.print_exc()
            print "This nfl game already exists in the DB"
            return False

    @staticmethod
    def from_id(db, evt_id):
        curs = db.execute("SELECT events.id, week, start, location, score, teams1.id, teams1.loc, \
            teams1.name, teams2.id, teams2.loc, teams2.name \
            FROM events, nfl_games, teams AS teams1,teams AS teams2 \
            WHERE team1 = teams1.id AND team2 = teams2.id AND \
                events.id=nfl_games.id AND nfl_games.id=?;",(evt_id,))

        id, week, start, loc, score, teams1_id, teams1_loc, teams1_name, teams2_id, teams2_loc, teams2_name = curs.fetchone()
        team1 = Team(teams1_id, teams1_loc, teams1_name)
        team2 = Team(teams2_id, teams2_loc, teams2_name)
        start = datetime.fromordinal(start)

        evt = NFL_Game(id, week, start, team1, team2, loc)

        return evt

        
    @staticmethod
    def get_all(db):
        """
        Retrieves all of the events in the db
        Returns a list of Event objects
        """
        curs = db.execute("SELECT events.id, week, start, location, score, teams1.id, teams1.loc, \
            teams1.name, teams2.id, teams2.loc, teams2.name \
            FROM events, nfl_games, teams AS teams1, teams AS teams2 \
            WHERE events.id=nfl_games.id AND team1 = teams1.id AND team2 = teams2.id;")

        events = []

        for id, week, start, loc, score, teams1_id, teams1_loc, teams1_name, teams2_id, teams2_loc, teams2_name in curs.fetchall():
            team1 = Team(teams1_id, teams1_loc, teams1_name)
            team2 = Team(teams2_id, teams2_loc, teams2_name)
            start = datetime.fromordinal(start)
            evt = NFL_Game(id, week, start, team1, team2, loc)
            events.append(evt)

        return events

class Score:
    def __init__(self, team1_score, team2_score):
        self.team1_score = team1_score
        self.team2_score = team2_score

    @staticmethod
    def from_str(string):
        t1, t2 = [int(x) for x in string.split('-')]
        return Score(t1, t2)

    def __str__(self):
        return str(self.team1_score) + "-" + str(self.team2_score)

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
    def from_id(db, id):
        """
        Get team obj from location/city
        """
        curs = db.execute("SELECT id, loc, name FROM teams WHERE id=?;", (id,))
        id, loc, name = curs.fetchone()

        return Team(id,loc, name)

    @staticmethod
    def from_name_location(db, name, loc):
        """
        Get team obj from location/city
        """
        curs = db.execute("SELECT id, loc, name FROM teams WHERE loc=? AND UPPER(name) = UPPER(?);", (loc,name))
        id, loc, name = curs.fetchone()

        return Team(id,loc, name)

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
    
    @staticmethod
    def get_all(db):
        curs = db.execute("SELECT * FROM documents;")
        
        docs = []
        for id, url, content, time in curs.fetchall():
            doc = Document(id, url, content)
            docs.append(doc)
        return docs

    def get_words(self):
        soup = BeautifulSoup(self.content)
        text = self.get_text(soup).lower()
        words = self.split_text(text)
        # print "Words:", words
        return words

    def get_text(self, soup):
        v = soup.string
        if v == None:
            c = soup.contents
            resulttext = ""
            for t in c:
                if hasattr(t, 'name') and t.name not in ['script', 'head', 'style', 'noscript']:
                    subtext = self.get_text(t)
                    resulttext += subtext+"\n"
            return resulttext
        else:
            return v.strip()

    def split_text(self, text):
        splitter = re.compile("\\W*")
        words = [s.lower() for s in splitter.split(text) if s != '']
        return words



    def __str__(self):
        return self.url

        
