"""
Gestione dello stato della sessione Streamlit
"""

import streamlit as st
from typing import Any, Dict, Optional
from datetime import datetime

from .models import ConfigSetup, SystemMetrics


class SessionManager:
    """Gestisce lo state della sessione Streamlit in modo type-safe"""
    
    def __init__(self):
        """Inizializza session state se non esiste"""
        if "config" not in st.session_state:
            st.session_state.config = None
        
        if "metrics" not in st.session_state:
            st.session_state.metrics = SystemMetrics()
        
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
    
    def add_message(self, role: str, content: str, metadata: Optional[Dict] = None) -> None:
        """
        Aggiungi un messaggio alla chat history
        
        Args:
            role: 'user' o 'assistant'
            content: Contenuto del messaggio
            metadata: Metadata opzionali (codice, trace, etc.)
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        if metadata:
            message["metadata"] = metadata
        
        st.session_state.messages.append(message)
    
    def get_messages(self) -> list:
        """Restituisce tutti i messaggi della chat"""
        return st.session_state.messages
    
    def update_metrics(
        self,
        sostituzioni_count: int,
        duration: float,
        cost: float
    ) -> None:
        """
        Aggiorna le metriche di sistema
        
        Args:
            sostituzioni_count: Numero di sostituzioni calcolate
            duration: Durata operazione in secondi
            cost: Costo stimato in euro
        """
        metrics = st.session_state.metrics
        
        # Incrementa contatori
        metrics.totale_richieste += 1
        metrics.totale_sostituzioni += sostituzioni_count
        metrics.costo_totale += cost
        
        # Calcola media mobile tempo risposta
        n = metrics.totale_richieste
        metrics.tempo_medio_risposta = (
            (metrics.tempo_medio_risposta * (n - 1) + duration) / n
        )
        
        metrics.ultimo_aggiornamento = datetime.now()
        st.session_state.metrics = metrics
    
    def get_metrics(self) -> SystemMetrics:
        """Restituisce le metriche correnti"""
        return st.session_state.metrics
