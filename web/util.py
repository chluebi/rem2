from pytz import timezone, utc
from flask import session, request, g, url_for
import requests
import datetime
import psycopg2

with open("secret") as f:
    l = f.read().split(" ")
    CLIENT_SECRET = l[0]

DATETIME_FORMAT = "%d/%m/%y %H:%M:%S"

#Wibbly wobbly timey wimey
def detimezonify(base, to):
    target = timezone(to)
    return target.localize(base).astimezone(utc)
def timezonify(base, frm):
    fromm = timezone(frm)
    return utc.localize(base).astimezone(fromm)

#Web stuff
def proxy_url_for(f): #The site runs behind a Caddy proxy, so is technically running HTTP while displaying as HTTPS, so the urls url_for generates are HTTPS and thus breaks if the HTTP redirection isn't working (which it only isn't for Raine)
    return url_for(f, _scheme="https", _external=True)

#Database setup
def db_connect(): return psycopg2.connect(host="localhost", port=5432, database="rem", user="rem")
def db():
    if 'db' not in g:
        g.db = db_connect()
    return g.db

#Database interaction
def get_user():
	cur = db().cursor()
	command = '''SELECT * FROM users WHERE id = %s'''
	cur.execute(command, (session["id"],))
	row = cur.fetchone()
	cur.close()
	return row

def get_timers(all=False):
    cur = db().cursor()
    if all:
        command = '''SELECT * from timers'''
        cur.execute(command)
    else:
        command = '''SELECT * FROM timers WHERE author_id = %s'''
        cur.execute(command, (session["id"],))
    rows = cur.fetchall()
    cur.close()
    timers = []
    tz = get_user()[1]
    for i in rows:
        created = timezonify(datetime.datetime.fromtimestamp(i[2]), tz).strftime(DATETIME_FORMAT)
        triggered = timezonify(datetime.datetime.fromtimestamp(i[3]), tz).strftime(DATETIME_FORMAT)
        if i[5] == 0: rows[5] = "@me"
        if i[6]: link = f"<a href='https://discordapp.com/channels/{i[5]}/{i[6]}/{i[7]}'> message </a>"
        else: link = "created in web"
        timers.append([i[0], i[1], created, triggered, link])
    return timers

def create_user():
	cur = db().cursor()
	command = '''INSERT INTO users(id, timezone) VALUES (%s, %s);'''
	cur.execute(command, (session["id"], "UTC"))
	db().commit()
	cur.close()

def create_timer(label, at):
    cur = db().cursor()
    time = detimezonify(datetime.datetime.fromisoformat(at), get_user()[1])
    command = '''INSERT INTO timers(label, timestamp_created, timestamp_triggered, author_id) VALUES (%s, %s, %s, %s);'''
    cur.execute(command, (label, datetime.datetime.utcnow().timestamp(), time.timestamp(), session["id"]))
    db().commit()
    cur.close()

def update_timezone(timezone):
	cur = g.cursor()
	command = '''UPDATE users
                SET user_timezone = %s
                WHERE user_id = %s;'''
	cur.execute(command, (timezone, session["id"]))
	db().commit()
	cur.close()


#OAuth stuff
def retrieve_user(store_in_session=True):
    ur = requests.get("https://discordapp.com/api/users/@me", headers={"Authorization": f"Bearer {session['access_token']}"})
    if store_in_session:
        session["username"] = ur.json()["username"]
        session["id"] = ur.json()["id"]
    return ur.json()

def get_tokens(refresh=False):
    data = {
        "client_id": "658749181300703252",
        "client_secret": CLIENT_SECRET,
        "grant_type": "refresh_token" if refresh else "authorization_code",
        "redirect_uri": "https://dittoslash.uk/projects/rem2/oauth_redirect",
        "scope": "identify"
    }
    if refresh: data["refresh_token"] = session["refresh_token"]
    else: data["code"] = request.args.get("code"),
    r = requests.post("https://discordapp.com/api/oauth2/token", data=data, headers={"Content-Type": "application/x-www-form-urlencoded"})
    session["access_token"] = r.json()["access_token"]
    session["refresh_token"] = r.json()["refresh_token"]