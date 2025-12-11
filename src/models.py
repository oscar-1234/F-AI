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
                "regola_applicata": "Regola 'Ora Jolly'"
            }
        }

class SystemMetrics(BaseModel):
    """System metrics"""
    totale_richieste: int = 0
    totale_sostituzioni: int = 0
    tempo_medio_risposta: float = 0.0
    costo_totale: float = 0.0
    ultimo_aggiornamento: datetime = Field(default_factory=datetime.now)