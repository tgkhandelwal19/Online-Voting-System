from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)
app.secret_key = "votingsecret"

# Create database
def get_db():
    return sqlite3.connect("voting.db")

# Create tables
with get_db() as con:
    con.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        password TEXT,
        has_voted INTEGER DEFAULT 0
    )
    """)
    con.execute("""
    CREATE TABLE IF NOT EXISTS candidates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        votes INTEGER DEFAULT 0
    )
    """)

# Home
@app.route("/")
def home():
    return render_template("login.html")

# Register
@app.route("/register", methods=["POST"])
def register():
    name = request.form["name"]
    password = request.form["password"]

    with get_db() as con:
        con.execute("INSERT INTO users(name,password) VALUES(?,?)",(name,password))
    return redirect("/")

# Login
@app.route("/login", methods=["POST"])
def login():
    name = request.form["name"]
    password = request.form["password"]

    con = get_db()
    user = con.execute("SELECT * FROM users WHERE name=? AND password=?",(name,password)).fetchone()

    if user:
        session["user_id"] = user[0]
        return redirect("/vote")
    else:
        return "Invalid Login"

# Show candidates
@app.route("/vote")
def vote():
    if "user_id" not in session:
        return redirect("/")

    con = get_db()
    user = con.execute("SELECT has_voted FROM users WHERE id=?",(session["user_id"],)).fetchone()

    if user[0] == 1:
        return "You have already voted"

    candidates = con.execute("SELECT * FROM candidates").fetchall()
    return render_template("vote.html", candidates=candidates)

# Vote action
@app.route("/cast/<int:id>")
def cast(id):
    con = get_db()
    user_id = session["user_id"]

    voted = con.execute("SELECT has_voted FROM users WHERE id=?",(user_id,)).fetchone()[0]

    if voted == 1:
        return "Already voted"

    con.execute("UPDATE candidates SET votes=votes+1 WHERE id=?", (id,))
    con.execute("UPDATE users SET has_voted=1 WHERE id=?", (user_id,))
    con.commit()

    return "Vote Successful"

# Add candidates (admin)
@app.route("/add", methods=["POST"])
def add():
    name = request.form["name"]
    with get_db() as con:
        con.execute("INSERT INTO candidates(name) VALUES(?)",(name,))
    return "Candidate Added"

# Results
@app.route("/result")
def result():
    con = get_db()
    data = con.execute("SELECT name, votes FROM candidates").fetchall()
    return str(data)

app.run(debug=True)
