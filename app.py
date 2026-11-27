import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA OTTIMIZZATA PER TABLET ---
st.set_page_config(page_title="G8 Quant & Solid Value", page_icon="⚽", layout="wide")

st.title("📱 SUITE ANALITICA — G8 QUANT & SOLID VALUE")
st.markdown("Motore di smistamento automatico con **Distribuzione di Poisson**, **xG** e **Gestione Cassa**.")

# --- PALINSESTO UNICO DEL GIORNO (LE QUOTE VENGONO ANALIZZATE IN AUTOMATICO DA ENTRAMBI I METODI) ---
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
    st.session_state.partite_db = [dict(x) for x in DATI_DEFAULT]

# --- FUNZIONE MATEMATICA DI POISSON COMPLETA ---
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

# --- PANNELLO TOUCH-SCREEN UNIFICATO ---
with st.expander("✏️ GESTISCI PALINSESTO DEL GIORNO (SMISTAMENTO AUTOMATICO)", expanded=False):
    st.caption("Inserisci o modifica le partite: l'app le smisterà in automatico nel Metodo 1 o nel Metodo 2 in base ai gol attesi e alle quote.")
    
    df_edit = pd.DataFrame(st.session_state.partite_db)
    edited_df = st.data_editor(df_edit, num_rows="dynamic", use_container_width=True)
    st.session_state.partite_db = edited_df.to_dict("records")
    
    col_b1, col_b2 = st.columns(2)
    if col_b1.button("🔄 Ripristina lista base"):
        st.session_state.partite_db = [dict(x) for x in DATI_DEFAULT]
        st.rerun()
    if col_b2.button("🗑️ Svuota tutto"):
        st.session_state.partite_db = []
        st.rerun()

# --- IMPOSTAZIONI CASSA E ORARI ---
st.sidebar.header("⚙️ Controlli Rapidi")
cassa_iniziale = st.sidebar.number_input("Cassa di partenza (€)", min_value=5.0, value=10.0, step=5.0)
ora_partenza = st.sidebar.slider("Partenza scalata dalle ore:", 12, 18, 14)

# --- ELABORAZIONE AUTOMATICA DI ENTRAMBI I METODI ---
vietate = ["U19", "U21", "U23", "Primavera", "Reserves", "Amichevole"]
validi_g8 = []
validi_solid = []

