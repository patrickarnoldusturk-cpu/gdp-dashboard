import streamlit as st
import pandas as pd
import urllib.parse
import datetime

# App configuratie
st.set_page_config(page_title="Festival Vrienden Planner", page_icon="⛺", layout="wide")
st.title("⛺ De Ultieme Festival Weekend Planner")
st.write("Jouw vriendengroep festival-proof geautomatiseerd: line-up, kosten, paklijst en Uber.")

# --- INITIALISATIE ---
if 'datums' not in st.session_state:
    st.session_state.datums = {}
if 'uitgaven' not in st.session_state:
    st.session_state.uitgaven = []
if 'timetable' not in st.session_state:
    st.session_state.timetable = []
if 'paklijst' not in st.session_state:
    st.session_state.paklijst = [
        {"Item": "Partytent", "Wie": "Niemand", "Ingepakt": False},
        {"Item": "Koelbox + Koelementen", "Wie": "Niemand", "Ingepakt": False},
        {"Item": "Bluetooth Speaker", "Wie": "Niemand", "Ingepakt": False},
        {"Item": "Ducttape", "Wie": "Niemand", "Ingepakt": False},
        {"Item": "Kaartspel / Drankspellen", "Wie": "Niemand", "Ingepakt": False}
    ]
if 'vrienden' not in st.session_state:
    st.session_state.vrienden = ["Patrick", "Annika", "Harland", "Richard", "Dirk", "Van Brakel"]

# --- NIEUW: ZELF IEMAND TOEVOEGEN ---
st.sidebar.header("👥 Wie gaat er mee?")
nieuwe_naam = st.sidebar.text_input("Naam van nieuwe festivalganger:")
if st.sidebar.button("➕ Voeg mij toe aan de groep"):
    if nieuwe_naam and nieuwe_naam not in st.session_state.vrienden:
        st.session_state.vrienden.append(nieuwe_naam)
        st.sidebar.success(f"{nieuwe_naam} is toegevoegd!")
        st.rerun()
    elif nieuwe_naam in st.session_state.vrienden:
        st.sidebar.warning("Deze naam staat al in de lijst!")
st.sidebar.write("**Huidige groep:**", ", ".join(st.session_state.vrienden))
st.sidebar.write("---")


# --- TABS MAPS (7 stuks) ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "🗓️ Welk Festival/Weekend?", 
    "💶 Tickets & Spullen Kosten", 
    "🎵 Timetable / Line-up", 
    "🧳 Groeps-Paklijst",
    "🚗 Uber naar Festival", 
    "📸 Google Foto's",
    "🎵 Groeps-Playlist"
])


