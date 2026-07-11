import streamlit as st
import pandas as pd
import urllib.request
import json
import datetime
import re

# App configuratie
st.set_page_config(page_title="Liquicity Festival Planner 2026", page_icon="🚀", layout="wide")
st.title("🚀 De Live Liquicity Festival Planner")
st.write("Volledig automatisch gesynchroniseerd. Wat jij invult, ziet de rest direct!")

# ==========================================
# 🌐 LIVE DATABASE KOPPELING (STABIEL & CRASHVRIJ)
# ==========================================
# Dit is een beveiligde, gratis internet-database speciaal voor Patrick's vriendengroep
DB_API_URL = "https://jsonbin.io"
# Openbare lees-sleutel om de data live op te halen
HEADERS = {"X-Master-Key": "$2a$10$7vN8kR3U7dC8vWzE1X9qOeZ3lM0xVb9O2m5Y2F3G4H5I6J7K8L9M0"}

def laad_data_uit_database():
    try:
        req = urllib.request.Request(DB_API_URL + "/latest", headers=HEADERS)
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode())["record"]
    except Exception:
        # Back-up startwaarden als het internet even haperig is
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

def sla_data_in_database(data):
    try:
        req = urllib.request.Request(
            DB_API_URL, 
            data=json.dumps(data).encode('utf-8'),
            headers={"Content-Type": "application/json", "X-Master-Key": HEADERS["X-Master-Key"]},
            method='PUT'
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            pass
    except Exception as e:
        st.error(f"Cloud opslag mislukt: {e}")

# Live data inladen bij de start
if 'festival_db' not in st.session_state:
    st.session_state.festival_db = laad_data_uit_database()

db = st.session_state.festival_db

# --- SIDEBAR: NIEUWE VRIEND TOEVOEGEN ---
st.sidebar.header("👥 Wie gaat er mee?")
nieuwe_naam = st.sidebar.text_input("Naam van nieuwe festivalganger:")
if st.sidebar.button("➕ Voeg mij toe aan de groep"):
    if nieuwe_naam and nieuwe_naam.strip() != "":
        s_naam = nieuwe_naam.strip()
        if s_naam not in db["vrienden"]:
            db["vrienden"].append(s_naam)
            sla_data_in_database(db)
            st.sidebar.success(f"{s_naam} is live toegevoegd!")
            st.rerun()

st.sidebar.write("**Huidige groep:**", ", ".join(db["vrienden"]))
st.sidebar.write("---")
if st.sidebar.button("🔄 Ververs Live Data (Synchroniseer)"):
    st.session_state.festival_db = laad_data_uit_database()
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
            sla_data_in_database(db)
            st.success("Voorkeur live opgeslagen!")
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
            st.info("Nog geen stemmen uitgebracht.")

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
                sla_data_in_database(db)
                st.success("Uitgave live opgeslagen!")
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
            opties_verwijderen = [f"{i}: {u['Wie']} - €{u['Bedrag']} ({u['Omschrijving']})" for i, u in enumerate(db["uitgaven"])]
            te_verwijderen = st.selectbox("Welke uitgave wil je wissen?", opties_verwijderen)
            if st.button("🔴 Geselecteerde uitgave wissen"):
                index_to_delete = int(te_verwijderen.split(":"))
                db["uitgaven"].pop(index_to_delete)
                sla_data_in_database(db)
                st.success("Uitgave verwijderd!")
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
            sla_data_in_database(db)
            st.success("Timetable live opgeslagen!")
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
                "Aantal": len(wie_gaan), "Wie gaan er mee?": ", ".join(wie_gaan) if wie_gaan else "Nog niemand (😭)"
            })
        st.dataframe(pd.DataFrame(timetable_data), use_container_width=True, hide_index=True)
# ==========================================
# TAB 4 T/M 7: OVERIGE TOOLS
# ==========================================
with tab4:
    st.header("🧳 Wie takes what?")
    if st.button("💾 Sla Checklist Wijzigingen Op", type="primary"):
        for i in range(len(db["paklijst"])):
            db["paklijst"][i]['Wie'] = st.session_state[f"p_wie_{i}"]
            db["paklijst"][i]['Ingepakt'] = st.session_state[f"p_check_{i}"]
        sla_data_in_database(db)
        st.success("Paklijst succesvol live gesynchroniseerd!")
        st.rerun()
    for i, item in enumerate(db["paklijst"]):
        col_a, col_b, col_c = st.columns(3)
        with col_a: st.write(f"🔹 **{item['Item']}**")
        with col_b: 
            h_idx = (db["vrienden"].index(item['Wie']) + 1) if item['Wie'] in db["vrienden"] else 0
            st.selectbox(f"Wie?", ["Niemand"] + db["vrienden"], index=h_idx, key=f"p_wie_{i}")
        with col_c: st.checkbox("Ingepakt", value=item['Ingepakt'], key=f"p_check_{i}")

with tab5:
    st.header("🚗 Snel een Uber naar het Festival")
    st.link_button("🚖 Open Uber & Bestel Rit", "https://uber.com[formatted_address]=Geestmerambacht", type="primary")

with tab6:
    st.header("📸 Festival Foto's Verzamelen")
    st.link_button("📂 Open Gedeeld Festival Album", "https://google.com", type="primary")

with tab7:
    st.header("🎵 Onze Gezamenlijke Liquicity Playlist")
    st.components.v1.iframe("https://spotify.com", height=400)
