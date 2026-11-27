import streamlit as st
import pandas as pd
import numpy as np
from scipy.stats import poisson
from datetime import datetime, timedelta

# --- CONFIGURAZIONE PAGINA OTTIMIZZATA PER TABLET ---
st.set_page_config(page_title="G8 Quant & Solid Value", page_icon="⚽", layout="wide")

st.title("📱 SUITE ANALITICA — G8 QUANT & SOLID VALUE")
st.markdown("Motore di calcolo statistico con **Distribuzione di Poisson**, **xG** e **Gestione Cassa**.")

# --- INIZIALIZZAZIONE MEMORIA PARTITE (PER INSERIMENTO DA TABLET) ---
if "partite_db" not in st.session_state:
    st.session_state.partite_db = [
        {"orario": "15:20", "lega": "Saudi Pro League", "match": "Al-Qadsiah - Al-Fayha", "lambda_a": 1.85, "lambda_b": 1.35, "mercato": "Over 2.5", "quota": 1.75},
        {"orario": "18:30", "lega": "Saudi Pro League", "match": "Al-Ittihad - NEOM SC", "lambda_a": 2.05, "lambda_b": 1.45, "mercato": "Over 2.5 + Goal", "quota": 1.85},
        {"orario": "20:30", "lega": "Bundesliga", "match": "Werder Bremen - B. M'gladbach", "lambda_a": 1.95, "lambda_b": 1.55, "mercato": "Over 2.5 + Goal", "quota": 1.80},
        {"orario": "20:45", "lega": "Serie A", "match": "Venezia - Bologna", "lambda_a": 1.45, "lambda_b": 1.60, "mercato": "Goal (BTTS)", "quota": 1.78},
        {"orario": "23:55", "lega": "Brasileirao", "match": "Fluminense - Cruzeiro", "lambda_a": 1.80, "lambda_b": 1.40, "mercato": "Goal (BTTS)", "quota": 1.75},
        {"orario": "16:00", "lega": "Serie B", "match": "Bari - Catanzaro", "lambda_a": 1.25, "lambda_b": 0.95, "mercato": "1X + Under 3.5", "quota": 1.72},
        {"orario": "18:00", "lega": "Ligue 1", "match": "Nantes - Le Havre", "lambda_a": 1.15, "lambda_b": 0.90, "mercato": "Under 2.5", "quota": 1.70},
        {"orario": "21:00", "lega": "La Liga", "match": "Getafe - Osasuna", "lambda_a": 1.10, "lambda_b": 1.05, "mercato": "X2 + Multigol 1-3", "quota": 1.82}
    ]

# --- FUNZIONE MATEMATICA DI POISSON COMPLETA ---
def calcola_matrice_poisson(lambda_a, lambda_b):
    max_gol = 10
    m = np.zeros((max_gol, max_gol))
    for i in range(max_gol):
        for j in range(max_gol):
            m[i, j] = poisson.pmf(i, lambda_a) * poisson.pmf(j, lambda_b)
            
    # Mercati Metodo 1: G8 Quant (Pure Goals)
    p_over25 = sum(m[i, j] for i in range(max_gol) for j in range(max_gol) if i + j >= 3)
    p_btts = sum(m[i, j] for i in range(1, max_gol) for j in range(1, max_gol))
    p_over25_btts = sum(m[i, j] for i in range(1, max_gol) for j in range(1, max_gol) if i + j >= 3)
    p_mg24 = sum(m[i, j] for i in range(max_gol) for j in range(max_gol) if 2 <= (i + j) <= 4)
    
    # Mercati Metodo 2: Solid Value (Tattico & Combo)
    p_under25 = sum(m[i, j] for i in range(max_gol) for j in range(max_gol) if i + j <= 2)
    p_1x_u35 = sum(m[i, j] for i in range(max_gol) for j in range(max_gol) if i >= j and (i + j) <= 3)
    p_x2_mg13 = sum(m[i, j] for i in range(max_gol) for j in range(max_gol) if i <= j and 1 <= (i + j) <= 3)
    p_1x_o15 = sum(m[i, j] for i in range(max_gol) for j in range(max_gol) if i >= j and (i + j) >= 2)
    
    return {
        "Over 2.5": round(p_over25 * 100, 1),
        "Goal (BTTS)": round(p_btts * 100, 1),
        "Over 2.5 + Goal": round(p_over25_btts * 100, 1),
        "Multigol 2-4": round(p_mg24 * 100, 1),
        "Under 2.5": round(p_under25 * 100, 1),
        "1X + Under 3.5": round(p_1x_u35 * 100, 1),
        "X2 + Multigol 1-3": round(p_x2_mg13 * 100, 1),
        "1X + Over 1.5": round(p_1x_o15 * 100, 1)
    }

