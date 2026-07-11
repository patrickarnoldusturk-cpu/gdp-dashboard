import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection
import urllib.parse
import datetime
import re

# App configuratie
st.set_page_config(page_title="Liquicity Festival Planner 2026", page_icon="🚀", layout="wide")
st.title("🚀 De Ultieme Liquicity Festival Planner")
st.write("Jouw vriendengroep festival-proof geautomatiseerd via Google Sheets cloud-opslag.")

# ==========================================
# 📊 CLOUD DATABASE KOPPELING
# ==========================================
# ⚠️ VERVANG DE LINK HIERONDER DOOR JULLIE EIGEN GOOGLE SHEET URL (VANUIT DE ADRESBALK)!
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/15WF6H64eQKCye-YaSBS1xEDOjCa_MUV8rBCUYNL5E9Y/edit?gid=0#gid=0"

# De verbinding instellen in de geheime instellingen van Streamlit
st.secrets["connections"] = {"gsheets": {"spreadsheet": GOOGLE_SHEET_URL}}

# Maak verbinding met Google Sheets
try:
    conn = st.connection("gsheets", type=GSheetsConnection)
except Exception:
    st.error("Databaseverbinding mislukt. Of de link klopt niet, of de sheet staat niet open op 'Bewerker' voor iedereen!")

# --- FUNCTIES OM DATA LIVE OP TE SLAAN EN OP TE HALEN ---
def haal_data_op(sheet_name, standaard_kolommen, standaard_data=None):
    try:
        df = conn.read(worksheet=sheet_name, ttl=0)
        if df is None or df.empty:
            return pd.DataFrame(standaard_data if standaard_data else [], columns=standaard_kolommen)
        # Zorg dat alle benodigde kolommen erin zitten
        for col in standaard_kolommen:
            if col not in df.columns:
                df[col] = ""
        return df
    except Exception:
        return pd.DataFrame(standaard_data if standaard_data else [], columns=standaard_kolommen)

def sla_data_op(df, sheet_name):
    try:
        # Zorg dat lege cellen netjes als tekst worden opgeslagen
        df_saved = df.fillna("")
        conn.update(worksheet=sheet_name, data=df_saved)
        st.cache_data.clear()
    except Exception as e:
        st.error(f"Fout bij opslaan in de cloud: {e}")

# --- CENTRALE DATA LIVE INLADEN UIT DE CLOUD ---
df_vrienden = haal_data_op("Vrienden", ["Naam"], [{"Naam": "Patrick"}, {"Naam": "Annika"}, {"Naam": "Harland"}, {"Naam": "Richard"}, {"Naam": "Dirk"}, {"Naam": "Van Brakel"}])
vrienden_lijst = df_vrienden["Naam"].dropna().tolist()
vrienden_lijst = [name for name in vrienden_lijst if str(name).strip() != ""]

df_datums = haal_data_op("Datums", ["Wie", "Festival"])
df_uitgaven = haal_data_op("Uitgaven", ["Wie", "Bedrag", "Omschrijving"])
df_timetable = haal_data_op("Timetable", ["Artiest", "Wie"])

standaard_paklijst = [
    {"Item": "Partytent", "Wie": "Niemand", "Ingepakt": "Nee"},
    {"Item": "Koelbox + Koelementen", "Wie": "Niemand", "Ingepakt": "Nee"},
    {"Item": "Bluetooth Speaker", "Wie": "Niemand", "Ingepakt": "Nee"},
    {"Item": "Ducttape", "Wie": "Niemand", "Ingepakt": "Nee"},
    {"Item": "Kaartspel / Drankspellen", "Wie": "Niemand", "Ingepakt": "Nee"}
]
df_paklijst = haal_data_op("Paklijst", ["Item", "Wie", "Ingepakt"], standaard_paklijst)

# --- SIDEBAR: NIEUWE VRIEND TOEVOEGEN ---
st.sidebar.header("👥 Wie gaat er mee?")
nieuwe_naam = st.sidebar.text_input("Naam van nieuwe festivalganger:")
if st.sidebar.button("➕ Voeg mij toe aan de groep"):
    if nieuwe_naam and nieuwe_naam not in vrienden_lijst:
        nieuw_row = pd.DataFrame([{"Naam": nieuwe_naam}])
        df_vrienden = pd.concat([df_vrienden, nieuw_row], ignore_index=True)
        sla_data_op(df_vrienden, "Vrienden")
        st.sidebar.success(f"{nieuwe_naam} is toegevoegd!")
        st.rerun()
    elif nieuwe_naam in vrienden_lijst:
        st.sidebar.warning("Deze naam staat al in de lijst!")