# ==========================================
# TAB 1: DATUMS / FESTIVALS PRIKKEN
# ==========================================
with tab1:
    st.header("Welk festival weekend gaan we pakken?")
    
    # Maak twee kolommen aan
    col1, col2 = st.columns(2)
    
    # LINKER KOLOM: INVOEREN
    with col1:
        st.subheader("Jouw voorkeur doorgeven")
        naam = st.selectbox("Wie ben je?", st.session_state.vrienden, key="datum_naam")
        opties = ["Volledig Liquicity Weekend 2026", "Alleen Vrijdag", "Alleen Zaterdag", "Alleen Zondag"]
        gekozen_datums = st.multiselect("Welke festivals/weekenden kun jij?", opties)
        if st.button("Voorkeur Opslaan"):
            st.session_state.datums[naam] = gekozen_datums
            st.success(f"Voorkeuren voor {naam} bijgewerkt!")
            st.rerun()

    # RECHTER KOLOM: GRAFIEK & RESULTATEN
    with col2:
        st.subheader("📊 Live Stemresultaten")
        if st.session_state.datums:
            # Maak een simpele lijst van alle stemmen
            stem_data = []
            for persoon, festivals in st.session_state.datums.items():
                for f in festivals:
                    stem_data.append({"Festival": f, "Wie": persoon, "Aantal": 1})
            
            if stem_data:
                df_stemmen = pd.DataFrame(stem_data)
                
                # Toon de kleurrijke grafiek met de juiste x-as en kleurverdeling per persoon
                st.bar_chart(data=df_stemmen, x="Festival", y="Aantal", color="Wie", stack=True)
                
                # Handig tekstoverzichtje eronder
                st.write("**Gedetailleerd overzicht:**")
                for persoon, festivals in st.session_state.datums.items():
                    if festivals:
                        st.write(f"• **{persoon}** heeft gestemd op: {', '.join(festivals)}")
            else:
                st.info("Nog geen stemmen uitgebracht.")
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
        wie_betaalt = st.selectbox("Wie heeft betaald?", st.session_state.vrienden, key="kosten_wie")
        bedrag = st.number_input("Bedrag (€)", min_value=0.0, step=0.01, value=0.0)
        omschrijving = st.text_input("Waarvoor? (bijv. 'Combi-tickets', 'Campingboodschappen')")
        if st.button("Uitgave Toevoegen"):
            if bedrag > 0 and omschrijving:
                st.session_state.uitgaven.append({"Wie": wie_betaalt, "Bedrag": bedrag, "Omschrijving": omschrijving})
                st.success("Uitgave succesvol toegevoegd!")
                st.rerun()
            else:
                st.error("Vul een geldig bedrag en omschrijving in.")
    with col2:
        st.subheader("📈 Tussenstand & Balans")
        if st.session_state.uitgaven:
            df_uitgaven = pd.DataFrame(st.session_state.uitgaven)
            st.dataframe(df_uitgaven)
            totaal = df_uitgaven["Bedrag"].sum()
            per_persoon = totaal / len(st.session_state.vrienden)
            st.metric("Totale kosten festival", f"€ {totaal:.2f}")
            st.metric("Kosten per persoon", f"€ {per_persoon:.2f}")
            
            st.subheader("⚖️ Wat krijgt of moet iedereen betalen?")
            balans = {vriend: -per_persoon for vriend in st.session_state.vrienden}
            for u in st.session_state.uitgaven:
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
            opties_verwijderen = [f"{i}: {u['Wie']} - €{u['Bedrag']} ({u['Omschrijving']})" for i, u in enumerate(st.session_state.uitgaven)]
            te_verwijderen = st.selectbox("Welke uitgave wil je wissen?", opties_verwijderen, key="verwijder_select")
            if st.button("🔴 Geselecteerde uitgave wissen"):
                index_to_delete = int(te_verwijderen.split(":")[0])
                st.session_state.uitgaven.pop(index_to_delete)
                st.success("Uitgave succesvol verwijderd!")
                st.rerun()
        else:
            st.info("Nog geen uitgaven ingevoerd.")

