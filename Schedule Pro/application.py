import os
import googlemaps

from datetime import datetime, date, timedelta
from cs50 import SQL
from flask import Flask, flash, jsonify, redirect, render_template, request, session
from flask_session import Session
from tempfile import mkdtemp
from werkzeug.exceptions import default_exceptions, HTTPException, InternalServerError
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required

# Configure application
app = Flask(__name__)

# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///schedule.db")

# Make sure API key is set
if not os.environ.get("API_KEY"):
    raise RuntimeError("API_KEY not set")


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if request.method == "GET":
        # gets all info from SQL tables, passes it into index to display taks
        nontasks = db.execute("SELECT taskname, location, starttime, endtime, weekday FROM non WHERE user_id = ? ORDER BY starttime ASC", session["user_id"])
        anytasks = db.execute("SELECT taskname, location FROM any WHERE user_id = ?", session["user_id"])
        return render_template("index.html", nontasks=nontasks, anytasks=anytasks)


@app.route("/optimize", methods=["POST"])
@login_required
def optimize():
    """Optimize Weekly Schedule"""

    # uses api key defined in terminal by user
    gmaps = googlemaps.Client(key=os.environ.get("API_KEY"))

    def get_distance(nontask, anytask):
        # \ is just a syntax thing; allows one line to be split up
        output = gmaps.distance_matrix(anytask, nontask)\
            ['rows'][0]['elements']
        distances = [(x['distance']['value'] / 1000.) /1.60934 for x in output]
        # dividing by 1.6 to get distance in terms of miles
        return distances[0]

# list of dicts containing all fields from the "any" and "non' tables, based on the session user
    nonlist = db.execute("SELECT taskname, location, starttime, endtime, weekday FROM non WHERE user_id = ?", session["user_id"])
    anylist = db.execute("SELECT taskname, location, deadtime, deadday FROM any WHERE user_id = ?", session["user_id"])

# list of locations featured in the previously created list of dicts
    anylocation = [a['location'] for a in anylist]
    nonlocation = [b['location'] for b in nonlist]

# function takes in a location from the any time tasks and compares it to each location in the list of non-negotiable tasks
    def closest(a, nonlocation):
        shortest = 10000
        closestloc = 'place'
        for n in nonlocation:
            print("BEING COMPARED: ", a, n)
            temp = get_distance(a, n)
            if temp < shortest:
                shortest = temp
                closestloc = n
        return closestloc


# sends each location from the any list to closest function to calculate which non-neg location is closest
    for a in anylocation:
        c = closest(a, nonlocation)
        newrow = db.execute("SELECT taskname, location, deadtime, deadday from any WHERE location = ? AND user_id = ? ORDER BY deadday", a, session["user_id"])

        # adds attributes to the any time tasks and inserts row of info into nonlist
        for row in newrow:
            for task in range(len(nonlist)):
                # checks if the task's location is the closest and if the weekday is before deadline
                if nonlist[task]["location"] == c and nonlist[task]["weekday"] < int(row["deadday"]):
                    #adds weekday and starttime attributes to the random task to be inserted into table
                    row["weekday"] = nonlist[task]["weekday"]
                    row["starttime"] = nonlist[task]["endtime"]
                    # adds entime attribute to row, 20 mins after the starttime
                    time = row["starttime"]
                    stime = time.split(":")
                    mins = int(stime[1]) + 20
                    endtime = str(stime[0] + ":" + str(mins))
                    row["endtime"] = endtime
                    # truetime = time.strptime(row["starttime"], '%H:%M').time()
                    # row["endtime"] = datetime.time(truetime) + timedelta(minutes=20)
                    #adds row of info of the random task after the closest location appears
                    nonlist.insert(task + 1, row)
                    break

        #sorts list so it can be added to weekly schedule in correct order
        nonlist.sort(key = lambda x: x["starttime"])
        print("CLOSEST: ", c)
    return render_template("index.html", nontasks=nonlist)




@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # Ensure username was submitted
        if not request.form.get("username"):
            return render_template("login.html", message="You must enter a username")

        # Ensure password was submitted
        elif not request.form.get("password"):
            return render_template("login.html", message="You must enter a password")

        # Query database for username
        rows = db.execute("SELECT * FROM users WHERE username = :username",
                          username=request.form.get("username"))

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(rows[0]["hash"], request.form.get("password")):
            return render_template("login.html", message="Invalid username and/or password")

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html", message = "Enter your login information")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        if not request.form.get("username"):
            return render_template("register.html", message = "Missing username!")
        if not request.form.get("password"):
            return render_template("register.html", message = "Missing password!")
        if not request.form.get("confirmation"):
            return render_template("register.html", message = "Missing confirmation!")
        if request.form.get("password") != request.form.get("confirmation"):
            return render_template("register.html", message = "Passwords do not match!")

        check = db.execute("SELECT COUNT(*) FROM users WHERE username = ?", request.form.get("username"))
        if check[0]["COUNT(*)"] != 0:
            return render_template("register.html", message ="Username already exists!")

        passhash = generate_password_hash(request.form.get("password"))
        name = db.execute("INSERT INTO users (username, hash) VALUES (?,?)", request.form.get("username"), passhash)
        session["user_id"] = name
        return redirect("/")

    else:
        return render_template("register.html", message = "Fill out account information")

@app.route("/new", methods=["GET", "POST"])
@login_required
def new():
    """Add new task"""
    if request.method == "GET":
        return render_template("new.html")
    if request.method == "POST":
        type = request.form.get("type")

        # makes inputted date correspond to an integer so we can check if task can be inserted before deadline
        if (request.form.get("weekday").lower() or request.form.get("deadday").lower()) == "sunday":
            day = 1
        elif (request.form.get("weekday").lower() or request.form.get("deadday").lower())== "monday":
            day = 2
        elif (request.form.get("weekday").lower() or request.form.get("deadday").lower())== "tuesday":
            day = 3
        elif (request.form.get("weekday").lower() or request.form.get("deadday").lower()) == "wednesday":
            day = 4
        elif (request.form.get("weekday").lower() or request.form.get("deadday").lower()) == "thursday":
            day = 5
        elif (request.form.get("weekday").lower() or request.form.get("deadday").lower()) == "friday":
            day = 6
        elif (request.form.get("weekday").lower() or request.form.get("deadday").lower()) == "saturday":
            day = 7
        else:
            day = 8
        if day != 8:
            if type == "any":
                request.form.get("deadday")
                db.execute("INSERT INTO any (user_id, taskname, location, deadtime, deadday) VALUES (?,?,?,?,?)", session["user_id"], request.form.get("task"), request.form.get("loc"), request.form.get("deadtime"), day)
            if type == "non":
                db.execute("INSERT INTO non (user_id, taskname, location, starttime, endtime, weekday) VALUES (?,?,?,?,?,?)", session["user_id"], request.form.get("task"), request.form.get("loc"), request.form.get("starttime"), request.form.get("endtime"), day)
        return render_template("new.html")


@app.route("/drop", methods=["GET", "POST"])
@login_required
def drop():
    if request.method == "POST":
        t=request.form.get('task')
        db.execute("DELETE FROM non WHERE taskname = ?", t)
        db.execute("DELETE FROM any WHERE taskname =?", t)
        return redirect("/")
    if request.method == "GET":
        t=request.args.get('t')
        return render_template("drop.html", t=t)


def errorhandler(e):
    """Handle error"""
    if not isinstance(e, HTTPException):
        e = InternalServerError()
    return apology(e.name, e.code)


# Listen for errors
for code in default_exceptions:
    app.errorhandler(code)(errorhandler)
