import os
import json
import requests
import numpy as np
from datetime import datetime
from zoneinfo import ZoneInfo
from scipy.optimize import minimize
from scipy.stats import poisson

API_KEY = os.environ.get("ODDS_API_KEY", "").strip()
ROME_TZ = ZoneInfo("Europe/Rome")

def stima_lambda_da_quote(q1, qx, q2, qo25, qu25):
    p1, px, p2 = 1 / q1, 1 / qx, 1 / q2
    tot_1x2 = p1 + px + p2
    p1, px, p2 = p1 / tot_1x2, px / tot_1x2, p2 / tot_1x2

    po, pu = 1 / qo25, 1 / qu25
    po = po / (po + pu)

    def loss(params):
        la, lb = params
        if la <= 0.1 or lb <= 0.1:
            return 1e6
        m = np.array([[poisson.pmf(i, la) * poisson.pmf(j, lb) for j in range(10)] for i in range(10)])
        m_p1 = sum(m[i, j] for i in range(10) for j in range(10) if i > j)
        m_px = sum(m[i, j] for i in range(10) for j in range(10) if i == j)
        m_po = sum(m[i, j] for i in range(10) for j in range(10) if i + j >= 3)
        return (m_p1 - p1)**2 + (m_px - px)**2 + (m_po - po)**2

    res = minimize(loss, [1.4, 1.2], method="Nelder-Mead")
    la = max(0.3, round(float(res.x), 2))
    lb = max(0.3, round(float(res.x), 2))
    return la, lb

def fetch_palinsesto():
    if not API_KEY:
        raise ValueError("Manca la variabile d'ambiente ODDS_API_KEY")

    # 1. Recupera tutti i campionati di calcio attivi oggi
    sports_url = "https://the-odds-api.com"
    s_resp = requests.get(sports_url, params={"apiKey": API_KEY})
    if s_resp.status_code != 200 or not s_resp.text.strip():
        raise Exception(f"Errore lista sport ({s_resp.status_code}): {s_resp.text[:200]}")

    sports = s_resp.json()
    soccer_keys = [s["key"] for s in sports if s.get("group") == "Soccer" and s.get("active")]
    print(f"Trovati {len(soccer_keys)} campionati di calcio attivi.")

    oggi_italia = datetime.now(ROME_TZ).date()
    palinsesto_pulito = []

    # 2. Scarica le partite di ogni campionato attivo
    for sport_key in soccer_keys:
        odds_url = f"https://the-odds-api.com{sport_key}/odds/"
        params = {
            "apiKey": API_KEY,
            "regions": "eu",
            "markets": "h2h,totals",
            "oddsFormat": "decimal"
        }
        resp = requests.get(odds_url, params=params)
        if resp.status_code != 200 or not resp.text.strip():
            continue

        try:
            raw_matches = resp.json()
        except Exception:
            continue

        for match in raw_matches:
            dt_utc = datetime.fromisoformat(match["commence_time"].replace("Z", "+00:00"))
            dt_it = dt_utc.astimezone(ROME_TZ)

            if dt_it.date() != oggi_italia:
                continue

            home = match["home_team"]
            away = match["away_team"]
            lega = match.get("sport_title", "Calcio")

            q1_list, qx_list, q2_list = [], [], []
            qo25_list, qu25_list = [], []

            for bk in match.get("bookmakers", []):
                for mkt in bk.get("markets", []):
                    key = mkt["key"]
                    outcomes = mkt["outcomes"]
                    if key == "h2h":
                        for o in outcomes:
                            if o["name"] == home: q1_list.append(o["price"])
                            elif o["name"] == away: q2_list.append(o["price"])
                            elif o["name"] == "Draw": qx_list.append(o["price"])
                    elif key == "totals":
                        for o in outcomes:
                            if o.get("point") == 2.5:
                                if o["name"] == "Over": qo25_list.append(o["price"])
                                elif o["name"] == "Under": qu25_list.append(o["price"])

            if not (q1_list and qx_list and q2_list and qo25_list and qu25_list):
                continue

            q1 = round(float(np.mean(q1_list)), 2)
            qx = round(float(np.mean(qx_list)), 2)
            q2 = round(float(np.mean(q2_list)), 2)
            qo25 = round(float(np.mean(qo25_list)), 2)
            qu25 = round(float(np.mean(qu25_list)), 2)

            la, lb = stima_lambda_da_quote(q1, qx, q2, qo25, qu25)

            qgg = round(qo25 * 0.96, 2)
            qob = round(qo25 * 1.18, 2)
            p1x = (1 / q1) + (1 / qx)
            q1x = round(max(1.15, (1 / p1x) * 1.25), 2)

            palinsesto_pulito.append({
                "ora": dt_it.strftime("%H:%M"),
                "lega": lega,
                "m": f"{home} - {away}",
                "la": la,
                "lb": lb,
                "qo25": qo25,
                "qgg": qgg,
                "qob": qob,
                "qu25": qu25,
                "q1x": q1x
            })

    palinsesto_pulito.sort(key=lambda x: x["ora"])

    os.makedirs("data", exist_ok=True)
    output = {
        "aggiornato_il": datetime.now(ROME_TZ).strftime("%d/%m/%Y alle %H:%M"),
        "totale_match": len(palinsesto_pulito),
        "partite": palinsesto_pulito
    }

    with open("data/palinsesto.json", "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=4)

    print(f"Salvati {len(palinsesto_pulito)} match mondiali per oggi.")

if __name__ == "__main__":
    fetch_palinsesto()
