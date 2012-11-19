from flask import *
from contextlib import closing
from model import *
import json
import sqlite3
import pdb, traceback
from datetime import datetime
DATABASE = "sb.sqlite"

app = Flask(__name__)

def connect_db():
    return sqlite3.connect(DATABASE)

@app.route('/initdb')
def init_db():
    print "************************************************"
    print "*********        Initializing db       *********"
    print "************************************************"
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()
    msg =  "The database has been cleared."
    print msg
    if request:
        # Don't need this if being called from command line
        resp = make_response(render_template('addevt.html', message=msg, error=False))
        return resp

def load_nba_teams():
    print "************************************************"
    print "*********       Loading NBA teams      *********"
    print "************************************************"
    f = open('static/nbateams.txt','r')
    with closing(connect_db()) as db:
        for line in f:
            loc,name = line.strip().split(',')
            print loc,name
            db.execute("INSERT INTO teams (loc, name) VALUES (?,?);",(loc,name))

        db.commit()
    print "Finished loading NBA teams"

def sql_execute(*args):
    print "using my own db execute, args:", args
    curs = g.db.execute(*args)
    g.db.commit()
    return curs

@app.before_request
def before_request():    
    g.db = connect_db()

@app.after_request
def after_request(response):
    g.db.close()
    return response

@app.route('/events/add', methods=['GET'])
def display_add_event():
    return render_template('addevt.html')

@app.route('/events/add', methods=['POST'])
def add_event():
    try:
        print request.form
        print "Ok got a http post"

        year, month, day = [int(x) for x in request.form['startdate'].split('-')]
        time = request.form['starttime'].strip()
        hour, minute = [int(x) for x in time.split(":")]

        print hour, minute
        print year, month, day

        stime = str(datetime(year, month, day, hour, minute).toordinal()) #to get utc timestamp

        event = Event(
            -1,
            stime, 
            request.form['team1'], 
            request.form['team2'], 
            request.form['location']
        )

        print "event:", event

        sql_execute("INSERT INTO events (start, team1, team2, \
                            location) VALUES (?,?,?,?);",\
            (event.start, event.team1, event.team2, event.loc))

        # pdb.set_trace()
        msg =  "This event has been recorded."
        return render_template('addevt.html', message=msg, error=False)
    except Exception as e:
        print "Exception:", e
        traceback.print_exc()
        msg =  "There was a problem."
        if type(e) == sqlite3.IntegrityError:
            msg = "This event already exists."
        return render_template('addevt.html', message=msg, error=True)

@app.route('/events/', methods=['GET'])
def events():
    events = Event.get_all(g.db)
    print events
    return json.dumps([event.toJSON() for event in events])
#     return render_template('addevt.html')

@app.route('/teams')
def get_all_teams():
    teams = Team.get_all(g.db)
    return json.dumps([team.toJSON() for team in teams])

@app.route('/vote', methods=['POST'])
def vote():
    # print "Vote form", request.form
    url = request.form['url']
    content = request.form['content']

    vote = True if 'vote' in request.form else False

    eventid = request.form['event']

    doc = Document(None, url, content)
    if doc.add_to_db(g.db):
        print "Added document to DB"
        print "doc id:", doc.id
    else:
        print "Document already exists in DB"
        doc = Document.get_from_db(g.db, url, content)

    # Record vote
    g.db.execute("INSERT INTO votes (vote, document, event) VALUES (?,?,?);", (vote, doc.id, eventid))
    g.db.commit()

    return "ok"

def doit():
    with closing(connect_db()) as db:
        # Get votes with enough info to make event and doc objects
        curs = db.execute("SELECT vote, events.id, start, location, score, teams1.id, teams1.loc, \
            teams1.name, teams2.id, teams2.loc, teams2.name, documents.id, url, content \
            FROM votes, events, teams AS teams1, teams AS teams2, documents \
            WHERE votes.document = documents.id AND votes.event = events.id \
            AND team1 = teams1.id AND team2 = teams2.id;")

        votes = []
        for vote, evt_id, start, loc, score, teams1_id, teams1_loc, teams1_name, \
                teams2_id, teams2_loc, teams2_name, doc_id, url, content in curs.fetchall():
            team1 = Team(teams1_id, teams1_loc, teams1_name)
            team2 = Team(teams2_id, teams2_loc, teams2_name)
            event = Event(evt_id, start, team1, team2, loc)
            doc = Document(doc_id, url, content)

            votes.append( (vote, event, doc) )

        words={} # maps doc.id to a list of words it contains
        all_words = []
        for vote, event, doc in votes:
            docwords = doc.get_words()
            words[doc.id] = {} # word -> count of that word in the doc
            for word in docwords:
                if not words[doc.id].get(word):
                    words[doc.id][word] = 1
                else:
                    words[doc.id][word] += 1

            # Keep track of all words seen
            for word in words[doc.id].keys():
                if word not in all_words:
                    all_words.append(word)

        # Make feature vectors
        training_data = {} # Maps event.id -> (feature vector, vote)
        for vote, event, doc in votes:
            # First add word counts
            vec = [0]*(len(all_words)+6)
            for i in range(len(all_words)):
                word = all_words[i]
                if words[doc.id].get(word):
                    vec[i] = words[doc.id][word]

            # features specific to the event
            if words[doc.id].get(event.team1.name):
                vec[len(all_words)] = 1

            if words[doc.id].get(event.team2.name):
                vec[len(all_words)+1] = 1

            if words[doc.id].get(event.team1.loc):
                vec[len(all_words)+2] = 1

            if words[doc.id].get(event.team2.loc):
                vec[len(all_words)+3] = 1

            if words[doc.id].get(event.loc):
                vec[len(all_words)+4] = 1

            if event.score != None and words[doc.id].get(str(event.score)):
                vec[len(all_words)+5] = 1

            training_data[event.id] = (vec, vote)
            pdb.set_trace()

        print"\n\n"
        print "Got here"
        print training_data
        pdb.set_trace()








if __name__ == '__main__':
    app.run(debug=True)