# ==========================================
# TAB 3: TIMETABLE / LINE-UP (Liquicity 2026)
# ==========================================
with tab3:
    st.header("🎵 Liquicity 2026 Groeps-Timetable")
    st.write("Vink aan welke artiesten je wilt zien. De app laat direct zien wie er met je meegaat!")

    # Officiële topacts van Liquicity Festival 2026 (Vrijdag t/m Zondag)
    liquicity_acts = [
        {"Dag": "Vrijdag", "Tijd": "21:30 - 23:00", "Artiest": "Netsky", "Stage": "Galaxy"},
        {"Dag": "Vrijdag", "Tijd": "20:15 - 21:30", "Artiest": "Wilkinson", "Stage": "Galaxy"},
        {"Dag": "Vrijdag", "Tijd": "19:00 - 20:15", "Artiest": "Culture Shock", "Stage": "Galaxy"},
        {"Dag": "Vrijdag", "Tijd": "15:45 - 17:00", "Artiest": "Goddard.", "Stage": "Galaxy"},
        {"Dag": "Zaterdag", "Tijd": "21:30 - 23:00", "Artiest": "Hybrid Minds", "Stage": "Galaxy"},
        {"Dag": "Zaterdag", "Tijd": "20:00 - 21:30", "Artiest": "Fox Stevenson (LIVE)", "Stage": "Galaxy"},
        {"Dag": "Zaterdag", "Tijd": "18:30 - 20:00", "Artiest": "Andromedik", "Stage": "Galaxy"},
        {"Dag": "Zondag", "Tijd": "22:00 - 23:30", "Artiest": "Andy C", "Stage": "Galaxy"},
        {"Dag": "Zondag", "Tijd": "20:30 - 22:00", "Artiest": "Maduk", "Stage": "Galaxy"},
        {"Dag": "Zondag", "Tijd": "19:00 - 20:30", "Artiest": "Koven", "Stage": "Galaxy"}
    ]

    # Database voor de stemmen aanmaken als deze nog niet bestaat
    if 'timetable_votes' not in st.session_state:
        st.session_state.timetable_votes = {act["Artiest"]: [] for act in liquicity_acts}

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🪐 Geef jouw 'Must-Sees' door")
        kiezende_vriend = st.selectbox("Wie ben je?", st.session_state.vrienden, key="timetable_persoon")
        
        st.write("Vink de artiesten aan die je wilt bezoeken:")
        for act in liquicity_acts:
            artiest_naam = act["Artiest"]
            
            # Controleer of deze persoon al gestemd had
            al_gestemd = kiezende_vriend in st.session_state.timetable_votes[artiest_naam]
            
            vinkje = st.checkbox(
                f"⏱️ {act['Tijd']} | **{artiest_naam}** ({act['Stage']} stage) — *[{act['Dag']}]*", 
                value=al_gestemd, 
                key=f"vote_{artiest_naam}_{kiezende_vriend}"
            )
            
            # Update de database op basis van het vinkje
            if vinkje and not al_gestemd:
                st.session_state.timetable_votes[artiest_naam].append(kiezende_vriend)
            elif not vinkje and al_gestemd:
                st.session_state.timetable_votes[artiest_naam].remove(kiezende_vriend)

        if st.button("Mijn Line-up Opslaan", type="primary"):
            st.success("Je voorkeuren zijn live bijgewerkt in het groepsoverzicht!")
            st.rerun()

    with col2:
        st.subheader("📊 Wie staat waar? (Groepsoverzicht)")
        st.write("Hier zie je per artiest wie er allemaal in het publiek staan:")
        
        # Bouw een overzichtelijke tabel van de acts en de stemmen
        timetable_data = []
        for act in liquicity_acts:
            artiest_naam = act["Artiest"]
            wie_gaan_er = st.session_state.timetable_votes[artiest_naam]
            
            timetable_data.append({
                "Dag": act["Dag"],
                "Tijd": act["Tijd"],
                "Artiest": artiest_naam,
                "Stage": act["Stage"],
                "Aantal Vrienden": len(wie_gaan_er),
                "Wie gaan er mee?": ", ".join(wie_gaan_er) if wie_gaan_er else "Nog niemand (😭)"
            })
            
        df_timetable = pd.DataFrame(timetable_data)
        # Sorteer netjes chronologisch op Dag
        st.dataframe(df_timetable, use_container_width=True, hide_index=True)
        
        st.info("💡 Tip: Sorteer de tabel in de browser door op de kolommen 'Dag' of 'Tijd' te klikken!")


# ==========================================
# TAB 4: GROEPS-PAKLIJST
# ==========================================
with tab4:
    st.header("🧳 Wie neemt wat mee?")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Nieuw item toevoegen")
        nieuw_item = st.text_input("Wat moet er nog mee?")
        if st.button("Item aan paklijst toevoegen"):
            if nieuw_item:
                st.session_state.paklijst.append({"Item": nieuw_item, "Wie": "Niemand", "Ingepakt": False})
                st.success(f"'{nieuw_item}' toegevoegd!")
                st.rerun()
                
    with col2:
        st.subheader("📋 De Groeps-Checklist")
        if st.session_state.paklijst:
            for i, item in enumerate(st.session_state.paklijst):
                col_a, col_b, col_c = st.columns(3)
                with col_a:
                    st.write(f"🔹 **{item['Item']}**")
                with col_b:
                    huidige_index = st.session_state.vrienden.index(item['Wie']) if item['Wie'] in st.session_state.vrienden else 0
                    wie_meeneemt = st.selectbox(f"Wie?", ["Niemand"] + st.session_state.vrienden, index=huidige_index if item['Wie'] != "Niemand" else 0, key=f"wie_{i}")
                    if wie_meeneemt != item['Wie']:
                        st.session_state.paklijst[i]['Wie'] = wie_meeneemt
                        st.rerun()
                with col_c:
                    ingepakt = st.checkbox("Ingepakt", value=item['Ingepakt'], key=f"check_{i}")
                    if ingepakt != item['Ingepakt']:
                        st.session_state.paklijst[i]['Ingepakt'] = ingepakt
                        st.rerun()

