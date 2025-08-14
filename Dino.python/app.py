import json
from flask import Flask, render_template, request, redirect, url_for, session, jsonify

# This line initializes your Flask application and fixes the error
app = Flask(__name__)
app.secret_key = "dino_run_secret"

# --- User and High Score Management ---
USERS_FILE = "users.json"
HIGHSCORE_FILE = "highscore.json"

def load_users():
    try:
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def load_highscores():
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            data = json.load(f)
            if isinstance(data, dict) and "highscores" in data:
                return data
            elif isinstance(data, list):
                return {"highscores": data}
            else:
                return {"highscores": []}
    except (FileNotFoundError, json.JSONDecodeError):
        return {"highscores": []}

def save_highscores(highscores_data):
    with open(HIGHSCORE_FILE, "w") as f:
        json.dump(highscores_data, f, indent=4)

# --- Routes ---
@app.route("/")
def index():
    if "username" not in session:
        return redirect(url_for("login"))
    
    highscores_data = load_highscores()["highscores"]
    valid_scores = [score for score in highscores_data if isinstance(score, dict) and "score" in score]
    highscores_data = sorted(valid_scores, key=lambda x: x["score"], reverse=True)[:5]
    
    return render_template(
        "index.html",
        username=session["username"],
        highscores=highscores_data
    )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()
        if username in users and users[username]["password"] == password:
            session["username"] = username
            return redirect(url_for("index"))
        else:
            return render_template("login.html", error="Invalid username or password.")
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        users = load_users()
        if username in users:
            return render_template("register.html", error="Username already exists.")
        
        users[username] = {"password": password, "score": 0}
        save_users(users)
        
        highscores_data = load_highscores()
        highscores_data["highscores"].append({"username": username, "score": 0})
        save_highscores(highscores_data)

        session["username"] = username
        return redirect(url_for("index"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect(url_for("login"))

@app.route("/update_highscore", methods=["POST"])
def update_highscore():
    if "username" not in session:
        return jsonify({"success": False, "message": "Not logged in"}), 401

    new_score = int(request.json.get("score"))
    username = session["username"]

    users = load_users()
    highscores_data = load_highscores()

    if username in users:
        if new_score > users[username]["score"]:
            users[username]["score"] = new_score
            save_users(users)

    found = False
    for player in highscores_data["highscores"]:
        if player["username"] == username:
            if new_score > player["score"]:
                player["score"] = new_score
            found = True
            break
    if not found:
        highscores_data["highscores"].append({"username": username, "score": new_score})
    
    save_highscores(highscores_data)

    return jsonify({"success": True, "message": "High score updated"})

if __name__ == '__main__':
    app.run(debug=True)