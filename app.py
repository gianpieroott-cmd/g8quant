import streamlit as st
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta

from PIL import Image
st.set_page_config(page_title="G8 Quant Stadium Pro", page_icon=Image.open("icona.png"), layout="wide")


st.markdown("""
<style>
.stApp { background: radial-gradient(circle at top, #113829 0%, #09151e 50%, #060b13 100%); color: #fff; }
#MainMenu, footer { visibility: hidden; }
.hero { background: linear-gradient(135deg, rgba(16,185,129,0.25), rgba(14,165,233,0.25)); border: 1px solid #34d399; border-radius: 16px; padding: 18px; margin-bottom: 16px; }
.hero h1 { font-size: 1.9rem; font-weight: 900; color: #34d399; margin: 0; }
.kpi { background: rgba(15,23,42,0.85); border: 1px solid rgba(255,255,255,0.15); border-radius: 14px; padding: 12px; text-align: center; }
.kpi-t { color: #94a3b8; font-size: 0.75rem; font-weight: 700; text-transform: uppercase; }
.kpi-v { color: #fbbf24; font-size: 1.55rem; font-weight: 900; }
.sec-g8 { background: linear-gradient(90deg, #059669, rgba(5,150,105,0.1)); border-left: 6px solid #34d399; padding: 10px 16px; border-radius: 8px; margin: 18px 0 12px 0; font-weight: 800; font-size: 1.15rem; }
.sec-so { background: linear-gradient(90deg, #0284c7, rgba(2,132,199,0.1)); border-left: 6px solid #38bdf8; padding: 10px 16px; border-radius: 8px; margin: 20px 0 12px 0; font-weight: 800; font-size: 1.15rem; }
.card-g8 { background: rgba(16,48,38,0.92); border: 1px solid #34d399; border-left: 7px solid #10b981; border-radius: 12px; padding: 15px; margin-bottom: 10px; }
.card-so { background: rgba(14,38,66,0.92); border: 1px solid #38bdf8; border-left: 7px solid #0ea5e9; border-radius: 12px; padding: 15px; margin-bottom: 10px; }
.b-g8 { background: #10b981; color: #022c22; font-weight: 900; font-size: 0.75rem; padding: 3px 10px; border-radius: 12px; }
.b-so { background: #38bdf8; color: #082f49; font-weight: 900; font-size: 0.75rem; padding: 3px 10px; border-radius: 12px; }
.q-box { background: #fbbf24; color: #000; padding: 3px 10px; border-radius: 6px; font-weight: 900; }
</style>
<div class="hero"><h1>⚽ G8 QUANT STADIUM PRO</h1><div>Motore Matematico Poisson • Smistamento Automatico • Due Strategie Distinte</div></div>
""", unsafe_allow_html=True)

DATI = [
    {"ora": "15:20", "lega": "Saudi Pro League", "m": "Al-Qadsiah - Al-Fayha", "la": 1.85, "lb": 1.35, "qo25": 1.75, "qgg": 1.72, "qob": 2.05, "qu25": 2.05, "q1x": 1.70},
    {"ora": "16:00", "lega": "Serie B", "m": "Bari - Catanzaro", "la": 1.25, "lb": 0.95, "qo25": 2.15, "qgg": 1.95, "qob": 2.50, "qu25": 1.68, "q1x": 1.72},
    {"ora": "18:00", "lega": "Ligue 1", "m": "Nantes - Le Havre", "la": 1.15, "lb": 0.90, "qo25": 2.25, "qgg": 2.05, "qob": 2.65, "qu25": 1.70, "q1x": 1.68},
    {"ora": "18:30", "lega": "Saudi Pro League", "m": "Al-Ittihad - NEOM SC", "la": 2.05, "lb": 1.45, "qo25": 1.60, "qgg": 1.65, "qob": 1.85, "qu25": 2.30, "q1x": 1.95},
    {"ora": "20:30", "lega": "Bundesliga", "m": "Werder Bremen - B. M'gladbach", "la": 1.95, "lb": 1.55, "qo25": 1.58, "qgg": 1.60, "qob": 1.80, "qu25": 2.35, "q1x": 2.10},
    {"ora": "20:45", "lega": "Serie A", "m": "Venezia - Bologna", "la": 1.45, "lb": 1.60, "qo25": 1.85, "qgg": 1.78, "qob": 2.15, "qu25": 1.95, "q1x": 2.15},
    {"ora": "21:00", "lega": "La Liga", "m": "Getafe - Osasuna", "la": 1.10, "lb": 1.05, "qo25": 2.35, "qgg": 2.10, "qob": 2.75, "qu25": 1.62, "q1x": 1.75},
    {"ora": "23:55", "lega": "Brasileirao", "m": "Fluminense - Cruzeiro", "la": 1.80, "lb": 1.40, "qo25": 1.82, "qgg": 1.75, "qob": 2.10, "qu25": 1.98, "q1x": 1.85}
]

