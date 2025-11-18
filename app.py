from flask import Flask, jsonify
import requests

app = Flask(__name__)

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://www.espn.com/"
}

def fetch_espn(scoreboard_url):
    try:
        response = requests.get(scoreboard_url, headers=HEADERS, timeout=10)
        response.raise_for_status()  # throws error if not 200
        data = response.json()

        games = []

        # ESPN scoreboard uses "events"
        for event in data.get("events", []):
            competition = event.get("competitions", [{}])[0]

            # competitors = teams in the game
            competitors = competition.get("competitors", [])

            if len(competitors) == 2:
                team1 = competitors[0]
                team2 = competitors[1]

                games.append({
                    "home": team1["team"]["displayName"],
                    "home_score": team1.get("score"),
                    "away": team2["team"]["displayName"],
                    "away_score": team2.get("score"),
                    "status": event.get("status", {}).get("type", {}).get("shortDetail")
                })

        return games

    except Exception as e:
        print("Fetch error:", e)
        return []

@app.route("/nba")
def nba_games():
    url = "https://site.api.espn.com/apis/v2/sports/basketball/nba/scoreboard"
    games = fetch_espn(url)
    return jsonify({"games": games})

@app.route("/cbb")
def cbb_games():
    url = "https://site.api.espn.com/apis/v2/sports/basketball/mens-college-basketball/scoreboard"
    games = fetch_espn(url)
    return jsonify({"games": games})

@app.route("/")
def home():
    return jsonify({"status": "API is running"})


# Needed for Render
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
