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
# 🌐 AUTOMATISCHE CLOUD-SYNCHRONISATIE
# ==========================================
# Dit is de unieke online sleutel voor de groepsdatabase van Patrick
CLOUD_URL = "https://kvdb.io"

def laad_data_uit_cloud():
    try:
        req = urllib.request.Request(CLOUD_URL, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            return json.loads(response.read().decode())
    except Exception:
        # Als de cloud nog leeg is, starten we met deze standaardwaarden
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

def sla_data_in_cloud(data):
    try:
        req = urllib.request.Request(
            CLOUD_URL, 
            data=json.dumps(data).encode('utf-8'),
            headers={'Content-Type': 'application/json', 'User-Agent': 'Mozilla/5.0'},
            method='PUT'
        )
        with urllib.request.urlopen(req, timeout=5) as response:
            pass
    except Exception:
        pass

# Altijd de meest actuele stand ophalen - NU MET DE JUISTE FUNCTIENAAM (laad_data_uit_cloud)
if 'groeps_data' not in st.session_state or st.session_state.groeps_data is None:
    st.session_state.groeps_data = laad_data_uit_cloud()

g_data = st.session_state.groeps_data

# --- SIDEBAR: NIEUWE VRIEND TOEVOEGEN ---
st.sidebar.header("👥 Wie gaat er mee?")
nieuwe_naam = st.sidebar.text_input("Naam van nieuwe festivalganger:")
if st.sidebar.button("➕ Voeg mij toe aan de groep"):
    if nieuwe_naam and nieuwe_naam.strip() != "":
        s_naam = nieuwe_naam.strip()
        if s_naam not in g_data["vrienden"]:
            g_data["vrienden"].append(s_naam)
            sla_data_in_cloud(g_data)
            st.sidebar.success(f"{s_naam} is toegevoegd!")
            st.rerun()
        else:
            st.sidebar.warning("Deze naam staat al in de lijst!")

st.sidebar.write("**Huidige groep:**", ", ".join(g_data["vrienden"]))
st.sidebar.write("---")
if st.sidebar.button("🔄 Forceer Live Refresh"):
    st.session_state.groeps_data = laad_data_uit_cloud() # GECORRIGEERD NAAR UIT_CLOUD
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
        naam = st.selectbox("Wie ben je?", g_data["vrienden"], key="datum_naam")
        opties = ["Volledig Liquicity Weekend 2026", "Alleen Vrijdag", "Alleen Zaterdag", "Alleen Zondag"]
        gekozen_datums = st.multiselect("Welke festivals/weekenden kun jij?", opties, default=g_data["datums"].get(naam, []))
        if st.button("Voorkeur Opslaan"):
            g_data["datums"][naam] = gekozen_datums
            sla_data_in_cloud(g_data)
            st.success("Voorkeuren opgeslagen in de cloud!")
            st.rerun()
            
    with col2:
        st.subheader("📊 Live Stemresultaten")
        stem_data = []
        for persoon, festivals in g_data["datums"].items():
            for f in festivals:
                stem_data.append({"Festival": f, "Wie": persoon, "Aantal": 1})
        if stem_data:
            df_stemmen = pd.DataFrame(stem_data)
            st.bar_chart(data=df_stemmen, x="Festival", y="Aantal", color="Wie", stack=True)
            st.write("**Gedetailleerd overzicht:**")
            for p, festivals in g_data["datums"].items():
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
        wie_betaalt = st.selectbox("Wie heeft betaald?", g_data["vrienden"], key="kosten_wie")
        bedrag = st.number_input("Bedrag (€)", min_value=0.0, step=0.01, value=0.0)
        omschrijving = st.text_input("Waarvoor? (bijv. 'Combi-tickets', 'Campingboodschappen')")
        if st.button("Uitgave Toevoegen"):
            if bedrag > 0 and omschrijving:
                g_data["uitgaven"].append({"Wie": wie_betaalt, "Bedrag": bedrag, "Omschrijving": omschrijving})
                sla_data_in_cloud(g_data)
                st.success("Uitgave live opgeslagen!")
                st.rerun()

    with col2:
        st.subheader("📈 Tussenstand & Balans")
        if g_data["uitgaven"]:
            df_uitgaven = pd.DataFrame(g_data["uitgaven"])
            st.dataframe(df_uitgaven, hide_index=True)
            totaal = df_uitgaven["Bedrag"].sum()
            per_persoon = totaal / len(g_data["vrienden"]) if g_data["vrienden"] else 0
            st.metric("Totale kosten festival", f"€ {totaal:.2f}")
            st.metric("Kosten per persoon", f"€ {per_persoon:.2f}")
            
            balans = {vriend: -per_persoon for vriend in g_data["vrienden"]}
            for u in g_data["uitgaven"]:
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
            opties_verwijderen = [f"{i}: {u['Wie']} - €{u['Bedrag']} ({u['Omschrijving']})" for i, u in enumerate(g_data["uitgaven"])]
            te_verwijderen = st.selectbox("Welke uitgave wil je wissen?", opties_verwijderen)
            if st.button("🔴 Geselecteerde uitgave wissen"):
                index_to_delete = int(te_verwijderen.split(":"))
                g_data["uitgaven"].pop(index_to_delete)
                sla_data_in_cloud(g_data)
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
        kiezende_vriend = st.selectbox("Wie ben je?", g_data["vrienden"], key="timetable_persoon")
        if st.button("Mijn Line-up Voorkeuren Opslaan", type="primary"):
            for act in liquicity_acts:
                a_naam = act["Artiest"]
                if a_naam not in g_data["timetable"]:
                    g_data["timetable"][a_naam] = []
                vinkje = st.session_state.get(f"v_{a_naam}_{kiezende_vriend}")
                if vinkje and kiezende_vriend not in g_data["timetable"][a_naam]:
                    g_data["timetable"][a_naam].append(kiezende_vriend)
                elif not vinkje and kiezende_vriend in g_data["timetable"][a_naam]:
                    g_data["timetable"][a_naam].remove(kiezende_vriend)
            sla_data_in_cloud(g_data)
            st.success("Timetable bijgewerkt in cloud!")
            st.rerun()
        for act in liquicity_acts:
            a_naam = act["Artiest"]
            al_gevinkt = kiezende_vriend in g_data["timetable"].get(a_naam, [])
            st.checkbox(f"⏱️ {act['Tijd']} | **{a_naam}** ({act['Stage']})", value=al_gevinkt, key=f"v_{a_naam}_{kiezende_vriend}")
    with col2:
        st.subheader("📊 Wie staat waar? (Groepsoverzicht)")
        timetable_data = []
        for act in liquicity_acts:
            a_naam = act["Artiest"]
            wie_gaan = g_data["timetable"].get(a_naam, [])
            timetable_data.append({
                "Dag": act["Dag"], "Tijd": act["Tijd"], "Artiest": a_naam, "Stage": act["Stage"],
                "Aantal": len(wie_gaan), "Wie gaan er mee?": ", ".join(wie_gaan) if wie_gaan else "Nog niemand (😭)"
            })
        st.dataframe(pd.DataFrame(timetable_data), use_container_width=True, hide_index=True)
# ==========================================
# TAB 4: GROUPS-PAKLIJST
# ==========================================
with tab4:
    st.header("🧳 Wie takes what?")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Nieuw item toevoegen")
        nieuw_item = st.text_input("Wat moet er nog mee?")
        if st.button("Item aan paklijst toevoegen"):
            if nieuw_item:
                g_data["paklijst"].append({"Item": nieuw_item, "Wie": "Niemand", "Ingepakt": False})
                sla_data_in_cloud(g_data)
                st.success(f"'{nieuw_item}' opgeslagen!")
                st.rerun()
    with col2:
        st.subheader("📋 De Groeps-Checklist")
        if st.button("💾 Sla Checklist Wijzigingen Op"):
            for i in range(len(g_data["paklijst"])):
                g_data["paklijst"][i]['Wie'] = st.session_state[f"p_wie_{i}"]
                g_data["paklijst"][i]['Ingepakt'] = st.session_state[f"p_check_{i}"]
            sla_data_in_cloud(g_data)
            st.success("Paklijst in de cloud bijgewerkt!")
            st.rerun()
            
        for i, item in enumerate(g_data["paklijst"]):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.write(f"🔹 **{item['Item']}**")
            with col_b:
                h_idx = (g_data["vrienden"].index(item['Wie']) + 1) if item['Wie'] in g_data["vrienden"] else 0
                st.selectbox(f"Wie?", ["Niemand"] + g_data["vrienden"], index=h_idx, key=f"p_wie_{i}")
            with col_c:
                st.checkbox("Ingepakt", value=item['Ingepakt'], key=f"p_check_{i}")

# ==========================================
# TAB 5: UBER BOEKEN
# ==========================================
with tab5:
    st.header("🚗 Snel een Uber naar het Festival")
    bestemming = "Liquicity Festival, Geestmerambacht"
    st.write(f"Bestemming staat ingesteld op: **{bestemming}**")
    ophaal_locatie = st.text_input("Ophaallocatie (Laat leeg voor huidige GPS)", key="uber_ophaal_fest")
    gecodeerde_bestemming = urllib.parse.quote(bestemming)
    uber_url = f"https://uber.com[formatted_address]={gecodeerde_bestemming}"
    if ophaal_locatie:
        uber_url += f"&pickup[formatted_address]={urllib.parse.quote(ophaal_locatie)}"
    st.link_button("🚖 Open Uber & Bestel Rit", uber_url, type="primary")

# ==========================================
# TAB 6: GOOGLE FOTO'S
# ==========================================
with tab6:
    st.header("📸 Festival Foto's Verzamelen")
    st.link_button("📂 Open Gedeeld Festival Album", "https://google.com", type="primary")

# ==========================================
# TAB 7: SPOTIFY GROEPS-PLAYLIST
# ==========================================
with tab7:
    st.header("🎵 Onze Gezamenlijke Liquicity Playlist")
    spotify_playlist_url = "https://spotify.com" 
    match = re.search(r'playlist/([a-zA-Z0-9]{22})', spotify_playlist_url)
    playlist_id = match.group(1) if match else "37i9dQZF1DX5wD9v76ANSG"
    st.components.v1.iframe(f"https://spotify.com{playlist_id}?utm_source=generator", height=400)
    st.link_button("🎶 Open Playlist in Spotify", spotify_playlist_url, type="primary")
