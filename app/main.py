"""
🎄 Fabbrica Elfi AI - Sistema di Gestione Emergenze
Datapizza Christmas AI Challenge 2025
"""

import streamlit as st
import sys
import json
import re
from pathlib import Path
from pydantic import TypeAdapter, ValidationError
from streamlit.runtime.scriptrunner import RerunException
from streamlit.runtime.scriptrunner.script_runner import StopException

# Setup path per importare src
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.config import PAGE_CONFIG, DATA_DIR, ICONS
from src.template_manager import TEMPLATES
from src.database import SessionManager
from src.utils import save_uploaded_file
from src.memory_manager import ConversationMemoryManager
from src.agents.factory import create_multi_agent_system
from src.models import Sostituzione

# Configurazione pagina
st.set_page_config(**PAGE_CONFIG)

# Inizializza managers
session = SessionManager()
memory_manager = ConversationMemoryManager()

# ========================================
# STEP 1: SETUP PANEL
# ========================================
if not session.is_configured():
    st.title("🎄 Benvenuto nella Fabbrica degli Elfi! 🧝")
    st.markdown("### 📋 Configura il sistema")
    
    template_choice = st.selectbox("Template", list(TEMPLATES.keys()))
    
    with st.form("setup_form"):
        uploaded_file = st.file_uploader("Carica orario (.xlsx)", type=['xlsx'])
        
        struttura = st.text_area(
            "Struttura File",
            value=TEMPLATES[template_choice]["struttura"],
            height=150
        )
        
        regole = st.text_area(
            "Regole Sostituzione",
            value=TEMPLATES[template_choice]["regole"],
            height=200
        )
        
        if st.form_submit_button("🚀 Avvia Sistema", use_container_width=True):
            if not uploaded_file:
                st.error("⚠️ Manca il file Excel!")
            else:
                file_path = save_uploaded_file(uploaded_file, DATA_DIR)
                session.setup({
                    "file_path": str(file_path),
                    "file_name": uploaded_file.name,
                    "struttura": struttura,
                    "regole": regole,
                    "template": template_choice
                })
                st.success("✅ Configurato!")
                st.rerun()

