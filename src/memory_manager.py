"""
Gestione memoria conversazionale per sistema multi-agente.
Integra datapizza.memory.Memory con Streamlit session state.
"""

import streamlit as st
from typing import Optional, List, Dict, Any
from datetime import datetime
from datapizza.memory import Memory
from datapizza.type import ROLE, TextBlock
from src.models import Sostituzione
import json


class ConversationMemoryManager:
    """
    Wrapper per datapizza.Memory integrato con Streamlit session state.
    Mantiene sia la memoria conversazionale che il context applicativo.
    """
    
    # Chiavi per session state
    MEMORY_KEY = "datapizza_memory"
    CONTEXT_KEY = "app_context"
    
    def __init__(self):
        """Inizializza o recupera Memory da session state"""
        self._init_session_state()
    
    def _init_session_state(self):
        """Inizializza le chiavi necessarie in session state"""
        if self.MEMORY_KEY not in st.session_state:
            # Crea nuova Memory datapizza
            st.session_state[self.MEMORY_KEY] = Memory()
        
        if self.CONTEXT_KEY not in st.session_state:
            # Context applicativo (non parte della memory LLM)
            st.session_state[self.CONTEXT_KEY] = {
                "all_substitutions": [],
                "last_request": "",
                "last_calculation_time": None
            }
    
    def get_memory(self) -> Memory:
        """
        Restituisce l'oggetto Memory datapizza corrente
        
        Returns:
            Memory: Oggetto Memory con la storia conversazionale
        """
        return st.session_state[self.MEMORY_KEY]
    
    def add_user_message(self, content: str):
        """
        Aggiunge un messaggio utente alla memoria
        
        Args:
            content: Testo del messaggio utente
        """
        memory = self.get_memory()
        text_block = TextBlock(content=content)
        memory.add_turn(text_block, role=ROLE.USER)
    
    def add_assistant_message(self, content: str):
        """
        Aggiunge un messaggio assistant alla memoria
        
        Args:
            content: Testo della risposta assistant
        """
        memory = self.get_memory()
        text_block = TextBlock(content=content)
        memory.add_turn(text_block, role=ROLE.ASSISTANT)

    def save_calculation_context(
        self,
        request: str,
        substitutions: List[Sostituzione]
    ):
        """
        Salva (APPEND) il context di un calcolo nel context applicativo.
        Mantiene le sostituzioni precedenti.

        Args:
            request: La richiesta dell'utente
            substitutions: Lista di sostituzioni calcolate (Pydantic models)
        """
        # Recupera sostituzioni esistenti
        current_subs = st.session_state[self.CONTEXT_KEY].get("all_substitutions", [])
        
        # Prepara le nuove
        new_subs = [s.model_dump() for s in substitutions]
        
        # Unisci le liste
        # (Opzionale: potrei rimuovere duplicati, ma per ora append è più sicuro)
        updated_subs = current_subs + new_subs
        
        # Aggiorna lo stato
        st.session_state[self.CONTEXT_KEY].update({
            "all_substitutions": updated_subs,
            "last_request": request,
            "last_calculation_time": datetime.now()
        })

    def get_all_substitutions(self) -> List[Dict[str, Any]]:
        """
        Recupera le ultime sostituzioni calcolate
        
        Returns:
            Lista di dizionari con le sostituzioni
        """
        return st.session_state[self.CONTEXT_KEY].get("all_substitutions", [])
    
    def has_substitutions(self) -> bool:
        """
        Verifica se esistono sostituzioni in memoria
        
        Returns:
            True se ci sono sostituzioni salvate
        """
        return len(self.get_all_substitutions()) > 0
    
    def get_substitutions_summary(self) -> str:
        """
        Crea un summary testuale delle sostituzioni per context degli agenti
        
        Returns:
            Stringa formattata con il summary
        """
        subs = self.get_all_substitutions()
        if not subs:
            return "Nessuna sostituzione calcolata in precedenza."
        
        ctx = st.session_state[self.CONTEXT_KEY]
        summary = f"**Ultima richiesta**: {ctx.get('last_request', 'N/A')}\n"
        summary += f"**Calcolo**: {ctx.get('last_calculation_time', 'N/A')}\n"
        summary += f"**Sostituzioni calcolate** ({len(subs)}):\n\n"
        
        for i, s in enumerate(subs, 1):
            summary += f"{i}. {s['assente']} ({s['reparto']}, {s['giorno']} ora {s['ora']}) "
            summary += f"→ {s['sostituto']} [{s['regola_applicata']}]\n"
            if s.get('reasoning'):
                summary += f"   Reasoning: {s['reasoning']}\n"
        
        return summary
    
    
    def clear_all(self):
        """Reset completo: memory conversazionale + context applicativo"""
        st.session_state[self.MEMORY_KEY] = Memory()
        st.session_state[self.CONTEXT_KEY] = {
            "all_substitutions": [],
            "last_request": "",
            "last_calculation_time": None
        }
    
    def get_conversation_length(self) -> int:
        """
        Restituisce il numero di turni nella conversazione
        """
        memory = self.get_memory()
        try:
            if hasattr(memory, 'to_dict'):
                data = memory.to_dict()
                return len(data)
            else:
                return 0
        except:
            return 0