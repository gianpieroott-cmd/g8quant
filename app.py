 

import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="G8 Quant Pro", page_icon="⚡", layout="wide")

# --- DESIGN PERSONALIZZATO (CSS DARK PRO & CARD MODERNE) ---
st.markdown("""
<style>
    .stApp {
        background-color: #0b0f19;
        color: #f1f5f9;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    .main-title {
        font-size: 2.1rem;
        font-weight: 800;
        background: linear-gradient(90deg, #10b981, #3b82f6);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px;
    }
    .sub-title {
        color: #94a3b8;
        font-size: 0.95rem;
        margin-bottom: 25px;
    }
    
    /* Card KPI in alto */
    .kpi-box {
        background: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 16px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.3);
    }
    .kpi-label {
        color: #94a3b8;
        font-size: 0.8rem;
        text-transform: uppercase;
        letter-spacing: 1px;
    }
    .kpi-value {
        color: #10b981;
        font-size: 1.6rem;
        font-weight: 800;
        margin-top: 4px;
    }
    
    /* Card singola partita (Step) */
    .match-card {
        background: linear-gradient(145deg, #131b2e, #0f172a);
        border-left: 5px solid #10b981;
        border-top: 1px solid #1e293b;
        border-right: 1px solid #1e293b;
        border-bottom: 1px solid #1e293b;
        border-radius: 12px;
        padding: 18px;
        margin-bottom: 14px;
        box-shadow: 0 6px 20px rgba(0,0,0,0.35);
    }
    .match-card-solid {
        border-left: 5px solid #3b82f6;
    }
    .card-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 8px;
    }
    .step-badge {
        background-color: rgba(16, 185, 129, 0.15);
        color: #10b981;
        padding: 4px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
    }
    .step-badge-blue {
        background-color: rgba(59, 130, 246, 0.15);
        color: #60a5fa;
    }
    .league-tag {
        color: #94a3b8;
        font-size: 0.85rem;
        font-weight: 600;
    }
    .match-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #ffffff;
        margin: 6px 0;
    }
    .card-grid {
        display: flex;
        flex-wrap: wrap;
        gap: 12px;
        margin-top: 12px;
        padding-top: 12px;
        border-top: 1px solid #1e293b;
        justify-content: space-between;
        align-items: center;
    }
    .market-pill {
        background-color: #1e293b;
        color: #f8fafc;
        padding: 6px 14px;
        border-radius: 8px;
        font-weight: 700;
        font-size: 0.95rem;
    }
    .odds-pill {
        background-color: #10b981;
        color: #064e3b;
        padding: 6px 14px;
        border-radius: 8px;
        font-weight: 800;
        font-size: 1rem;
    }
    .odds-pill-blue {
        background-color: #3b82f6;
        color: #eff6ff;
    }
    .stats-text {
        color: #cbd5e1;
        font-size: 0.88rem;
    }
    .cash-flow {
        color: #fbbf24;
        font-weight: 700;
        font-size: 0.95rem;
    }
    
    /* Box Guida */
    .guide-box {
        background: #131b2e;
        border: 1px solid #1e293b;
        border-radius: 14px;
        padding: 22px;
        margin-bottom: 16px;
        line-height: 1.6;
    }
    .guide-title {
        color: #10b981;
        font-size: 1.2rem;
        font-weight: 700;
        margin-bottom: 10px;
    }
    .guide-title-blue {
        color: #60a5fa;
    }
</style>
""", unsafe_allow_html=True)

# --- INTESTAZIONE ---
st.markdown('<div class="main-title">⚡ G8 QUANT PRO — ANALYTICS SUITE</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Motore Matematico Poisson • Smistamento Automatico • Gestione Progressione</div>', unsafe_allow_html=True)

