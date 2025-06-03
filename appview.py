
from flask import Flask, render_template
import json
import os

app = Flask(__name__)
DATA_FILE = 'scores.json'

groups = {
    'A': {
        'pitch': 'Pitch 1',
        'fixtures': [
            ("1:00 PM", "Tigers", "Thunder"),
            ("1:15 PM", "Buzz Bees", "Raptors"),
            ("1:30 PM", "Tigers", "Buzz Bees"),
            ("1:45 PM", "Thunder", "Raptors"),
            ("2:00 PM", "Tigers", "Raptors"),
            ("2:15 PM", "Thunder", "Buzz Bees")
        ]
    },
    'B': {
        'pitch': 'Pitch 2',
        'fixtures': [
            ("1:00 PM", "Galacticos", "Lightning"),
            ("1:10 PM", "Devils", "Emeralds"),
            ("1:20 PM", "Raiders", "Galacticos"),
            ("1:30 PM", "Lightning", "Devils"),
            ("1:40 PM", "Emeralds", "Raiders"),
            ("1:50 PM", "Galacticos", "Devils"),
            ("2:00 PM", "Lightning", "Emeralds"),
            ("2:10 PM", "Raiders", "Devils"),
            ("2:20 PM", "Galacticos", "Emeralds"),
            ("2:30 PM", "Lightning", "Raiders")
        ]
    },
    'C': {
        'pitch': 'Pitch 3',
        'fixtures': [
            ("1:00 PM", "Avengers", "Sapphires"),
            ("1:10 PM", "Grim Reapers", "Emeralds 2"),
            ("1:20 PM", "Sonics", "Avengers"),
            ("1:30 PM", "Sapphires", "Grim Reapers"),
            ("1:40 PM", "Emeralds 2", "Sonics"),
            ("1:50 PM", "Avengers", "Grim Reapers"),
            ("2:00 PM", "Sapphires", "Emeralds 2"),
            ("2:10 PM", "Sonics", "Grim Reapers"),
            ("2:20 PM", "Avengers", "Emeralds 2"),
            ("2:30 PM", "Sapphires", "Sonics")
        ]
    },
    'D': {
        'pitch': 'Pitch 4',
        'fixtures': [
            ("1:00 PM", "Aces", "Red Rebels"),
            ("1:15 PM", "Blazies", "Gems"),
            ("1:30 PM", "Aces", "Blazies"),
            ("1:45 PM", "Red Rebels", "Gems"),
            ("2:00 PM", "Aces", "Gems"),
            ("2:15 PM", "Red Rebels", "Blazies")
        ]
    },
    'Semi1': {
        'pitch': 'Pitch 1',
        'fixtures': [("2:45 PM", "Winner A", "Winner D")]
    },
    'Semi2': {
        'pitch': 'Pitch 3',
        'fixtures': [("2:45 PM", "Winner B", "Winner C")]
    },
    'Final': {
        'pitch': 'Pitch 3',
        'fixtures': [("3:10 PM", "Winner Semi1", "Winner Semi2")]
    }
}

def load_scores():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def calculate_table(fixtures, scores):
    table = {}
    for i, (_, team1, team2) in enumerate(fixtures):
        score = scores.get(str(i))
        table.setdefault(team1, {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'Pts': 0})
        table.setdefault(team2, {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'Pts': 0})
        if score:
            s1 = int(score['home'])
            s2 = int(score['away'])
            table[team1]['P'] += 1
            table[team2]['P'] += 1
            table[team1]['GF'] += s1
            table[team1]['GA'] += s2
            table[team2]['GF'] += s2
            table[team2]['GA'] += s1
            if s1 > s2:
                table[team1]['W'] += 1
                table[team1]['Pts'] += 3
                table[team2]['L'] += 1
            elif s2 > s1:
                table[team2]['W'] += 1
                table[team2]['Pts'] += 3
                table[team1]['L'] += 1
            else:
                table[team1]['D'] += 1
                table[team2]['D'] += 1
                table[team1]['Pts'] += 1
                table[team2]['Pts'] += 1
    sorted_table = sorted(table.items(), key=lambda x: (x[1]['Pts'], x[1]['GF'] - x[1]['GA'], x[1]['GF']), reverse=True)
    return sorted_table

@app.route("/")
def home():
    return render_template("home.html", groups=groups)

@app.route("/group/<group_id>")
def group(group_id):
    scores = load_scores()
    fixtures = groups[group_id]['fixtures']
    pitch = groups[group_id]['pitch']
    group_scores = scores.get(group_id, {})
    table = calculate_table(fixtures, group_scores) if group_id in ['A', 'B', 'C', 'D'] else None
    return render_template("groupview.html", group_id=group_id, fixtures=fixtures, scores=group_scores, pitch=pitch, table=table)

if __name__ == "__main__":
    app.run(debug=True, port=5001)
