import os
import json
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

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
    return render_template('index.html')

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
