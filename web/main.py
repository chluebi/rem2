from flask import Flask, render_template, session, redirect, request, url_for, g, flash
import requests
import secrets
import psycopg2
import util
app = Flask(__name__)

with open("secret") as f:
    l = f.read().split(" ")
    CLIENT_SECRET = l[0]
    app.secret_key = l[1]

@app.teardown_appcontext
def teardown_db(e): #Stolen directly from Flask's docs
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route("/projects/rem2/")
def hello():
    timers = []
    if "access_token" in session: 
        util.get_tokens(refresh=True)
        util.retrieve_user()
        timers = util.get_timers()
    return render_template("hello.html", timers=timers)

@app.route("/projects/rem2/login")
def login():
    session["auth_state"] = secrets.token_urlsafe(64)
    #Should this URL contain references to some variable holding the client id and URLS etc? Yeah, probably
    return redirect(f"https://discordapp.com/api/oauth2/authorize?client_id=658749181300703252&redirect_uri=https%3A%2F%2Fdittoslash.uk%2Fprojects%2Frem2%2Foauth_redirect&response_type=code&prompt=none&scope=identify&state={session['auth_state']}")

@app.route("/projects/rem2/logout")
def logout():
    session.clear()
    flash("Logged out successfully!", "success")
    return redirect(util.proxy_url_for("hello"))

@app.route("/projects/rem2/new_timer", methods=["POST"])
def new_timer():
    failed = False
    try: util.create_timer(request.form.get("label"), request.form.get("time"))
    except Exception as e: 
        print(e)
        flash("Could not create timer.", "failure")
        failed = True
    if not failed: flash("Created timer!", "success")
    return redirect(util.proxy_url_for("hello"))

@app.route("/projects/rem2/debug_see_all_timers")
def debug_all_timers():
    if session["id"] == "95575367317716992":
        timers = util.get_timers(all=True)
        return render_template("hello.html", timers=timers)
    else:
        flash("Cannot access debug page", "failure")
        return redirect(util.proxy_url_for("hello"))

@app.route("/projects/rem2/oauth_redirect")
def oauth():
    if request.args.get("state") != session["auth_state"]:
        return "State invalid! Possible clickjacking/cross-site request forgery attack detected. Please retry login, and contact the devs if this doesn't fix itself"
    failed = False
    try: util.get_tokens()
    except: 
        flash("Could not login with Discord.", "failure")
        failed = True
    try: util.retrieve_user()
    except: 
        flash("Could not get user data from Discord.", "failure")
        failed = True
    try: 
        if not util.get_user(): util.create_user()
    except: 
        flash("Could not create user in database.", "failure")
        failed = True
    if failed: session.clear()
    else: flash("Logged in successfully!", "success")
    return redirect(util.proxy_url_for("hello"))
    