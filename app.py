from flask import Flask, render_template_string
import requests
import datetime

app = Flask(__name__)

NBA_URL = "https://www.balldontlie.io/api/v1/games"
CBB_URL = "https://api.collegebasketballdata.com/games"

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
{{ nba|safe }}
</div>

<div class="section">
<h2>CBB</h2>
{{ cbb|safe }}
</div>

</body>
</html>
'''

def get_nba():
    today = datetime.date.today().isoformat()
    r = requests.get(NBA_URL, params={"dates[]": today, "per_page": 100})
    if r.status_code != 200:
        return "Error loading NBA games"

    games = r.json().get("data", [])
    if not games:
        return "No games today"

    out = ""
    for g in games:
        home = g['home_team']['abbreviation']
        away = g['visitor_team']['abbreviation']
        hs = g['home_team_score']
        vs = g['visitor_team_score']
        status = g['status']
        out += f"{away} {vs} @ {home} {hs} — {status}<br>"
    return out

def get_cbb():
    today = datetime.date.today().isoformat()
    headers = {"accept": "application/json"}
    r = requests.get(CBB_URL, params={"date": today}, headers=headers)

    if r.status_code != 200:
        return "Error loading CBB games"

    games = r.json()
    if not games:
        return "No CBB games today"

    out = ""
    for g in games:
        home = g['home']['market']
        away = g['away']['market']
        hs = g.get('home_points', '')
        vs = g.get('away_points', '')
        out += f"{away} {vs} @ {home} {hs}<br>"
    return out

@app.route("/")
def home():
    return render_template_string(HTML, nba=get_nba(), cbb=get_cbb())

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
