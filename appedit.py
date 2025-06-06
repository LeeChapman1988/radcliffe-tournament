
from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)
DATA_FILE = 'scores.json'

# Base group fixtures
base_groups = {
    'A': {
        'pitch': 'Pitch 1',
        'fixtures': [
            ("1:00 PM", "Tigers", "Galacticos"),
            ("1:20 PM", "Avengers", "13 Devils"),
            ("1:40 PM", "Tigers", "Avengers"),
            ("2:00 PM", "Galacticos", "13 Devils"),
            ("2:20 PM", "Tigers", "13 Devils"),
            ("2:40 PM", "Galacticos", "Avengers")
        ]
    },
    'B': {
        'pitch': 'Pitch 2',
        'fixtures': [
            ("1:00 PM", "Raiders", "Sapphires"),
            ("1:20 PM", "Lightning", "Thunder"),
            ("1:40 PM", "Raiders", "Lightning"),
            ("2:00 PM", "Sapphires", "Thunder"),
            ("2:20 PM", "Raiders", "Thunder"),
            ("2:40 PM", "Sapphires", "Lightning")
        ]
    },
    'C': {
        'pitch': 'Pitch 3',
        'fixtures': [
            ("1:00 PM", "Sonics", "Buzz Bees"),
            ("1:20 PM", "Devils", "Grim Reapers"),
            ("1:40 PM", "Sonics", "Devils"),
            ("2:00 PM", "Buzz Bees", "Grim Reapers"),
            ("2:20 PM", "Sonics", "Grim Reapers"),
            ("2:40 PM", "Buzz Bees", "Devils")
        ]
    },
    'D': {
        'pitch': 'Pitch 4',
        'fixtures': [
            ("1:00 PM", "Gems", "Blazies"),
            ("1:12 PM", "Raptors", "Emeralds"),
            ("1:24 PM", "Gems", "Emeralds 2"),
            ("1:36 PM", "Blazies", "Raptors"),
            ("1:48 PM", "Emeralds", "Emeralds 2"),
            ("2:00 PM", "Gems", "Raptors"),
            ("2:12 PM", "Blazies", "Emeralds"),
            ("2:24 PM", "Gems", "Emeralds"),
            ("2:36 PM", "Blazies", "Emeralds 2"),
            ("2:48 PM", "Raptors", "Emeralds 2")
        ]
    }
}

def load_scores():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_scores(data):
    with open(DATA_FILE, 'w') as f:
        json.dump(data, f)

def safe_int(value):
    try:
        return int(value)
    except (ValueError, TypeError):
        return 0

def calculate_table(fixtures, scores):
    table = {}
    for i, (_, team1, team2) in enumerate(fixtures):
        score = scores.get(str(i))
        table.setdefault(team1, {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'Pts': 0})
        table.setdefault(team2, {'P': 0, 'W': 0, 'D': 0, 'L': 0, 'GF': 0, 'GA': 0, 'Pts': 0})
        if score:
            s1 = safe_int(score.get('home'))
            s2 = safe_int(score.get('away'))
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
    return sorted(table.items(), key=lambda x: (x[1]['Pts'], x[1]['GF'] - x[1]['GA'], x[1]['GF']), reverse=True)

def get_dynamic_groups():
    scores = load_scores()
    groups = dict(base_groups)

    # Calculate winners
    winners = {}
    for gid in ['A', 'B', 'C', 'D']:
        group_scores = scores.get(gid, {})
        table = calculate_table(groups[gid]['fixtures'], group_scores)
        if table:
            winners[gid] = table[0][0]

    # Build semi-finals
    groups['Semi1'] = {
        'pitch': 'Pitch 1',
        'fixtures': [("3:00 PM", winners.get('A', 'TBD'), winners.get('B', 'TBD'))]
    }
    groups['Semi2'] = {
        'pitch': 'Pitch 2',
        'fixtures': [("3:00 PM", winners.get('C', 'TBD'), winners.get('D', 'TBD'))]
    }

    # Final
    semi_scores = scores.get('Semi1', {})
    final_teams = []
    if '0' in semi_scores:
        h = safe_int(semi_scores['0'].get('home'))
        a = safe_int(semi_scores['0'].get('away'))
        final_teams.append(winners.get('A') if h > a else winners.get('B') if a > h else 'TBD')
    semi_scores = scores.get('Semi2', {})
    if '0' in semi_scores:
        h = safe_int(semi_scores['0'].get('home'))
        a = safe_int(semi_scores['0'].get('away'))
        final_teams.append(winners.get('C') if h > a else winners.get('D') if a > h else 'TBD')

    groups['Final'] = {
        'pitch': 'Pitch 1',
        'fixtures': [("3:30 PM", final_teams[0] if len(final_teams) > 0 else 'TBD', final_teams[1] if len(final_teams) > 1 else 'TBD')]
    }

    return groups, scores

@app.route("/")
def home():
    groups, _ = get_dynamic_groups()
    return render_template("home.html", groups=groups)

@app.route("/group/<group_id>")
def group(group_id):
    groups, scores = get_dynamic_groups()
    if group_id not in groups:
        return f"Group '{group_id}' not found", 404

    fixtures = groups[group_id]['fixtures']
    pitch = groups[group_id]['pitch']
    group_scores = scores.get(group_id, {})
    table = calculate_table(fixtures, group_scores) if group_id in ['A', 'B', 'C', 'D'] else None
    return render_template("groupedit.html", group_id=group_id, fixtures=fixtures, scores=group_scores, table=table, pitch=pitch)

@app.route("/submit_score/<group_id>/<int:fixture_index>", methods=["POST"])
def submit_score(group_id, fixture_index):
    scores = load_scores()
    group_scores = scores.get(group_id, {})
    home = request.form.get("home_score", "")
    away = request.form.get("away_score", "")
    group_scores[str(fixture_index)] = {"home": home, "away": away}
    scores[group_id] = group_scores
    save_scores(scores)
    return redirect(url_for("group", group_id=group_id))

@app.route("/scores.json")
def scores_json():
    return jsonify(load_scores())

if __name__ == "__main__":
    app.run(debug=True, port=5000)