def poisson_calc(la, lb):
    m = np.array([[poisson.pmf(i, la)*poisson.pmf(j, lb) for j in range(10)] for i in range(10)])
    return {
        "Over 2.5": round(sum(m[i,j] for i in range(10) for j in range(10) if i+j>=3)*100, 1),
        "Goal (BTTS)": round(sum(m[i,j] for i in range(1,10) for j in range(1,10))*100, 1),
        "Over 2.5 + Goal": round(sum(m[i,j] for i in range(1,10) for j in range(1,10) if i+j>=3)*100, 1),
        "Under 2.5": round(sum(m[i,j] for i in range(10) for j in range(10) if i+j<=2)*100, 1),
        "1X + Under 3.5": round(sum(m[i,j] for i in range(10) for j in range(10) if i>=j and i+j<=3)*100, 1)
    }

c1, c2, c3 = st.columns(3)
cassa = c1.number_input("💰 Budget (€)", 5.0, 1000.0, 10.0, 5.0)
ora_min = c2.slider("⏰ Ora Partenza", 12, 18, 14)
filtro = c3.selectbox("🎯 Mostra:", ["Entrambi i Metodi", "Solo G8 Quant (Verde)", "Solo Solid Value (Blu)"])

g8, solid = [], []
for p in DATI:
    t = datetime.strptime(p["ora"], "%H:%M")
    ltot, sim = p["la"] + p["lb"], abs(p["la"] - p["lb"])
    pr = poisson_calc(p["la"], p["lb"])
    if t.hour >= ora_min and ltot >= 3.00 and sim <= 0.75:
        for es, q in [("Over 2.5", p["qo25"]), ("Goal (BTTS)", p["qgg"]), ("Over 2.5 + Goal", p["qob"])]:
            if 1.70 <= q <= 2.05 and (pr[es] - round(100/q, 1)) > 1.5:
                g8.append({"t": t, "ora": p["ora"], "lega": p["lega"], "m": p["m"], "es": es, "q": q, "pr": pr[es], "pi": round(100/q, 1), "ed": round(pr[es]-100/q, 1), "xg": round(ltot, 2)})
                break
    if ltot <= 2.65:
        for es, q in [("Under 2.5", p["qu25"]), ("1X + Under 3.5", p["q1x"])]:
            if 1.65 <= q <= 2.00 and (pr[es] - round(100/q, 1)) > 1.0:
                b = q - 1
                kelly = max(0, round((((b*(pr[es]/100))-(1-pr[es]/100))/b)*25, 1))
                solid.append({"ora": p["ora"], "lega": p["lega"], "m": p["m"], "es": es, "q": q, "pr": pr[es], "pi": round(100/q, 1), "ed": round(pr[es]-100/q, 1), "kelly": kelly, "xg": round(ltot, 2)})
                break