st.sidebar.write("**Huidige groep:**", ", ".join(vrienden_lijst))
st.sidebar.write("---")

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
        naam = st.selectbox("Wie ben je?", vrienden_lijst, key="datum_naam")
        opties = ["Volledig Liquicity Weekend 2026", "Alleen Vrijdag", "Alleen Zaterdag", "Alleen Zondag"]
        gekozen_datums = st.multiselect("Welke festivals/weekenden kun jij?", opties)
        if st.button("Voorkeur Opslaan"):
            df_datums = df_datums[df_datums["Wie"] != naam]
            nieuwe_stemmen = pd.DataFrame([{"Wie": naam, "Festival": f} for f in gekozen_datums])
            df_datums = pd.concat([df_datums, nieuwe_stemmen], ignore_index=True)
            sla_data_op(df_datums, "Datums")
            st.success("Voorkeuren opgeslagen in de cloud!")
            st.rerun()
            
    with col2:
        st.subheader("📊 Live Stemresultaten")
        if not df_datums.empty and "Festival" in df_datums.columns and "Wie" in df_datums.columns:
            df_datums["Aantal"] = 1
            st.bar_chart(data=df_datums, x="Festival", y="Aantal", color="Wie", stack=True)
            st.write("**Gedetailleerd overzicht:**")
            for p in vrienden_lijst:
                p_stemmen = df_datums[df_datums["Wie"] == p]["Festival"].tolist()
                if p_stemmen:
                    st.write(f"• **{p}** heeft gestemd op: {', '.join(p_stemmen)}")
        else:
            st.info("Nog geen cloud-stemmen uitgebracht.")

# ==========================================
# TAB 2: KOSTEN VERREKENEN
# ==========================================
with tab2:
    st.header("💶 Festival Pot (Tickets, Drank, Muntjes)")
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Nieuwe festivaluitgave invoeren")
        wie_betaalt = st.selectbox("Wie heeft betaald?", vrienden_lijst, key="kosten_wie")
        bedrag = st.number_input("Bedrag (€)", min_value=0.0, step=0.01, value=0.0)
        omschrijving = st.text_input("Waarvoor? (bijv. 'Combi-tickets', 'Campingboodschappen')")
        if st.button("Uitgave Toevoegen"):
            if bedrag > 0 and omschrijving:
                nieuwe_uitgave = pd.DataFrame([{"Wie": wie_betaalt, "Bedrag": bedrag, "Omschrijving": omschrijving}])
                df_uitgaven = pd.concat([df_uitgaven, nieuwe_uitgave], ignore_index=True)
                sla_data_op(df_uitgaven, "Uitgaven")
                st.success("Uitgave opgeslagen in de cloud!")
                st.rerun()

    with col2:
        st.subheader("📈 Tussenstand & Balans")
        if not df_uitgaven.empty:
            df_uitgaven["Bedrag"] = df_uitgaven["Bedrag"].astype(float)
            st.dataframe(df_uitgaven, hide_index=True)
            totaal = df_uitgaven["Bedrag"].sum()
            per_persoon = totaal / len(vrienden_lijst) if vrienden_lijst else 0
            st.metric("Totale kosten festival", f"€ {totaal:.2f}")
            st.metric("Kosten per persoon", f"€ {per_persoon:.2f}")
            
            balans = {vriend: -per_persoon for vriend in vrienden_lijst}
            for _, u in df_uitgaven.iterrows():
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
            opties_verwijderen = [f"{i}: {row['Wie']} - €{row['Bedrag']} ({row['Omschrijving']})" for i, row in df_uitgaven.iterrows()]
            te_verwijderen = st.selectbox("Welke uitgave wil je wissen?", opties_verwijderen)
            if st.button("🔴 Geselecteerde uitgave wissen"):
                index_to_delete = int(te_verwijderen.split(":"))
                df_uitgaven = df_uitgaven.drop(index_to_delete).reset_index(drop=True)
                sla_data_op(df_uitgaven, "Uitgaven")
                st.success("Uitgave verwijderd uit de cloud!")
                st.rerun()
        else:
            st.info("Nog geen uitgaven opgeslagen in de cloud.")

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
        kiezende_vriend = st.selectbox("Wie ben je?", vrienden_lijst, key="timetable_persoon")
        
        if st.button("Mijn Line-up Voorkeuren Opslaan", type="primary"):
            df_timetable = df_timetable[df_timetable["Wie"] != kiezende_vriend]
            nieuwe_vinkjes = []
            for act in liquicity_acts:
                if st.session_state.get(f"v_{act['Artiest']}_{kiezende_vriend}"):
                    nieuwe_vinkjes.append({"Artiest": act["Artiest"], "Wie": kiezende_vriend})