for p in st.session_state.partite_db:
    if not p.get("match") or not p.get("orario"):
        continue
    if any(v.lower() in str(p.get("lega", "")).lower() or v.lower() in str(p.get("match", "")).lower() for v in vietate):
        continue
    try:
        ora_obj = datetime.strptime(str(p["orario"]), "%H:%M")
    except:
        continue

    la = float(p.get("lambda_a", 0))
    lb = float(p.get("lambda_b", 0))
    l_tot = la + lb
    simm = abs(la - lb)
    probs = calcola_matrice_poisson(la, lb)

    # 1. VALUTAZIONE AUTOMATICA PER METODO 1: G8 QUANT (Pure Goals)
    if ora_obj.hour >= ora_partenza and l_tot >= 3.00 and simm <= 0.75:
        candidati_g8 = [
            ("Over 2.5", float(p.get("q_over25", 0))),
            ("Goal (BTTS)", float(p.get("q_btts", 0))),
            ("Over 2.5 + Goal", float(p.get("q_o25_btts", 0))),
            ("Multigol 2-4", float(p.get("q_mg24", 0)))
        ]
        miglior_g8 = None
        for nome_m, quota_m in candidati_g8:
            if 1.70 <= quota_m <= 2.05:
                p_reale = probs[nome_m]
                p_impl = round((1 / quota_m) * 100, 1)
                edge = round(p_reale - p_impl, 1)
                if edge > 1.5 and (miglior_g8 is None or edge > miglior_g8["Edge"]):
                    miglior_g8 = {
                        "ora_obj": ora_obj, "Orario": p["orario"], "Competizione": p["lega"],
                        "Partita": p["match"], "Esito Pure Goals": nome_m, "Quota": quota_m,
                        "Stake": "5/5" if edge >= 4.0 else "4/5",
                        "Prob_Reale": p_reale, "Prob_Implicita": p_impl, "Edge": edge
                    }
        if miglior_g8:
            validi_g8.append(miglior_g8)

    # 2. VALUTAZIONE AUTOMATICA PER METODO 2: SOLID VALUE (Tattico & Combo)
    if l_tot <= 2.65:
        candidati_solid = [
            ("Under 2.5", float(p.get("q_under25", 0))),
            ("1X + Under 3.5", float(p.get("q_1x_u35", 0))),
            ("X2 + Multigol 1-3", float(p.get("q_x2_mg13", 0)))
        ]
        miglior_solid = None
        for nome_s, quota_s in candidati_solid:
            if 1.65 <= quota_s <= 2.00:
                p_reale = probs[nome_s]
                p_impl = round((1 / quota_s) * 100, 1)
                edge = round(p_reale - p_impl, 1)
                if edge > 1.0 and (miglior_solid is None or edge > miglior_solid["Edge"]):
                    b = quota_s - 1
                    q_prob = 1 - (p_reale / 100)
                    kelly = max(0, round((((b * (p_reale / 100)) - q_prob) / b) * 25, 1))
                    miglior_solid = {
                        "Orario": p["orario"], "Competizione": p["lega"], "Partita": p["match"],
                        "Esito Solid": nome_s, "Quota": quota_s,
                        "Prob. Reale vs Implicita": f"{p_reale}% vs {p_impl}% (+{edge}%)",
                        "Stake Kelly Consigliato": f"{kelly}% della cassa",
                        "Edge": edge
                    }
        if miglior_solid:
            validi_solid.append(miglior_solid)

# --- VISUALIZZAZIONE SCHEDE ---
tab1, tab2 = st.tabs([
    f"⚽ METODO 1: G8 QUANT ({len(validi_g8)} trovate)",
    f"🛡️ METODO 2: SOLID VALUE ({len(validi_solid)} trovate)"
])

with tab1:
    st.subheader("Algoritmo Pure Goals & Scalata Sequenziale")
    st.caption("Seleziona in automatico le partite con Lambda Tot >= 3.00, Simmetria <= 0.75 e Quota 1.70 - 2.05 senza sovrapposizioni.")
    
    validi_g8.sort(key=lambda x: x["ora_obj"])
    scalata, riserve, checkpoints = [], [], []
    ultimo_inizio = None
    cassa_corr = cassa_iniziale
    
    for r in validi_g8:
        if ultimo_inizio is None or (r["ora_obj"] - ultimo_inizio) >= timedelta(hours=2):
            if len(scalata) < 5:
                ora_fine = (r["ora_obj"] + timedelta(minutes=115)).strftime("%H:%M")
                ora_check = (r["ora_obj"] - timedelta(minutes=45)).strftime("%H:%M")
                nuova_cassa = round(cassa_corr * r["Quota"], 2)
                step_num = len(scalata) + 1
                
                scalata.append({
                    "Step": step_num,
                    "Orario (Inizio/Fine)": f"{r['Orario']} - {ora_fine}",
                    "Competizione": r["Competizione"],
                    "Partita": r["Partita"],
                    "Esito Pure Goals": r["Esito Pure Goals"],
                    "Quota": r["Quota"],
                    "Stake": r["Stake"],
                    "Prob. Reale vs Implicita": f"{r['Prob_Reale']}% vs {r['Prob_Implicita']}% (+{r['Edge']}%)",
                    "Progressione Cassa": f"{cassa_corr:.2f} € -> {nuova_cassa:.2f} €"
                })
                checkpoints.append(f"⏰ **Check-Point Step {step_num} ({ora_check})** → Verifica formazioni per *{r['Partita']}* (inizio ore {r['Orario']})")
