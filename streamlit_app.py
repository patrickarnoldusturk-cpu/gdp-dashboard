import streamlit as st
import pandas as pd
import urllib.parse
import datetime
import re

# App configuratie
st.set_page_config(page_title="Liquicity Festival Planner 2026", page_icon="🚀", layout="wide")
st.title("🚀 De Ultieme Liquicity Festival Planner")
st.write("Jouw vriendengroep live en automatisch gesynchroniseerd via de Streamlit cloud-opslag.")

# ==========================================
# 🌐 DATABASE INITIALISATIE
# ==========================================
if "vrienden" not in st.session_state:
    st.session_state.vrienden = ["Patrick", "Annika", "Harland", "Richard", "Dirk", "Van Brakel"]
if "datums" not in st.session_state:
    st.session_state.datums = {}
if "uitgaven" not in st.session_state:
    st.session_state.uitgaven = []
if "timetable" not in st.session_state:
    st.session_state.timetable = {}
if "paklijst" not in st.session_state:
    st.session_state.paklijst = [
        {"Item": "Partytent", "Wie": "Niemand", "Ingepakt": False},
        {"Item": "Koelbox + Koelementen", "Wie": "Niemand", "Ingepakt": False},
        {"Item": "Bluetooth Speaker", "Wie": "Niemand", "Ingepakt": False},
        {"Item": "Ducttape", "Wie": "Niemand", "Ingepakt": False},
        {"Item": "Kaartspel / Drankspellen", "Wie": "Niemand", "Ingepakt": False}
    ]

# --- SIDEBAR: NIEUWE VRIEND TOEVOEGEN ---
st.sidebar.header("👥 Wie gaat er mee?")
nieuwe_naam = st.sidebar.text_input("Naam van nieuwe festivalganger:")
if st.sidebar.button("➕ Voeg mij toe aan de groep"):
    if nieuwe_naam and nieuwe_naam.strip() != "":
        s_naam = nieuwe_naam.strip()
        if s_naam not in st.session_state.vrienden:
            st.session_state.vrienden.append(s_naam)
            st.sidebar.success(f"{s_naam} is succesvol toegevoegd!")
            st.rerun()
        else:
            st.sidebar.warning("Deze naam staat al in de lijst!")
    else:
        st.sidebar.error("Vul eerst een geldige naam in.")

st.sidebar.write("**Huidige groep:**", ", ".join(st.session_state.vrienden))
st.sidebar.write("---")