# --- PALINSESTO UNICO DEL GIORNO ---
DATI_DEFAULT = [
    {"orario": "15:20", "lega": "Saudi Pro League", "match": "Al-Qadsiah - Al-Fayha", "lambda_a": 1.85, "lambda_b": 1.35, "q_over25": 1.75, "q_btts": 1.72, "q_o25_btts": 2.05, "q_mg24": 1.55, "q_under25": 2.05, "q_1x_u35": 1.70, "q_x2_mg13": 2.30},
    {"orario": "16:00", "lega": "Serie B", "match": "Bari - Catanzaro", "lambda_a": 1.25, "lambda_b": 0.95, "q_over25": 2.15, "q_btts": 1.95, "q_o25_btts": 2.50, "q_mg24": 1.60, "q_under25": 1.68, "q_1x_u35": 1.72, "q_x2_mg13": 2.10},
    {"orario": "18:00", "lega": "Ligue 1", "match": "Nantes - Le Havre", "lambda_a": 1.15, "lambda_b": 0.90, "q_over25": 2.25, "q_btts": 2.05, "q_o25_btts": 2.65, "q_mg24": 1.65, "q_under25": 1.70, "q_1x_u35": 1.68, "q_x2_mg13": 2.05},
    {"orario": "18:30", "lega": "Saudi Pro League", "match": "Al-Ittihad - NEOM SC", "lambda_a": 2.05, "lambda_b": 1.45, "q_over25": 1.60, "q_btts": 1.65, "q_o25_btts": 1.85, "q_mg24": 1.52, "q_under25": 2.30, "q_1x_u35": 1.95, "q_x2_mg13": 2.60},
    {"orario": "20:30", "lega": "Bundesliga", "match": "Werder Bremen - B. M'gladbach", "lambda_a": 1.95, "lambda_b": 1.55, "q_over25": 1.58, "q_btts": 1.60, "q_o25_btts": 1.80, "q_mg24": 1.55, "q_under25": 2.35, "q_1x_u35": 2.10, "q_x2_mg13": 2.40},
    {"orario": "20:45", "lega": "Serie A", "match": "Venezia - Bologna", "lambda_a": 1.45, "lambda_b": 1.60, "q_over25": 1.85, "q_btts": 1.78, "q_o25_btts": 2.15, "q_mg24": 1.52, "q_under25": 1.95, "q_1x_u35": 2.15, "q_x2_mg13": 1.85},
    {"orario": "21:00", "lega": "La Liga", "match": "Getafe - Osasuna", "lambda_a": 1.10, "lambda_b": 1.05, "q_over25": 2.35, "q_btts": 2.10, "q_o25_btts": 2.75, "q_mg24": 1.68, "q_under25": 1.62, "q_1x_u35": 1.75, "q_x2_mg13": 1.82},
    {"orario": "23:55", "lega": "Brasileirao", "match": "Fluminense - Cruzeiro", "lambda_a": 1.80, "lambda_b": 1.40, "q_over25": 1.82, "q_btts": 1.75, "q_o25_btts": 2.10, "q_mg24": 1.50, "q_under25": 1.98, "q_1x_u35": 1.85, "q_x2_mg13": 2.25}
]

if "partite_db" not in st.session_state:
    st.session_state.partite_db = list(DATI_DEFAULT)

def calcola_matrice_poisson(lambda_a, lambda_b):
    max_gol = 10
    m = np.zeros((max_gol, max_gol))
    for i in range(max_gol):
        for j in range(max_gol):
            m[i, j] = poisson.pmf(i, lambda_a) * poisson.pmf(j, lambda_b)
            
    p_over25 = sum(m[i, j] for i in range(max_gol) for j in range(max_gol) if i + j >= 3)
    p_btts = sum(m[i, j] for i in range(1, max_gol) for j in range(1, max_gol))
    p_over25_btts = sum(m[i, j] for i in range(1, max_gol) for j in range(1, max_gol) if i + j >= 3)
    p_mg24 = sum(m[i, j] for i in range(max_gol) for j in range(max_gol) if 2 <= (i + j) <= 4)
    p_under25 = sum(m[i, j] for i in range(max_gol) for j in range(max_gol) if i + j <= 2)
    p_1x_u35 = sum(m[i, j] for i in range(max_gol) for j in range(max_gol) if i >= j and (i + j) <= 3)
    p_x2_mg13 = sum(m[i, j] for i in range(max_gol) for j in range(max_gol) if i <= j and 1 <= (i + j) <= 3)
    
    return {
        "Over 2.5": round(p_over25 * 100, 1),
        "Goal (BTTS)": round(p_btts * 100, 1),
        "Over 2.5 + Goal": round(p_over25_btts * 100, 1),
        "Multigol 2-4": round(p_mg24 * 100, 1),
        "Under 2.5": round(p_under25 * 100, 1),
        "1X + Under 3.5": round(p_1x_u35 * 100, 1),
        "X2 + Multigol 1-3": round(p_x2_mg13 * 100, 1)
    }