# ==========================================
# TAB 5: UBER BOEKEN
# ==========================================
with tab5:
    st.header("🚗 Snel een Uber naar het Festival")
    bestemming = st.text_input("Naar welk festivalterrein of station moeten jullie?", value="Lowlands Biddinghuizen")
    ophaal_locatie = st.text_input("Ophaallocatie (Laat leeg voor huidige GPS)", key="uber_ophaal_fest")
    if bestemming:
        gecodeerde_bestemming = urllib.parse.quote(bestemming)
        uber_url = f"https://uber.com[formatted_address]={gecodeerde_bestemming}"
        if ophaal_locatie:
            gecodeerde_ophaal = urllib.parse.quote(ophaal_locatie)
            uber_url += f"&pickup[formatted_address]={gecodeerde_ophaal}"
        st.write("---")
        st.link_button("🚖 Open Uber & Bestel Rit", uber_url, type="primary", key="uber_btn_fest")

# ==========================================
# TAB 6: GOOGLE FOTO'S
# ==========================================
with tab6:
    st.header("📸 Festival Foto's Verzamelen")
    google_fotos_album_url = "https://google.com" 
    st.link_button("📂 Open Gedeeld Festival Album", google_fotos_album_url, type="primary", key="fotos_btn_fest")

# ==========================================
# TAB 7: SPOTIFY GROEPS-PLAYLIST
# ==========================================
with tab7:
    st.header("🎵 Onze Gezamenlijke Liquicity Playlist")
    st.write("Luister direct naar de playlist of voeg zelf je favoriete Drum & Bass tracks toe!")
    
    # ⚠️ HIER PLAK JIE JOUW EIGEN LINK (Elke Spotify-link werkt nu!)
    spotify_playlist_url = "https://open.spotify.com/playlist/2xjqPMtbmhpsS1QAzwnkYs?si=c4aad32c934f4349&pt=ee26a639c0facc55f723cbfd8d11178e" 
    
    # Kogelvrije methode om de unieke playlist-ID van 22 tekens te pakken
    import re
    match = re.search(r'playlist/([a-zA-Z0-9]{22})', spotify_playlist_url)
    if match:
        playlist_id = match.group(1)
    else:
        # Altijd een werkende back-up als de link per ongeluk helemaal misgaat
        playlist_id = "37i9dQZF1DX5wD9v76ANSG"
        
    embed_url = f"https://open.spotify.com/embed/playlist/{playlist_id}?utm_source=generator"
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("🔊 Live Luisteren")
        # Dit bouwt de officiële Spotify Player foutloos in de app
        st.components.v1.iframe(embed_url, height=400, scrolling=False)
        
    with col2:
        st.subheader("➕ Nummers toevoegen?")
        st.write("Wil je dat iedereen nummers kan toevoegen?")
        st.info("""
        1. Open deze playlist in de **Spotify-app** op je telefoon of laptop.
        2. Klik op het poppetje met het plusje (**'Samenwerkingsplaylist maken'** of 'Collaborative playlist').
        3. Kopieer die specifieke deellink en plak hem in de code van festival.py bij 'spotify_playlist_url'. 
        """)
        st.link_button("🎶 Open Playlist in Spotify", spotify_playlist_url, type="primary")


