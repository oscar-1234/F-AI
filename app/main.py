"""
🎄 Fabbrica Elfi AI - Sistema di Gestione Emergenze
Datapizza Christmas AI Challenge 2025
"""

import streamlit as st
import sys
import json
import re
from pathlib import Path

# Setup path per importare src
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))

from src.models import Sostituzione
from pydantic import TypeAdapter, ValidationError
from src.config import PAGE_CONFIG
from src.template_manager import TEMPLATES
from src.database import SessionManager
from src.agents import create_code_generator_agent, create_narrator_agent
from src.utils import save_uploaded_file

# Configurazione pagina
st.set_page_config(**PAGE_CONFIG)
session = SessionManager()

# ========================================
# STEP 1: WIZARD SETUP
# ========================================
if not session.is_configured():
    st.title("🎄 Benvenuto nella Fabbrica degli Elfi!")
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
                file_path = save_uploaded_file(uploaded_file, "app/data")
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
    st.title("🎄 Gestione Emergenze Polo Nord")
    
    # ---------------------------------------------------------
    # SIDEBAR
    # ---------------------------------------------------------
    with st.sidebar:
        st.success("✅ Sistema configurato")
        st.caption(f"📊 File: `{session.get('file_name')}`")
        
        if st.button("⚙️ Modifica Configurazione", use_container_width=True):
            session.reset()
            st.rerun()
        
        st.markdown("---")
        
        with st.expander("📄 Struttura File"):
            st.text(session.get("struttura"))
        
        with st.expander("📜 Regole Attive"):
            st.text(session.get("regole"))
        
        st.markdown("---")
        debug_mode = st.checkbox("🔍 Modalità Debug", value=False)
        
        if debug_mode:
            with st.expander("🧪 Session State"):
                st.json(session.get_all())
    
    # ---------------------------------------------------------
    # Chat UI
    # ---------------------------------------------------------
    if "messages" not in st.session_state:
        st.session_state.messages = []
    
    for msg in st.session_state.messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if debug_mode and "metadata" in msg:
                st.json(msg["metadata"])
    
    if prompt := st.chat_input("Es: Oggi Scintillino è malato..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Context per l'agente
        full_context = f"""
HAI UN NUOVO COMPITO:
{prompt}

REGOLE DI SOSTITUZIONE ATTIVE:
{session.get('regole')}

ISTRUZIONI PER L'AGENTE:
1. Scrivi la funzione `calcola_sostituzioni(df)` in Python.
2. Usa il tool `execute_code_in_sandbox`.
3. Non preoccuparti del caricamento file: il tool caricherà automaticamente il file corretto nella variabile `df`.
4. Se ottieni un risultato valido (JSON con le sostituzioni), RESTITUISCILO IMMEDIATAMENTE come risposta finale.
5. NON scrivere spiegazioni tipo "Ecco fatto" o "Ho corretto l'errore".
6. La tua risposta finale DEVE essere SOLTANTO il JSON/Lista dei dati.
"""
        
        with st.chat_message("assistant"):
            with st.spinner("Babbo Natale sta gestendo l'emergenza..."):
                try:
                    code_agent = create_code_generator_agent()
                    narrator_agent = create_narrator_agent()
                    
                    # Esecuzione Agente
                    raw_response = code_agent.run(full_context)
                    
                    if debug_mode:
                        st.write("🔍 Raw response:", raw_response)
                    
                    # ====================================================
                    # PARSING DATAPIZZA (TextBlock → JSON → Pydantic)
                    # ====================================================
                    final_data = []
                    
                    # 1. Estrai content da StepResult
                    if hasattr(raw_response, 'content') and isinstance(raw_response.content, list):
                        if len(raw_response.content) > 0:
                            first_block = raw_response.content[0]
                            if hasattr(first_block, 'content'):
                                content_to_parse = first_block.content
                            elif hasattr(first_block, 'text'):
                                content_to_parse = first_block.text
                            else:
                                content_to_parse = str(first_block)
                        else:
                            content_to_parse = str(raw_response)
                    else:
                        content_to_parse = str(raw_response)
                    
                    if debug_mode:
                        st.write(f"📝 Contenuto estratto: {str(content_to_parse)[:300]}...")
                    
                    # 2. Pulizia Markdown
                    if isinstance(content_to_parse, str):
                        content_to_parse = content_to_parse.replace('```json', '').replace('```', '').strip()
                    
                    # 3. Validazione Pydantic
                    try:
                        adapter = TypeAdapter(list[Sostituzione])
                        if isinstance(content_to_parse, str):
                            final_data_objs = adapter.validate_json(content_to_parse)
                        else:
                            final_data_objs = adapter.validate_python(content_to_parse)
                        final_data = [obj.model_dump() for obj in final_data_objs]
                        
                        if debug_mode:
                            st.success(f"✅ {len(final_data)} sostituzioni validate")
                    
                    except Exception as e:
                        st.error(f"⚠️ Errore validazione: {type(e).__name__}")
                        if debug_mode:
                            st.error(str(e))
                        final_data = []
                    
                    # ====================================================
                    # FINE PARSING
                    # ====================================================
                    
                    if not final_data:
                        msg = "⚠️ Non sono riuscito a calcolare sostituzioni valide."
                        if debug_mode:
                            msg += f"\n\nContenuto grezzo:\n{content_to_parse}"
                        st.error(msg)
                    else:
                        # Narrazione
                        story_prompt = f"""
Crea una breve storia natalizia (max 150 parole) basata su queste sostituzioni:
{json.dumps(final_data, ensure_ascii=False)}
"""
                        story_response = narrator_agent.run(story_prompt)
                        
                        # Estrai testo dalla risposta del narrator
                        if hasattr(story_response, 'content') and isinstance(story_response.content, list):
                            if len(story_response.content) > 0 and hasattr(story_response.content, 'content'):
                                story = story_response.content.content
                            else:
                                story = str(story_response)
                        elif hasattr(story_response, 'text'):
                            story = story_response.text
                        else:
                            story = str(story_response)
                        
                        st.markdown(story)
                        
                        with st.expander("📊 Dettagli Tecnici Sostituzioni"):
                            st.dataframe(final_data)
                        
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": story,
                            "metadata": final_data
                        })
                        
                        # Metrics
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            st.metric("Sostituzioni", len(final_data))
                        with col2:
                            st.metric("Stato", "✅ Completato")
                        with col3:
                            st.metric("Template", session.get("template", "N/A"))
                
                except Exception as e:
                    st.error(f"❌ Errore sistema: {str(e)}")
                    if debug_mode:
                        import traceback
                        st.code(traceback.format_exc())