# ========================================
# STEP 2: CHAT INTERFACE
# ========================================
else:
    st.title("🎄 Gestione Emergenze fabbrica giocattoli Polo Nord 🧝")
    
    # ---------------------------------------------------------
    # SIDEBAR
    # ---------------------------------------------------------
    with st.sidebar:
        st.success("✅ Sistema configurato")
        st.caption(f"📊 File: `{session.get('file_name')}`")
        
        if st.button("⚙️ Reset e modifica configurazione", use_container_width=True):
            session.reset()
            memory_manager.clear_all()
            st.rerun()
        
        st.markdown("---")
        
        with st.expander("📄 Struttura File"):
            st.text(session.get("struttura"))
        
        with st.expander("📜 Regole Attive"):
            st.text(session.get("regole"))
        
        # Mostra context conversazionale se presente
        if memory_manager.has_substitutions():
            with st.expander("💬 Context Conversazione"):
                ctx_data = st.session_state.get(memory_manager.CONTEXT_KEY, {})
                if ctx_data.get('last_calculation_time'):
                    st.caption(f"⏰ {ctx_data['last_calculation_time'].strftime('%H:%M:%S')}")
                st.info(f"📝 Ultima richiesta: {ctx_data.get('last_request', 'N/A')}")
                st.success(f"✅ {len(memory_manager.get_all_substitutions())} sostituzioni in memoria")
        
        st.markdown("---")
        
        debug_mode = st.checkbox("🔍 Modalità Debug", value=False)
        
        if debug_mode:
            with st.expander("🧪 Session State"):
                st.json(session.get_all())
            
            with st.expander("🧠 Memory Info"):
                st.write(f"Conversazione: {memory_manager.get_conversation_length()} turni")
                st.write(f"Sostituzioni: {len(memory_manager.get_all_substitutions())}")
    
    # ---------------------------------------------------------
    # Chat UI
    # ---------------------------------------------------------
    if st.session_state.messages == []:
        # Salva in chat history
        message_data = {
            "role": "assistant",
            "content": "🎄Ho! Ho! Ho! Sono Babbo Natale! Benvenuto nella mia fabbrica! Qui tra un regalo 🎁 e una pizza 🍕 c'è sempre un po' di trambusto. Dimmi pure, quale intoppo sta preoccupando i miei elfi oggi?"
        }
        st.session_state.messages.append(message_data)
    
    # Mostra messaggi precedenti
    for msg in st.session_state.messages:
        # Seleziona l'icona in base al ruolo del messaggio
        avatar_icon = ICONS.get(msg["role"]) 
        with st.chat_message(msg["role"], avatar=avatar_icon):

            st.markdown(msg["content"])
            
            # Mostra JSON sostituzioni se presenti
            if msg["role"] == "assistant" and "substitutions_data" in msg:
                with st.expander("📊 Dettagli Tecnici Sostituzioni"):
                    st.dataframe(msg["substitutions_data"])
    
    # Input utente
    if prompt := st.chat_input("Es: Ciao, martedì Scintillino è malato..."):
        # Aggiungi messaggio utente
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user", avatar=ICONS["user"]):
            st.markdown(prompt)
        
        with st.chat_message("assistant", avatar=ICONS["assistant"]):
            with st.spinner("Babbo Natale sta pensando..."):
                try:
                    # =========================================
                    # CREA ORCHESTRATOR CON MEMORY
                    # =========================================
                    from src.config import OPENAI_API_KEY
                    
                    memory = memory_manager.get_memory()
                    
                    orchestrator = create_multi_agent_system(
                        api_key=OPENAI_API_KEY,
                        memory=memory
                    )
                    
                    # =========================================
                    # COSTRUISCI PROMPT CON CONTEXT
                    # =========================================
                    full_prompt = f"""
RICHIESTA UTENTE:
{prompt}

STRUTTURA DATI:
{session.get('struttura')}

REGOLE ATTIVE:
{session.get('regole')}

CONTEXT SOSTITUZIONI PRECEDENTI:
"""
                    # Aggiungi context sostituzioni se presenti
                    if memory_manager.has_substitutions():
                        full_prompt += f"""
{memory_manager.get_substitutions_summary()}
"""
                    if debug_mode:
                        st.info("📨 Prompt inviato all'orchestrator")
                        with st.expander("Vedi prompt completo"):
                            st.text(full_prompt)
                    
                    # =========================================
                    # AGGIUNGI USER MESSAGE A MEMORY
                    # =========================================
                    memory_manager.add_user_message(prompt)
                    
                    # =========================================
                    # CHIAMA ORCHESTRATOR
                    # =========================================
                    response = orchestrator.run(full_prompt)
                    
                    if debug_mode:
                        st.write("🔍 Raw response:")
                        st.write(response)
                    
                    # =========================================
                    # ESTRAI RISPOSTA
                    # =========================================
                    #response_text = str(response)
                    raw_text = response.text
                    response_text = raw_text
                    
                    # Cerca JSON
                    json_match = re.search(r'\[.*?\]', raw_text, re.DOTALL)

                    # Pulisci il testo per l'utente (Rimuovi il JSON)
                    #if json_match:
                        # Sostituisci il blocco JSON trovato con una stringa vuota
                    #    clean_text = raw_text.replace(json_match.group(), "").strip()
                        
                        # Opzionale: Rimuovi eventuali frasi di accompagnamento tipo "Ecco il JSON:"
                        # clean_text = re.sub(r'Ecco i dati tecnici:?', '', clean_text, flags=re.IGNORECASE).strip()
                        
                    #    response_out = clean_text
                    #else:
                    #    response_out = raw_text

                    # =========================================
                    # MOSTRA RISPOSTA
                    # =========================================
                    st.markdown(response_text)
                    
                    # =========================================
                    # PARSING JSON SOSTITUZIONI (se presenti)
                    # =========================================
                    substitutions_data = []
                    
                    # Cerca JSON nel formato [...]
                    #json_match = re.search(r'\[.*?\]', response_text, re.DOTALL)
                    if json_match:
                        if debug_mode:
                            print("--- JSON TROVATO ---")
                            print(json_match.group())
                        try:
                            json_str = json_match.group()
                            # Valida con Pydantic
                            adapter = TypeAdapter(list[Sostituzione])
                            validated_subs = adapter.validate_json(json_str)
                            if debug_mode:
                                print(f"--- VALIDAZIONE OK: {len(validated_subs)} items ---")
                            substitutions_data = [s.model_dump() for s in validated_subs]
                            
                            if substitutions_data:
                                try:
                                    # Salva in memory manager
                                    memory_manager.save_calculation_context(
                                        request=prompt,
                                        substitutions=validated_subs
                                    )
                                    if debug_mode:
                                        st.success(f"💾 Salvate {len(substitutions_data)} sostituzioni in memoria")
                                except Exception as e:
                                    print(f"--- ERRORE Salvataggio: {e} ---") #-#

                                # Mostra dettagli tecnici
                                with st.expander("📊 Dettagli Tecnici Sostituzioni"):
                                    st.dataframe(substitutions_data)
                                
                                # Metrics
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Sostituzioni", len(substitutions_data))
                                with col2:
                                    st.metric("Stato", "✅ Completato")
                                with col3:
                                    st.metric("Template", session.get("template", "N/A"))
                        
                        except (json.JSONDecodeError, ValidationError) as e:
                            if debug_mode:
                                st.warning(f"⚠️ JSON trovato ma non valido: {e}")
                    
                    # =========================================
                    # AGGIUNGI ASSISTANT MESSAGE A MEMORY
                    # =========================================
                    memory_manager.add_assistant_message(response_text)
                    
                    # Salva in chat history
                    message_data = {
                        "role": "assistant",
                        "content": response_text
                    }
                    if substitutions_data:
                        message_data["substitutions_data"] = substitutions_data
                    
                    st.session_state.messages.append(message_data)
                    
                    st.rerun()

                except (RerunException, StopException):
                    raise

                except Exception as e:
                    error_msg = f"❌ Errore sistema: {str(e)}"
                    st.error(error_msg)
                    
                    if debug_mode:
                        import traceback
                        st.code(traceback.format_exc())
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })