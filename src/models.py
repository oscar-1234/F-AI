"""
Data models for validation and serialization
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any
from datetime import datetime

class ConfigSetup(BaseModel):
    """Initial system setup"""
    file_path: str
    file_name: str
    struttura: str
    regole: str
    template: str
    created_at: datetime = Field(default_factory=datetime.now)


class Sostituzione(BaseModel):
    """Single calculated replacement"""
    giorno: str
    ora: int
    reparto: str
    assente: str
    cappello_assente: Optional[str] = None
    sostituto: str
    regola_applicata: str
    ragionamento: str
    
    @field_validator('ora', mode='before')
    @classmethod
    def convert_ora_to_int(cls, v):
        """Converts 'ora' from string to int if necessary"""
        if isinstance(v, str):
            return int(v)
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "giorno": "Lunedì",
                "ora": "4",
                "reparto": "PE",
                "assente": "Scintillino",
                "cappello_assente": "Rosso",
                "sostituto": "Brillastella",
                "regola_applicata": "Regola 'Ora Jolly'",
                "ragionamento": "Ho scelto la regola 'Ora Jolly' perchè ..."
            }
        }

class ConversationalContext(BaseModel):
    """Context of the current conversation"""
    ultima_richiesta: str
    ultime_sostituzioni: List[Sostituzione] = []
    codice_generato: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)
    
    def get_sostituzioni_summary(self) -> str:
        """Returns a summary of the substitutions for the context"""
        if not self.ultime_sostituzioni:
            return "Nessuna sostituzione calcolata"
        
        summary = f"Calcolate {len(self.ultime_sostituzioni)} sostituzioni:\n"
        for s in self.ultime_sostituzioni:
            summary += f"- {s.assente} ({s.reparto}, {s.giorno} ora {s.ora}) → {s.sostituto} [{s.regola_applicata}]\n"
        return summary
#*.*
class SystemMetrics(BaseModel):
    """System metrics"""
    totale_richieste: int = 0
    totale_sostituzioni: int = 0
    tempo_medio_risposta: float = 0.0
#    costo_totale: float = 0.0 #-#
    ultimo_aggiornamento: datetime = Field(default_factory=datetime.now)