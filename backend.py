# backend.py


import asyncio
import os
from dotenv import load_dotenv

# Importeer alle benodigde LangChain en Pydantic classes
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_community.vectorstores import FAISS
from pydantic import BaseModel, Field

# --- Definieer de Pydantic structuur voor de analyse ---
class StateAnalysis(BaseModel):
    state: str = Field(description="De geschatte AEDP-staat of afweer van de gebruiker.")
    reasoning: str = Field(description="Een korte redenering voor de gekozen staat.")

# --- De ECHTE Backend Class ---
class Backend:
    def __init__(self):
        """Initialiseert alle modellen en chains. Dit gebeurt maar één keer."""
        asyncio.set_event_loop(asyncio.new_event_loop())
        load_dotenv()
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("API-sleutel niet gevonden in .env")

        # CHECK OF INDEX BESTAAT, ANDERS BOUWEN
        if not os.path.exists("faiss_index"):
            print("FAISS index niet gevonden, bezig met bouwen...")
            # De logica van build_vectorstore.py hierin verwerkt
            from langchain_text_splitters import CharacterTextSplitter
            with open("AEDP_KB.txt", "r", encoding="utf-8") as f:
                text = f.read()
            text_splitter = CharacterTextSplitter(separator="---", chunk_size=1000, chunk_overlap=200)
            docs = text_splitter.create_documents([text])
            # --- DEBUGGING STAP: Controleer of er documenten zijn gemaakt ---
            if not docs:
                raise ValueError("De text_splitter heeft geen documenten kunnen maken. Controleer of 'AEDP_KB.txt' niet leeg is en het '---' scheidingsteken bevat.")
            
            vector_store = FAISS.from_documents(docs, embeddings)
            vector_store.save_local("faiss_index")
            print("FAISS index gebouwd en opgeslagen.")

        # Laad de FAISS index en initialiseer retriever
        embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001", google_api_key=api_key)
        vector_store = FAISS.load_local("faiss_index", embeddings, allow_dangerous_deserialization=True)
        self.retriever = vector_store.as_retriever(search_kwargs={"k": 1})
        
        # Initialiseer het chatmodel
        self.model = ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=api_key)
        
        # Initialiseer de analyse-chain
        parser = PydanticOutputParser(pydantic_object=StateAnalysis)
        analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", "Jij bent een expert-analist in AEDP... (zelfde analyse-prompt) {format_instructions}"),
            ("human", "{user_input}")
        ])
        self.analysis_chain = analysis_prompt | self.model | parser

    def get_response(self, user_input: str) -> str:
        """Voert de volledige RAG-workflow uit en geeft het antwoord van de AI terug."""
        # 1. Analyseer
        analysis_result = self.analysis_chain.invoke({
            "user_input": user_input, "format_instructions": PydanticOutputParser(pydantic_object=StateAnalysis).get_format_instructions()
        })

        # 2. Haal strategie op
        retrieved_docs = self.retriever.invoke(analysis_result.state)
        retrieved_strategy = retrieved_docs[0].page_content

        # 3. Genereer antwoord
        system_prompt_persona = "Jij bent een AI 'Therapy Buddy'. Je bent empathisch, niet-oordelend en altijd gericht op het creëren van veiligheid. Spreek altijd in een warme, ondersteunende en natuurlijke toon."
        final_prompt_instruction = f"""
        Je bent nu in een direct gesprek met de gebruiker. Je interne analyse, gebaseerd op AEDP-principes, is als volgt: '{retrieved_strategy}'.

        Gebruik dit inzicht om een KORT, warm en empathisch antwoord te formuleren. 
        Spreek DIRECT en alleen tegen de gebruiker. 
        Begin NIET met zinnen als "Op basis van mijn analyse...". 
        Noem de strategie of je interne proces NIET. 
        Je antwoord moet een uitnodiging zijn voor de gebruiker om verder te praten.
        """

        final_prompt = [
            SystemMessage(content=system_prompt_persona),
            HumanMessage(content=user_input), # We gebruiken de originele input van de gebruiker
            SystemMessage(content=final_prompt_instruction)
        ]
        response = self.model.invoke(final_prompt)
        return response.content

# --- De "NEP" Backend Class voor snelle UI-ontwikkeling ---
class MockBackend:
    def get_response(self, user_input: str) -> str:
        """Simuleert een antwoord van de AI zonder API-aanroep."""

        return f"Je zei: '{user_input}'. Dit is een test-antwoord van de Mock Backend."



