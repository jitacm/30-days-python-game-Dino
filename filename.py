import os
import json
import datetime
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

SCORE_FILE = os.path.join(os.path.dirname(__file__), "score.json")

# ----------- Utility Functions -----------
def read_score():
    if not os.path.exists(SCORE_FILE) or os.path.getsize(SCORE_FILE) == 0:
        write_score({})
    try:
        with open(SCORE_FILE, "r") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        write_score({})
        return {}

def write_score(scores):
    with open(SCORE_FILE, "w") as f:
        json.dump(scores, f, indent=4)

# ----------- Routes -----------
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_score", methods=["GET"])
def get_score():
    """Return all player scores."""
    return jsonify(read_score())

@app.route("/save_score", methods=["POST"])
def save_score():
    """Save a new score for a player if it's higher than their previous best."""
    player = request.json.get("player", "Anonymous")
    try:
        new_score = int(request.json.get("score", 0))
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid score"}), 400

    scores = read_score()

    # If new player or better score
    if player not in scores or new_score > scores[player]["score"]:
        scores[player] = {
            "score": new_score,
            "date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        write_score(scores)

    return jsonify(scores)

@app.route("/leaderboard", methods=["GET"])
def leaderboard():
    """Return leaderboard sorted by highest score."""
    scores = read_score()
    sorted_scores = sorted(scores.items(), key=lambda x: x[1]["score"], reverse=True)
    return jsonify(sorted_scores)

@app.route("/reset_score", methods=["POST"])
def reset_score():
    """Reset all scores."""
    write_score({})
    return jsonify({"message": "All scores reset successfully", "scores": {}})

# ----------- Run App -----------
if __name__ == "__main__":
    app.run(debug=True)