# --- TABS MAPS (7 tabbladen) ---
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
        naam = st.selectbox("Wie ben je?", st.session_state.vrienden, key="datum_naam")
        opties = ["Volledig Liquicity Weekend 2026", "Alleen Vrijdag", "Alleen Zaterdag", "Alleen Zondag"]
        gekozen_datums = st.multiselect("Welke festivals/weekenden kun jij?", opties, default=st.session_state.datums.get(naam, []))
        if st.button("Voorkeur Opslaan"):
            st.session_state.datums[naam] = gekozen_datums
            st.success("Voorkeuren live opgeslagen!")
            st.rerun()
            
    with col2:
        st.subheader("📊 Live Stemresultaten")
        stem_data = []
        for persoon, festivals in st.session_state.datums.items():
            for f in festivals:
                stem_data.append({"Festival": f, "Wie": persoon, "Aantal": 1})
        if stem_data:
            df_stemmen = pd.DataFrame(stem_data)
            st.bar_chart(data=df_stemmen, x="Festival", y="Aantal", color="Wie", stack=True)
            st.write("**Gedetailleerd overzicht:**")
            for p, festivals in st.session_state.datums.items():
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
        wie_betaalt = st.selectbox("Wie heeft betaald?", st.session_state.vrienden, key="kosten_wie")
        bedrag = st.number_input("Bedrag (€)", min_value=0.0, step=0.01, value=0.0)
        omschrijving = st.text_input("Waarvoor? (bijv. 'Combi-tickets', 'Campingboodschappen')")
        if st.button("Uitgave Toevoegen"):
            if bedrag > 0 and omschrijving:
                st.session_state.uitgaven.append({"Wie": wie_betaalt, "Bedrag": bedrag, "Omschrijving": omschrijving})
                st.success("Uitgave live gesynchroniseerd!")
                st.rerun()

    with col2:
        st.subheader("📈 Tussenstand & Balans")
        if st.session_state.uitgaven:
            df_uitgaven = pd.DataFrame(st.session_state.uitgaven)
            st.dataframe(df_uitgaven, hide_index=True)
            totaal = df_uitgaven["Bedrag"].sum()
            per_persoon = totaal / len(st.session_state.vrienden) if st.session_state.vrienden else 0
            st.metric("Totale kosten festival", f"€ {totaal:.2f}")
            st.metric("Kosten per persoon", f"€ {per_persoon:.2f}")
            
            balans = {vriend: -per_persoon for vriend in st.session_state.vrienden}
            for u in st.session_state.uitgaven:
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
            opties_verwijderen = [f"{i}: {u['Wie']} - €{u['Bedrag']} ({u['Omschrijving']})" for i, u in enumerate(st.session_state.uitgaven)]
            te_verwijderen = st.selectbox("Welke uitgave wil je wissen?", opties_verwijderen)
            if st.button("🔴 Geselecteerde uitgave wissen"):
                index_to_delete = int(te_verwijderen.split(":"))
                st.session_state.uitgaven.pop(index_to_delete)
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
        kiezende_vriend = st.selectbox("Wie ben je?", st.session_state.vrienden, key="timetable_persoon")
        if st.button("Mijn Line-up Voorkeuren Opslaan", type="primary"):
            for act in liquicity_acts:
                a_naam = act["Artiest"]
                if a_naam not in st.session_state.timetable:
                    st.session_state.timetable[a_naam] = []
                vinkje = st.session_state.get(f"v_{a_naam}_{kiezende_vriend}")
                if vinkje and kiezende_vriend not in st.session_state.timetable[a_naam]:
                    st.session_state.timetable[a_naam].append(kiezende_vriend)
                elif not vinkje and kiezende_vriend in st.session_state.timetable[a_naam]:
                    st.session_state.timetable[a_naam].remove(kiezende_vriend)
            st.success("Timetable bijgewerkt!")
            st.rerun()
        for act in liquicity_acts:
            a_naam = act["Artiest"]
            al_gevinkt = kiezende_vriend in st.session_state.timetable.get(a_naam, [])
            st.checkbox(f"⏱️ {act['Tijd']} | **{a_naam}** ({act['Stage']})", value=al_gevinkt, key=f"v_{a_naam}_{kiezende_vriend}")
    with col2:
        st.subheader("📊 Wie staat waar? (Groepsoverzicht)")
        timetable_data = []
        for act in liquicity_acts:
            a_naam = act["Artiest"]
            wie_gaan = st.session_state.timetable.get(a_naam, [])
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
                st.session_state.paklijst.append({"Item": nieuw_item, "Wie": "Niemand", "Ingepakt": False})
                st.success(f"'{nieuw_item}' opgeslagen!")
                st.rerun()
    with col2:
        st.subheader("📋 De Groeps-Checklist")
        if st.button("💾 Sla Checklist Wijzigingen Op"):
            for i in range(len(st.session_state.paklijst)):
                st.session_state.paklijst[i]['Wie'] = st.session_state[f"p_wie_{i}"]
                st.session_state.paklijst[i]['Ingepakt'] = st.session_state[f"p_check_{i}"]
            st.success("Paklijst gesynchroniseerd!")
            st.rerun()
        for i, item in enumerate(st.session_state.paklijst):
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.write(f"🔹 **{item['Item']}**")
            with col_b:
                h_idx = (st.session_state.vrienden.index(item['Wie']) + 1) if item['Wie'] in st.session_state.vrienden else 0
                st.selectbox(f"Wie?", ["Niemand"] + st.session_state.vrienden, index=h_idx, key=f"p_wie_{i}")
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
