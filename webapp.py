# webapp.py

import streamlit as st
import asyncio
from backend import Backend, MockBackend # Importeer onze nieuwe klassen

# De class voor de Streamlit UI
class ChatApp:
    def __init__(self, backend):
        self.backend = backend
        st.set_page_config(page_title="Therapy Buddy", layout="centered")

    def run(self):
        st.title("🛋️ Therapy Buddy")
        st.caption("Een AI-gebaseerde gesprekspartner.")

        # Initialiseer de chat-geschiedenis
        if "messages" not in st.session_state:
            st.session_state.messages = []

        # Toon de bestaande berichten
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])

        # Wacht op nieuwe input
        if prompt := st.chat_input("Waar denk je aan?"):
            # Voeg gebruikersbericht toe en toon het
            st.session_state.messages.append({"role": "user", "content": prompt})
            with st.chat_message("user"):
                st.markdown(prompt)

            # Genereer en toon het antwoord van de assistent
            with st.chat_message("assistant"):
                response = self.backend.get_response(prompt)
                st.markdown(response)
            
            # Voeg het antwoord toe aan de geschiedenis
            st.session_state.messages.append({"role": "assistant", "content": response})

# --- Hoofdgedeelte van de applicatie ---
if __name__ == "__main__":
    # KIES WELKE BACKEND JE WILT GEBRUIKEN:
    
    # Optie 1: Gebruik de "nep" backend voor snelle UI-tests
    backend_to_use = Backend()
    
    # Optie 2: Gebruik de "echte" AI-backend (commentarieer de regel hierboven uit en deze in)
    # backend_to_use = Backend()

    # Creëer en draai de app
    app = ChatApp(backend=backend_to_use)
    app.run()