"""
Gestione dello stato della sessione Streamlit
"""

import streamlit as st
from typing import Any, Dict, Optional
from datetime import datetime

from .models import ConfigSetup

class SessionManager:
    """Gestisce lo stato della sessione Streamlit in modo type-safe"""
   
    def __init__(self):
        """Inizializza session state se non esiste"""
        if "config" not in st.session_state:
            st.session_state.config = None
        
        if "messages" not in st.session_state:
            st.session_state.messages = []

    def is_configured(self) -> bool:
        """Verifica se il sistema è configurato"""
        return st.session_state.config is not None
    
    def setup(self, config_dict: Dict[str, Any]) -> None:
        """
        Salva la configurazione iniziale
        
        Args:
            config_dict: Dizionario con file_path, struttura, regole, etc.
        """
        config = ConfigSetup(**config_dict)
        st.session_state.config = config.model_dump()
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Ottieni un valore dalla configurazione
        
        Args:
            key: Chiave da cercare
            default: Valore di default se non trovato
        
        Returns:
            Valore salvato o default
        """
        if not self.is_configured():
            return default
        return st.session_state.config.get(key, default)

    def get_all(self) -> Dict[str, Any]:
        """Restituisce tutta la configurazione"""
        return st.session_state.config or {}
    
    def reset(self) -> None:
        """Reset completo della configurazione"""
        st.session_state.config = None
        st.session_state.messages = []
    
    def get_messages(self) -> list:
        """Restituisce tutti i messaggi della chat"""
        return st.session_state.messages