from flask import Flask, render_template_string
import requests
import datetime

app = Flask(__name__)

NBA_URL = "https://site.api.espn.com/apis/v2/sports/basketball/nba/scoreboard"
CBB_URL = "https://site.api.espn.com/apis/v2/sports/basketball/mens-college-basketball/scoreboard"

HTML = '''
<!DOCTYPE html>
<html>
<head>
<title>Scores</title>
<meta http-equiv="refresh" content="30">
<style>
body { font-family: Arial; font-size: 14px; }
.section { margin-bottom: 20px; }
h2 { font-size: 18px; }
</style>
</head>
<body>
<h1>Today's Games</h1>

<div class="section">
<h2>NBA</h2>
{{ nba }}
</div>

<div class="section">
<h2>CBB</h2>
{{ cbb }}
</div>

</body>
</html>
'''

def parse_espn_game(g):
    """Extract team names, scores, rankings, and status."""
    comps = g["competitions"][0]
    status = g["status"]["type"]["shortDetail"]

    lines = []
    for team in comps["competitors"]:
        name = team["team"]["abbreviation"]
        score = team.get("score", "0")
        rank = team["team"].get("rank")
        if rank is not None:
            name = f"#{rank} {name}"
        lines.append((name, score, team["homeAway"]))

    # Order home/away properly
    away = [t for t in lines if t[2] == "away"][0]
    home = [t for t in lines if t[2] == "home"][0]

    return f"{away[0]} {away[1]} @ {home[0]} {home[1]} — {status}<br>"

def get_nba():
    r = requests.get(NBA_URL, headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code != 200:
        return "Error loading NBA games"

    events = r.json().get("events", [])
    if not events:
        return "No games"

    return "".join(parse_espn_game(g) for g in events)

def get_cbb():
    r = requests.get(CBB_URL, headers={"User-Agent": "Mozilla/5.0"})
    if r.status_code != 200:
        return "Error loading CBB games"

    events = r.json().get("events", [])
    if not events:
        return "No games"

    return "".join(parse_espn_game(g) for g in events)

@app.route("/")
def home():
    return render_template_string(HTML, nba=get_nba(), cbb=get_cbb())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
