import streamlit as st
import pandas as pd
import urllib.request
import urllib.parse
import json
import datetime
import re

# App configuratie
st.set_page_config(page_title="Liquicity Festival Planner 2026", page_icon="🚀", layout="wide")
st.title("🚀 De Ultieme Liquicity Festival Planner")
st.write("Jouw vriendengroep live en automatisch gesynchroniseerd in de cloud.")

# ==========================================
# 🌐 LIVE CLOUD GEHEUGEN (KVDB)
# ==========================================
DB_URL = "https://kvdb.io"

def laad_cloud_data():
    try:
        req = urllib.request.Request(DB_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode())
    except Exception:
        # Basisopstart als de cloud nog leeg is
        return {
            "vrienden": ["Patrick", "Annika", "Harland", "Richard", "Dirk", "Van Brakel"],
            "datums": {},
            "uitgaven": [],
            "timetable": {},
            "paklijst": [
                {"Item": "Partytent", "Wie": "Niemand", "Ingepakt": False},
                {"Item": "Koelbox + Koelementen", "Wie": "Niemand", "Ingepakt": False},
                {"Item": "Bluetooth Speaker", "Wie": "Niemand", "Ingepakt": False},
                {"Item": "Ducttape", "Wie": "Niemand", "Ingepakt": False},
                {"Item": "Kaartspel / Drankspellen", "Wie": "Niemand", "Ingepakt": False}
            ]
        }

def sla_cloud_data(data):
    try:
        req = urllib.request.Request(
            DB_URL, 
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'},
            method='POST'
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            pass
    except Exception as e:
        st.error(f"Cloud-synchronisatie mislukt: {e}")

# --- KOGELVRIJE DATABASE INITIALISATIE ---
if 'cloud_db' not in st.session_state or st.session_state.cloud_db is None:
    st.session_state.cloud_db = laad_cloud_data()

db = st.session_state.cloud_db

# --- SIDEBAR: NIEUWE VRIEND TOEVOEGEN ---
st.sidebar.header("👥 Wie gaat er mee?")
nieuwe_naam = st.sidebar.text_input("Naam van nieuwe festivalganger:")
if st.sidebar.button("➕ Voeg mij toe aan de groep"):
    if nieuwe_naam and nieuwe_naam.strip() != "":
        s_naam = nieuwe_naam.strip()
        if s_naam not in st.session_state.cloud_db["vrienden"]:
            st.session_state.cloud_db["vrienden"].append(s_naam)
            sla_cloud_data(st.session_state.cloud_db)
            st.sidebar.success(f"{s_naam} is succesvol toegevoegd!")
            st.rerun()
        else:
            st.sidebar.warning("Deze naam staat al in de lijst!")
    else:
        st.sidebar.error("Vul eers een geldige naam in.")

st.sidebar.write("**Huidige groep:**", ", ".join(st.session_state.cloud_db["vrienden"]))
st.sidebar.write("---")
if st.sidebar.button("🔄 Forceer Live Refresh"):
    st.session_state.cloud_db = laad_cloud_data()
    st.rerun()

# --- TABS MAPS ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🗓️ Welk Festival/Weekend?", "💶 Tickets & Spullen Kosten", "🎵 Timetable / Line-up", 
    "🧳 Groeps-Paklijst", "🚗 Uber naar Festival", "📸 Google Foto's", "🎵 Groeps-Playlist"
])

# ==========================================
# TAB 1: DATUMS / FESTIVALS PRIKKEN
# ==========================================
with tab1:
    st.header("Welk festival weekend gaan we pakken?")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Jouw voorkeur doorgeven")
        naam = st.selectbox("Wie ben je?", db["vrienden"], key="datum_naam")
        opties = ["Volledig Liquicity Weekend 2026", "Alleen Vrijdag", "Alleen Zaterdag", "Alleen Zondag"]
        gekozen_datums = st.multiselect("Welke festivals/weekenden kun jij?", opties, default=db["datums"].get(naam, []))
        if st.button("Voorkeur Opslaan"):
            db["datums"][naam] = gekozen_datums
            sla_cloud_data(db)
            st.success("Voorkeuren live opgeslagen!")
            st.rerun()
            
    with col2:
        st.subheader("📊 Live Stemresultaten")
        stem_data = []
        for persoon, festivals in db["datums"].items():
            for f in festivals:
                stem_data.append({"Festival": f, "Wie": persoon, "Aantal": 1})
        
        if stem_data:
            df_stemmen = pd.DataFrame(stem_data)
            st.bar_chart(data=df_stemmen, x="Festival", y="Aantal", color="Wie", stack=True)
            st.write("**Gedetailleerd overzicht:**")
            for p, festivals in db["datums"].items():
                if festivals:
                    st.write(f"• **{p}** heeft gestemd op: {', '.join(festivals)}")
        else:
            st.info("Nog geen stemmen uitgebracht door de groep.")