g8.sort(key=lambda x: x["t"])
scalata, last_t, curr = [], None, cassa
for r in g8:
    if last_t is None or (r["t"] - last_t) >= timedelta(hours=2):
        if len(scalata) < 5:
            nxt = round(curr * r["q"], 2)
            r.update({"step": len(scalata)+1, "c1": curr, "c2": nxt})
            scalata.append(r)
            curr, last_t = nxt, r["t"]

k1, k2, k3, k4 = st.columns(4)
k1.markdown(f'<div class="kpi"><div class="kpi-t">💰 Budget</div><div class="kpi-v">{cassa:.2f} €</div></div>', unsafe_allow_html=True)
k2.markdown(f'<div class="kpi"><div class="kpi-t">🏆 Finale G8</div><div class="kpi-v">{curr:.2f} €</div></div>', unsafe_allow_html=True)
k3.markdown(f'<div class="kpi"><div class="kpi-t">🔥 G8 Quant</div><div class="kpi-v">{len(scalata)} Step</div></div>', unsafe_allow_html=True)
k4.markdown(f'<div class="kpi"><div class="kpi-t">🛡️ Solid Value</div><div class="kpi-v">{len(solid)} Match</div></div>', unsafe_allow_html=True)

if filtro in ["Entrambi i Metodi", "Solo G8 Quant (Verde)"]:
    st.markdown('<div class="sec-g8">🔥 METODO 1: G8 QUANT — SCALATA PURE GOALS (4 Step • xG ≥ 3.00)</div>', unsafe_allow_html=True)
    for s in scalata:
        st.markdown(f'<div class="card-g8"><span class="b-g8">🟢 G8 QUANT • STEP {s["step"]}</span> &nbsp; ⏱️ <b>{s["ora"]}</b> | 🏆 {s["lega"]} (xG: {s["xg"]})<h3 style="margin:6px 0;">⚽ {s["m"]}</h3>🎯 <b>{s["es"]}</b> &nbsp; <span class="q-box">@ {s["q"]:.2f}</span> &nbsp; | &nbsp; Reale: <b>{s["pr"]}%</b> vs Imp: {s["pi"]}% (+{s["ed"]}%) &nbsp; | &nbsp; 💸 <b>{s["c1"]:.2f} € ➔ {s["c2"]:.2f} €</b></div>', unsafe_allow_html=True)

if filtro in ["Entrambi i Metodi", "Solo Solid Value (Blu)"]:
    st.markdown('<div class="sec-so">🛡️ METODO 2: SOLID VALUE — SINGOLE TATTICHE (Match Chiusi • xG ≤ 2.65)</div>', unsafe_allow_html=True)
    for s in solid:
        st.markdown(f'<div class="card-so"><span class="b-so">🔵 SOLID VALUE • SINGOLA</span> &nbsp; ⏱️ <b>{s["ora"]}</b> | 🏆 {s["lega"]} (xG: {s["xg"]})<h3 style="margin:6px 0;">⚽ {s["m"]}</h3>🛡️ <b>{s["es"]}</b> &nbsp; <span class="q-box">@ {s["q"]:.2f}</span> &nbsp; | &nbsp; Reale: <b>{s["pr"]}%</b> vs Imp: {s["pi"]}% (+{s["ed"]}%) &nbsp; | &nbsp; 📊 Stake Kelly: <b>{s["kelly"]}%</b></div>', unsafe_allow_html=True)

with st.expander("📖 GUIDA RAPIDA AI DUE METODI"):
    st.markdown("""
    * **🟢 Metodo 1 (G8 Quant — Verde):** Seleziona solo partite molto offensive (**xG ≥ 3.00**) distanziate di almeno 2 ore per costruire una scalata progressiva su *Over 2.5*, *Goal* e *Over 2.5 + Goal*.
    * **🔵 Metodo 2 (Solid Value — Blu):** Isola le partite tattiche ed equilibrate (**xG ≤ 2,65**) calcolando la puntata ideale con il **Criterio di Kelly** su *Under 2.5* e *1X + Under 3.5*.
    """)
