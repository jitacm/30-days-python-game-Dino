
import os
import json
from flask import Flask, render_template, request, jsonify


# This line initializes your Flask application and fixes the error
app = Flask(__name__)
app.secret_key = "dino_run_secret"


SCORE_FILE = os.path.join(os.path.dirname(__file__), "score.json")

def read_score():
    # If file doesn't exist or is empty/corrupted, reset it
    if not os.path.exists(SCORE_FILE) or os.path.getsize(SCORE_FILE) == 0:
        write_score(0)
    
    try:
        with open(SCORE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        # If JSON is broken, reset to default
        write_score(0)
        return {"highScore": 0}

def write_score(new_score):
    with open(SCORE_FILE, "w") as f:
        json.dump({"highScore": new_score}, f)

@app.route('/')


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


@app.route("/get_score", methods=["GET"])
def get_score():
    return jsonify(read_score())

@app.route("/save_score", methods=["POST"])
def save_score():
    try:
        new_score = int(request.json.get("score", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid score"}), 400

    data = read_score()
    if new_score > data["highScore"]:
        write_score(new_score)
    return jsonify(read_score())

if __name__ == "__main__":
    app.run(debug=True)

