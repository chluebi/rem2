from pytz import timezone, utc
from flask import session, request, g, url_for
import requests
import datetime
import psycopg2
from lib import common, time_handle, database

config = common.parse_config("web")

DATETIME_FORMAT = '%d/%m/%y %H:%M:%S'

def timeywimeicate(secs, tz): #seconds to localized, strf'd time
    return time_handle.seconds_to_datetime(time_handle.delocalize_seconds(secs, tz)).strftime(DATETIME_FORMAT)

#Web stuff
def proxy_url_for(f): #The site runs behind a Caddy proxy, so is technically running HTTP while displaying as HTTPS, so the urls url_for generates are HTTPS and thus breaks if the HTTP redirection isn't working (which it only isn't for Raine)
    return url_for(f, _scheme='https', _external=True)

#Database setup
def db():
    if 'db' not in g:
        g.db = database.connect()
    return g.db

#Database interaction
def get_user(): return database.get_user(db(), session["id"])

def get_timers(all=False): 
    rows = database.get_timers(db(), session["id"], all)
    timers = []
    tz = get_user()[1]
    for i in rows:
        created = timeywimeicate(i[2], tz)
        triggered = timeywimeicate(i[3], tz)
        if i[5] == 0: rows[5] = '@me'
        if i[6]: link = f'<a href="https://discordapp.com/channels/{i[5]}/{i[6]}/{i[7]}"> message </a>'
        else: link = 'created in web'
        timers.append([i[0], i[1], created, triggered, link])
    return timers

def create_user(): database.create_user(db(), session["id"], "UTC")

def create_timer(label, at):
    time = time_handle.delocalize_datetime(datetime.datetime.fromisoformat(at), get_user()[1])
    #TODO: get time from request object?
    database.create_timer(db(), label, datetime.datetime.utcnow().timestamp(), time.timestamp(), session['id'])

def update_timezone(timezone): database.update_timezone(db(), session["id"], timezone)

#OAuth stuff
def retrieve_user(store_in_session=True):
    ur = requests.get('https://discordapp.com/api/users/@me', headers={'Authorization': f"Bearer {session['access_token']}"})
    if store_in_session:
        session['username'] = ur.json()['username']
        session['id'] = ur.json()['id']
    return ur.json()

def get_tokens(refresh=False):
    data = {
        'client_id': config["client_id"],
        'client_secret': config["client_secret"],
        'grant_type': 'refresh_token' if refresh else 'authorization_code',
        'redirect_uri': config["redirect_uri"],
        'scope': 'identify'
    }
    if refresh: data['refresh_token'] = session['refresh_token']
    else: data['code'] = request.args.get('code'),
    r = requests.post('https://discordapp.com/api/oauth2/token', data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    session['access_token'] = r.json()['access_token']
    session['refresh_token'] = r.json()['refresh_token']