# ==========================================
# TAB 2: KOSTEN VERREKENEN
# ==========================================
with tab2:
    st.header("💶 Festival Pot (Tickets, Drank, Muntjes)")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Nieuwe festivaluitgave invoeren")
        wie_betaalt = st.selectbox("Wie heeft betaald?", db["vrienden"], key="kosten_wie")
        bedrag = st.number_input("Bedrag (€)", min_value=0.0, step=0.01, value=0.0)
        omschrijving = st.text_input("Waarvoor? (bijv. 'Combi-tickets', 'Campingboodschappen')")
        if st.button("Uitgave Toevoegen"):
            if bedrag > 0 and omschrijving:
                db["uitgaven"].append({"Wie": wie_betaalt, "Bedrag": bedrag, "Omschrijving": omschrijving})
                sla_cloud_data(db)
                st.success("Uitgave live gesynchroniseerd!")
                st.rerun()

    with col2:
        st.subheader("📈 Tussenstand & Balans")
        if db["uitgaven"]:
            df_uitgaven = pd.DataFrame(db["uitgaven"])
            st.dataframe(df_uitgaven, hide_index=True)
            totaal = df_uitgaven["Bedrag"].sum()
            per_persoon = totaal / len(db["vrienden"]) if db["vrienden"] else 0
            st.metric("Totale kosten festival", f"€ {totaal:.2f}")
            st.metric("Kosten per persoon", f"€ {per_persoon:.2f}")
            
            balans = {vriend: -per_persoon for vriend in db["vrienden"]}
            for u in db["uitgaven"]:
                if u["Wie"] in balans:
                    balans[u["Wie"]] += u["Bedrag"]
            for persoon, geld in balans.items():
                if geld > 0.01:
                    st.write(f"🟢 **{persoon}** krijgt nog **€ {geld:.2f}** terug.")
                elif geld < -0.01:
                    st.write(f"🔴 **{persoon}** moet nog **€ {abs(geld):.2f}** betalen.")
                else:
                    st.write(f"⚪ **{persoon}** staat precies quitte.")
            
            st.write("---")
            st.subheader("🗑️ Uitgave Verwijderen")
            opties_verwijderen = [f"{i}: {u['Wie']} - €{u['Bedrag']} ({u['Omschrijving']})" for i, u in enumerate(db["uitgaven"])]
            te_verwijderen = st.selectbox("Welke uitgave wil je wissen?", opties_verwijderen)
            if st.button("🔴 Geselecteerde uitgave wissen"):
                index_to_delete = int(te_verwijderen.split(":"))
                db["uitgaven"].pop(index_to_delete)
                sla_cloud_data(db)
                st.success("Uitgave verwijderd uit de cloud!")
                st.rerun()
        else:
            st.info("Nog geen groepsuitgaven ingevoerd.")

# ==========================================
# TAB 3: TIMETABLE / LINE-UP
# ==========================================
with tab3:
    st.header("🎵 Liquicity 2026 Groeps-Timetable")
    liquicity_acts = [
        {"Dag": "Vrijdag", "Tijd": "21:30 - 23:00", "Artiest": "Netsky", "Stage": "Galaxy"},
        {"Dag": "Vrijdag", "Tijd": "20:15 - 21:30", "Artiest": "Wilkinson", "Stage": "Galaxy"},
        {"Dag": "Zaterdag", "Tijd": "21:30 - 23:00", "Artiest": "Hybrid Minds", "Stage": "Galaxy"},
        {"Dag": "Zaterdag", "Tijd": "20:00 - 21:30", "Artiest": "Fox Stevenson (LIVE)", "Stage": "Galaxy"},
        {"Dag": "Zondag", "Tijd": "22:00 - 23:30", "Artiest": "Andy C", "Stage": "Galaxy"},
        {"Dag": "Zondag", "Tijd": "20:30 - 22:00", "Artiest": "Maduk", "Stage": "Galaxy"}
    ]
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🪐 Geef jouw 'Must-Sees' door")
        kiezende_vriend = st.selectbox("Wie ben je?", db["vrienden"], key="timetable_persoon")
        
        if st.button("Mijn Line-up Voorkeuren Opslaan", type="primary"):
            for act in liquicity_acts:
                a_naam = act["Artiest"]
                if a_naam not in db["timetable"]:
                    db["timetable"][a_naam] = []
                
                vinkje = st.session_state.get(f"v_{a_naam}_{kiezende_vriend}")
                if vinkje and kiezende_vriend not in db["timetable"][a_naam]:
                    db["timetable"][a_naam].append(kiezende_vriend)
                elif not vinkje and kiezende_vriend in db["timetable"][a_naam]:
                    db["timetable"][a_naam].remove(kiezende_vriend)
            sla_cloud_data(db)
            st.success("Timetable cloud-sync voltooid!")
            st.rerun()

        for act in liquicity_acts:
            a_naam = act["Artiest"]
            al_gevinkt = kiezende_vriend in db["timetable"].get(a_naam, [])
            st.checkbox(f"⏱️ {act['Tijd']} | **{a_naam}** ({act['Stage']})", value=al_gevinkt, key=f"v_{a_naam}_{kiezende_vriend}")

    with col2:
        st.subheader("📊 Wie staat waar? (Groepsoverzicht)")
        timetable_data = []
        for act in liquicity_acts:
            a_naam = act["Artiest"]
            wie_gaan = db["timetable"].get(a_naam, [])
            timetable_data.append({
                "Dag": act["Dag"], "Tijd": act["Tijd"], "Artiest": a_naam, "Stage": act["Stage"],
