import streamlit as st
import os

# --- Deze app helpt bij het debuggen van bestandspaden in Streamlit ---

st.title("🔍 Bestands- en Pad Debugger")

# --- STAP 1: Toon de huidige werkmap ---
st.header("1. Waar 'kijkt' de Streamlit-app op dit moment?")
try:
    # Haal de huidige werkmap op
    current_working_directory = os.getcwd()
    st.write("De app is opgestart vanuit de volgende map:")
    st.code(current_working_directory, language="bash")
except Exception as e:
    st.error(f"Kon de huidige werkmap niet ophalen: {e}")

# --- STAP 2: Toon de bestanden in die map ---
st.header("2. Welke bestanden ziet de app in die map?")
try:
    # Haal de lijst met bestanden en mappen op
    files_in_directory = os.listdir(current_working_directory)
    st.write(f"De app ziet de volgende {len(files_in_directory)} items:")
    # Maak een nette string van de lijst voor weergave
    files_str = "\n".join(f"- {item}" for item in files_in_directory)
    st.code(files_str, language="bash")
except Exception as e:
    st.error(f"Kon de bestanden in de map niet lezen: {e}")

# --- STAP 3: Probeer het specifieke bestand te lezen ---
st.header("3. Poging om 'AEDP_KB.txt' te lezen en te splitsen")
filename = "AEDP_KB.txt"

# Controleer of het bestand bestaat op deze locatie
if os.path.exists(os.path.join(current_working_directory, filename)):
    st.success(f"[SUCCES] Het bestand '{filename}' is gevonden in de werkmap!")
    try:
        with open(os.path.join(current_working_directory, filename), "r", encoding="utf-8") as f:
            content = f.read()
            
            st.write("Inhoud van het bestand is succesvol gelezen.")
            
            if "---" in content:
                st.success("[SUCCES] Het scheidingsteken '---' is gevonden in de inhoud!")
                parts = content.split("---")
                st.info(f"Het bestand is opgesplitst in {len(parts)} delen.")
            else:
                st.error("[FOUT] Het scheidingsteken '---' kon NIET worden gevonden in de gelezen inhoud!")

    except Exception as e:
        st.error(f"[FOUT] Er ging iets mis bij het lezen van het bestand: {e}")
else:
    st.error(f"[FOUT] Het bestand '{filename}' kon NIET worden gevonden in de werkmap hierboven.")
    st.warning("Zorg ervoor dat 'AEDP_KB.txt' in dezelfde map staat als je scripts.")