# --- PANNELLO TOUCH-SCREEN PER AGGIUNGERE PARTITE DAL TABLET ---
with st.expander("➕ AGGIUNGI O MODIFICA PARTITE DEL GIORNO (TOUCH)", expanded=False):
    with st.form("form_aggiungi_partita", clear_on_submit=True):
        c1, c2, c3 = st.columns(3)
        nuovo_orario = c1.text_input("Orario (es. 20:45)", "20:45")
        nuova_lega = c2.text_input("Campionato", "Serie A")
        nuovo_match = c3.text_input("Partita (Casa - Ospite)", "Inter - Milan")
        
        c4, c5, c6, c7 = st.columns(4)
        nuovo_la = c4.number_input("Lambda Casa (Gol attesi)", 0.2, 4.5, 1.80, 0.05)
        nuovo_lb = c5.number_input("Lambda Ospite (Gol attesi)", 0.2, 4.5, 1.45, 0.05)
        nuovo_mercato = c6.selectbox("Esito da valutare", [
            "Over 2.5", "Goal (BTTS)", "Over 2.5 + Goal", "Multigol 2-4",
            "Under 2.5", "1X + Under 3.5", "X2 + Multigol 1-3", "1X + Over 1.5"
        ])
        nuova_quota = c7.number_input("Quota Bookmaker", 1.30, 4.00, 1.80, 0.02)
        
        if st.form_submit_button("✅ Inserisci nella lista di oggi"):
            st.session_state.partite_db.append({
                "orario": nuovo_orario, "lega": nuova_lega, "match": nuovo_match,
                "lambda_a": nuovo_la, "lambda_b": nuovo_lb, "mercato": nuovo_mercato, "quota": nuova_quota
            })
            st.success(f"Aggiunta: {nuovo_match} ({nuovo_mercato} @ {nuova_quota})")

    if st.button("🗑️ Svuota tutte le partite"):
        st.session_state.partite_db = []
        st.rerun()

# --- IMPOSTAZIONI CASSA E ORARI ---
st.sidebar.header("⚙️ Controlli Rapidi")
cassa_iniziale = st.sidebar.number_input("Cassa di partenza (€)", min_value=5.0, value=10.0, step=5.0)
ora_partenza = st.sidebar.slider("Partenza scalata dalle ore:", 12, 18, 14)

# --- SCHEDE DEI DUE METODI ---
tab1, tab2 = st.tabs(["⚽ METODO 1: G8 QUANT (Pure Goals)", "🛡️ METODO 2: SOLID VALUE (Tattico & Combo)"])

