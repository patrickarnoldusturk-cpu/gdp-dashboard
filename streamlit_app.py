import streamlit as st
import pandas as pd
import json
import base64

# App configuratie
st.set_page_config(page_title="Liquicity Festival Planner 2026", page_icon="🚀", layout="wide")
st.title("🚀 De Kogelvrije Liquicity Festival Planner")
st.write("Plan jullie festivalweekend 100% stabiel en crashvrij!")

# ==========================================
# 🔐 TEXT-CODE SYNCHRONISATIE (CRASHVRIJ)
# ==========================================
standaard_data = {
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

if 'groeps_data' not in st.session_state:
    st.session_state.groeps_data = standaard_data.copy()

# --- SIDEBAR: DE UPDATER & NAVIGATIE ---
st.sidebar.header("🔄 Groeps-Update")
import_code = st.sidebar.text_area("Plak hier de nieuwste code van de WhatsApp-groep:", key="sb_import_code_input")

if st.sidebar.button("📥 Update Mijn App", key="sb_update_trigger_btn"):
    if import_code:
        try:
            gedecodeerd = base64.b64decode(import_code.strip()).decode('utf-8')
            st.session_state.groeps_data = json.loads(gedecodeerd)
            st.sidebar.success("App succesvol bijgewerkt!")
            st.rerun()
        except Exception:
            st.sidebar.error("Ongeldige code! Zorg dat je de hele tekst kopieert.")

st.sidebar.write("---")
st.sidebar.header("👥 Wie gaat er mee?")
nieuwe_naam = st.sidebar.text_input("Naam van nieuwe festivalganger:", key="sb_nieuwe_naam_input")

if st.sidebar.button("➕ Voeg mij toe", key="sb_add_person_btn"):
    if nieuwe_naam and nieuwe_naam.strip() != "":
        s_naam = nieuwe_naam.strip()
        if s_naam not in st.session_state.groeps_data["vrienden"]:
            st.session_state.groeps_data["vrienden"].append(s_naam)
            st.sidebar.success(f"{s_naam} toegevoegd!")
            st.rerun()
        else:
            st.sidebar.warning("Deze naam staat al in de lijst!")

st.sidebar.write("**Huidige groep:**", ", ".join(st.session_state.groeps_data["vrienden"]))

st.sidebar.write("---")
st.sidebar.header("📂 Menu Planner")
gekozen_menu = st.sidebar.radio(
    "Ga naar:",
    ["🗓️ Welk Festival/Weekend?", "💶 Tickets & Spullen Kosten", "🎵 Timetable / Line-up", 
     "🧳 Groeps-Paklijst", "🚗 Uber naar Festival", "📸 Google Foto's", "🎵 Groeps-Playlist"],
    key="sb_navigation_radio"
)

g_data = st.session_state.groeps_data
# ==========================================
# PAGINA 1: DATUMS / FESTIVALS PRIKKEN
# ==========================================
if gekozen_menu == "🗓️ Welk Festival/Weekend?":
    st.header("Welk festival weekend gaan we pakken?")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Jouw voorkeur doorgeven")
        naam = st.selectbox("Wie ben je?", g_data["vrienden"], key="p1_user_selectbox")
        opties = ["Volledig Liquicity Weekend 2026", "Alleen Vrijdag", "Alleen Zaterdag", "Alleen Zondag"]
        
        huidige_voorkeur = g_data["datums"].get(naam, [])
        
        # CRASH FIX: We halen de dynamische key weg bij de widget en slaan pas op bij de submit
        with st.form(key="form_dates_isolated"):
            gekozen_datums = st.multiselect("Welke festivals/weekenden kun jij?", opties, default=huidige_voorkeur)
            submit_dates = st.form_submit_button("Voorkeur Opslaan")
            
            if submit_dates:
                st.session_state.groeps_data["datums"][naam] = gekozen_datums
                st.success("Voorkeur opgeslagen!")
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
            st.info("Nog geen stemmen uitgebracht.")

# ==========================================
# PAGINA 2: KOSTEN VERREKENEN
# ==========================================
elif gekozen_menu == "💶 Tickets & Spullen Kosten":
    st.header("💶 Festival Pot (Tickets, Drank, Muntjes)")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Nieuwe festivaluitgave invoeren")
        
        with st.form(key="form_add_expense_isolated"):
            wie_betaalt = st.selectbox("Wie heeft betaald?", g_data["vrienden"])
            bedrag = st.number_input("Bedrag (€)", min_value=0.0, step=0.01, value=0.0)
            omschrijving = st.text_input("Waarvoor? (bijv. 'Combi-tickets')")
            submit_expense = st.form_submit_button("Uitgave Toevoegen")
            
            if submit_expense:
                if bedrag > 0 and omschrijving:
                    st.session_state.groeps_data["uitgaven"].append({"Wie": wie_betaalt, "Bedrag": bedrag, "Omschrijving": omschrijving})
                    st.success("Uitgave toegevoegd!")
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
            
            with st.form(key="form_delete_expense_isolated"):
                opties_verwijderen = [f"{i}: {u['Wie']} - €{u['Bedrag']} ({u['Omschrijving']})" for i, u in enumerate(g_data["uitgaven"])]
                te_verwijderen = st.selectbox("Welke uitgave wil je wissen?", opties_verwijderen)
                submit_delete = st.form_submit_button("🔴 Geselecteerde uitgave wissen")
                
                if submit_delete:
                    index_to_delete = int(te_verwijderen.split(":"))
                    st.session_state.groeps_data["uitgaven"].pop(index_to_delete)
                    st.success("Uitgave verwijderd!")
                    st.rerun()
        else:
            st.info("Nog geen groepsuitgaven ingevoerd.")
# ==========================================
# PAGINA 3: TIMETABLE / LINE-UP
# ==========================================
elif gekozen_menu == "🎵 Timetable / Line-up":
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
        kiezende_vriend = st.selectbox("Wie ben je?", g_data["vrienden"], key="p3_vriend_select")
        
        # CRASH FIX: De checkboxes hebben nu een unieke, tijdelijke naam per act en slaan pas op bij submit
        with st.form(key="form_timetable_isolated"):
            tijdelijke_vinkjes = {}
            for act in liquicity_acts:
                a_naam = act["Artiest"]
                al_gevinkt = kiezende_vriend in g_data["timetable"].get(a_naam, [])
                tijdelijke_vinkjes[a_naam] = st.checkbox(f"⏱️ {act['Tijd']} | **{a_naam}** ({act['Stage']})", value=al_gevinkt)
                
            submit_timetable = st.form_submit_button("Mijn Line-up Voorkeuren Opslaan", type="primary")
            
            if submit_timetable:
                for act in liquicity_acts:
                    a_naam = act["Artiest"]
                    if a_naam not in st.session_state.groeps_data["timetable"]:
                        st.session_state.groeps_data["timetable"][a_naam] = []
                    
                    vinkje = tijdelijke_vinkjes[a_naam]
                    if vinkje and kiezende_vriend not in st.session_state.groeps_data["timetable"][a_naam]:
                        st.session_state.groeps_data["timetable"][a_naam].append(kiezende_vriend)
                    elif not vinkje and kiezende_vriend in st.session_state.groeps_data["timetable"][a_naam]:
                        st.session_state.groeps_data["timetable"][a_naam].remove(kiezende_vriend)
                st.success("Timetable bijgewerkt!")
                st.rerun()
            
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
# PAGINA 4: GROEPS-PAKLIJST
# ==========================================
elif gekozen_menu == "🧳 Groeps-Paklijst":
    st.header("🧳 Wie takes what?")
    vrienden_lijst = ["Niemand"] + g_data["vrienden"]
    
    # CRASH FIX: Geen harde index-keys meer aan de widgets gekoppeld
    with st.form(key="form_paklijst_isolated"):
        tijdelijke_wie = []
        tijdelijke_done = []
        
        for i, item in enumerate(g_data["paklijst"]):
            col_a, col_b, col_c = st.columns(3)
            with col_a: 
                st.write(f"🔹 **{item['Item']}**")
            with col_b: 
                h_idx = vrienden_lijst.index(item['Wie']) if item['Wie'] in vrienden_lijst else 0
                tijdelijke_wie.append(st.selectbox(f"Wie voor {item['Item']}?", vrienden_lijst, index=h_idx))
            with col_c: 
                tijdelijke_done.append(st.checkbox(f"Ingepakt ({item['Item']})", value=item['Ingepakt']))
                
        submit_packing = st.form_submit_button("💾 Sla Checklist Wijzigingen Op")
        
        if submit_packing:
            for i in range(len(st.session_state.groeps_data["paklijst"])):
                st.session_state.groeps_data["paklijst"][i]['Wie'] = tijdelijke_wie[i]
                st.session_state.groeps_data["paklijst"][i]['Ingepakt'] = tijdelijke_done[i]
            st.success("Paklijst succesvol bijgewerkt!")
            st.rerun()

elif gekozen_menu == "🎵 Groeps-Playlist":
    st.header("🎵 Onze Gezamenlijke Liquicity Playlist")
    st.write("Luister direct naar de playlist of voeg zelf je favoriete Drum & Bass tracks toe!")
    
    # De directe link naar jouw afspeellijst
    spotify_playlist_url = "https://spotify.com"
    
    # FIX: st.video omzeilt de X-Frame-Options blokkade van open.spotify.com volledig!
    st.video(spotify_playlist_url)
    
    st.write("---")
    st.link_button("🎶 Open Playlist in Spotify-App", spotify_playlist_url, type="primary")


# ==========================================
# 📋 GENERATOR ONDERIN VOOR DE DEELLINK
# ==========================================
st.write("---")
st.subheader("📋 De Actuele Groeps-Deelcode")
st.write("Klik op de knop hieronder om de nieuwste code voor WhatsApp te genereren.")

if st.button("🔗 Genereer Nieuwe WhatsApp Code", key="generate_share_code_btn_isolated"):
    json_bytes = json.dumps(g_data).encode('utf-8')
    deel_code = base64.b64encode(json_bytes).decode('utf-8')
    st.text_area("Kopieer deze code:", value=deel_code, height=100, key="bottom_share_code_textarea_isolated")
    st.success("Code succesvol gegenereerd!")