# --- BARRA PARAMETRI RAPIDI IN ALTO ---
c_set1, c_set2, c_set3 = st.columns([1, 1, 2])
cassa_iniziale = c_set1.number_input("💰 Cassa Iniziale (€)", min_value=5.0, value=10.0, step=5.0)
ora_partenza = c_set2.slider("⏰ Ora Partenza", 12, 18, 14)

with c_set3:
    st.write("")
    with st.expander("➕ Aggiungi Nuova Partita al Palinsesto"):
        with st.form("aggiungi_form", clear_on_submit=True):
            f1, f2, f3 = st.columns(3)
            f_ora = f1.text_input("Orario", "20:45")
            f_lega = f2.text_input("Lega", "Serie A")
            f_match = f3.text_input("Match", "Roma - Lazio")
            
            f4, f5 = st.columns(2)
            f_la = f4.number_input("xG Casa (Lambda A)", 0.2, 4.5, 1.65, 0.05)
            f_lb = f5.number_input("xG Ospite (Lambda B)", 0.2, 4.5, 1.50, 0.05)
            
            q1, q2, q3, q4 = st.columns(4)
            q_o25 = q1.number_input("Q. Over 2.5", 1.10, 5.0, 1.80, 0.05)
            q_gg = q2.number_input("Q. Goal", 1.10, 5.0, 1.75, 0.05)
            q_u25 = q3.number_input("Q. Under 2.5", 1.10, 5.0, 1.95, 0.05)
            q_1xu35 = q4.number_input("Q. 1X+U3.5", 1.10, 5.0, 1.80, 0.05)
            
            if st.form_submit_button("Salva e Calcola"):
                st.session_state.partite_db.append({
                    "orario": f_ora, "lega": f_lega, "match": f_match,
                    "lambda_a": f_la, "lambda_b": f_lb,
                    "q_over25": q_o25, "q_btts": q_gg, "q_o25_btts": 2.15, "q_mg24": 1.55,
                    "q_under25": q_u25, "q_1x_u35": q_1xu35, "q_x2_mg13": 2.00
                })
                st.rerun()

# --- SMISTAMENTO AUTOMATICO ---
validi_g8 = []
validi_solid = []

for p in st.session_state.partite_db:
    ora_obj = datetime.strptime(p["orario"], "%H:%M")
    la, lb = p["lambda_a"], p["lambda_b"]
    l_tot = la + lb
    simm = abs(la - lb)
    probs = calcola_matrice_poisson(la, lb)

    if ora_obj.hour >= ora_partenza and l_tot >= 3.00 and simm <= 0.75:
        for nome_m, quota_m in [("Over 2.5", p["q_over25"]), ("Goal (BTTS)", p["q_btts"]), ("Over 2.5 + Goal", p["q_o25_btts"]), ("Multigol 2-4", p["q_mg24"])]:
            if 1.70 <= quota_m <= 2.05:
                p_reale = probs[nome_m]
                p_impl = round((1 / quota_m) * 100, 1)
                edge = round(p_reale - p_impl, 1)
                if edge > 1.5:
                    validi_g8.append({