# === LOGICA METODO 1: G8 QUANT ===
with tab1:
    st.subheader("Algoritmo Pure Goals & Scalata Sequenziale")
    st.caption("Filtri attivi: Solo mercati Gol | Lambda Tot >= 3.00 | Simmetria <= 0.75 | Quota 1.70 - 2.05 | Zero sovrapposizioni (gap 2h)")
    
    mercati_g8 = ["Over 2.5", "Goal (BTTS)", "Over 2.5 + Goal", "Multigol 2-4"]
    vietate = ["U19", "U21", "U23", "Primavera", "Reserves", "Amichevole"]
    
    validi_g8 = []
    for p in st.session_state.partite_db:
        if p["mercato"] not in mercati_g8:
            continue
        if any(v.lower() in p["lega"].lower() or v.lower() in p["match"].lower() for v in vietate):
            continue
        try:
            ora_obj = datetime.strptime(p["orario"], "%H:%M")
        except:
            continue
        if ora_obj.hour < ora_partenza:
            continue
            
        l_tot = p["lambda_a"] + p["lambda_b"]
        simm = abs(p["lambda_a"] - p["lambda_b"])
        if l_tot < 3.00 or simm > 0.75:
            continue
            
        if not (1.70 <= p["quota"] <= 2.05):
            continue
            
        probs = calcola_matrice_poisson(p["lambda_a"], p["lambda_b"])
        p_reale = probs[p["mercato"]]
        p_impl = round((1 / p["quota"]) * 100, 1)
        edge = round(p_reale - p_impl, 1)
        
        if edge > 1.5:
            validi_g8.append({
                "ora_obj": ora_obj, "Orario": p["orario"], "Competizione": p["lega"],
                "Partita": p["match"], "Esito Pure Goals": p["mercato"], "Quota": p["quota"],
                "Stake": "5/5" if edge >= 4.0 else "4/5",
                "Prob_Reale": p_reale, "Prob_Implicita": p_impl, "Edge": edge
            })
            
    validi_g8.sort(key=lambda x: x["ora_obj"])
    
    scalata = []
    riserve = []
    ultimo_inizio = None
    cassa_corr = cassa_iniziale
    
    for r in validi_g8:
        if ultimo_inizio is None or (r["ora_obj"] - ultimo_inizio) >= timedelta(hours=2):
            if len(scalata) < 5:
                ora_fine = (r["ora_obj"] + timedelta(minutes=115)).strftime("%H:%M")
                nuova_cassa = round(cassa_corr * r["Quota"], 2)
                scalata.append({
                    "Step": len(scalata) + 1,
                    "Orario (Inizio/Fine)": f"{r['Orario']} - {ora_fine}",
                    "Competizione": r["Competizione"],
                    "Partita": r["Partita"],
                    "Esito Pure Goals": r["Esito Pure Goals"],
                    "Quota": r["Quota"],
                    "Stake": r["Stake"],
                    "Prob. Reale vs Implicita": f"{r['Prob_Reale']}% vs {r['Prob_Implicita']}% (+{r['Edge']}%)",
                    "Progressione Cassa": f"{cassa_corr:.2f} € -> {nuova_cassa:.2f} €"
                })
                cassa_corr = nuova_cassa
                ultimo_inizio = r["ora_obj"]
            else:
                riserve.append(r)
        else:
            riserve.append(r)
            
    if scalata:
        st.dataframe(pd.DataFrame(scalata), use_container_width=True, hide_index=True)
        st.success(f"🎯 Potenziale finale scalata G8 Quant: **{cassa_corr:.2f} €** (partendo da {cassa_iniziale:.2f} €)")
    else:
        st.warning("Nessun match soddisfa tutti i filtri rigidi G8 Quant al momento.")
        
    if riserve:
        st.markdown("**🛡️ Riserve pronte (in caso di assenze pre-match):**")
        st.dataframe(pd.DataFrame(riserve)[["Orario", "Competizione", "Partita", "Esito Pure Goals", "Quota", "Edge"]], use_container_width=True, hide_index=True)

# === LOGICA METODO 2: SOLID VALUE ===
with tab2:
    st.subheader("Algoritmo Solid Value (Partite Tattiche & Doppia Chance Combo)")
    st.caption("Filtri attivi: Lambda Tot <= 2.65 | Alta stabilità difensiva | Quota 1.65 - 2.00 | Giocata a Stake Fisso o Raddoppio")
    
    mercati_solid = ["Under 2.5", "1X + Under 3.5", "X2 + Multigol 1-3", "1X + Over 1.5"]
    validi_solid = []
    
    for p in st.session_state.partite_db:
        if p["mercato"] not in mercati_solid:
            continue
        l_tot = p["lambda_a"] + p["lambda_b"]
        if l_tot > 2.65:
            continue
        if not (1.65 <= p["quota"] <= 2.00):
            continue
            
        probs = calcola_matrice_poisson(p["lambda_a"], p["lambda_b"])
        p_reale = probs[p["mercato"]]
        p_impl = round((1 / p["quota"]) * 100, 1)
        edge = round(p_reale - p_impl, 1)
        
        if edge > 1.0:
            b = p["quota"] - 1
            q_prob = 1 - (p_reale / 100)
