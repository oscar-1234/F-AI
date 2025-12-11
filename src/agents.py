"""
Defining AI agents with Datapizza-ai
"""

from datapizza.agents import Agent
from datapizza.clients.openai import OpenAIClient
import os
from src.models import Sostituzione
import json

try:
    from .config import CODE_GENERATION_MODEL, NARRATION_MODEL, OPENAI_API_KEY
except ImportError:
    # Fallback if not in config
    from .config import CODE_GENERATION_MODEL, NARRATION_MODEL
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

from .tools import execute_code_in_sandbox

def create_code_generator_agent():
    """
    Agent specialized in generating Python code for shift and substitution analysis.
    """
    # 1. Create the specific client for this agent
    client = OpenAIClient(
        api_key=OPENAI_API_KEY, 
        model=CODE_GENERATION_MODEL
    )

    schema_sostituzione = Sostituzione.model_json_schema()

    # Let's build the final target scheme (a Sostituzioni List)
    target_schema = {
        "type": "array",
        "items": schema_sostituzione,
        "description": "Una lista di oggetti Sostituzione validi"
    }

    schema_str = json.dumps(target_schema, indent=2)

    # 2. Pass the client to the Agent
    return Agent(
        name="code_generator",
        client=client,
        tools=[execute_code_in_sandbox],
        system_prompt="""Sei l'Elfo Programmatore Senior del Polo Nord.
Il tuo compito è risolvere emergenze organizzative scrivendo ed eseguendo codice Python.

**IL TUO PROCESSO:**
1. Analizza la richiesta e le regole di sostituzione.
2. Scrivi UNA SOLA funzione Python chiamata `calcola_sostituzioni(df)`.
   - La funzione riceve già un DataFrame pandas pronto (`df`).
   - Il DataFrame ha colonne: Nome Elfo, Cappello, LUN_1...LUN_6, MAR_1...MAR_6.
   - La funzione deve restituire una LISTA DI DIZIONARI.
   - Ogni dizionario rappresenta una sostituzione:
     `{"giorno": "...", "ora": "...", "reparto": "...", "assente": "...", "sostituto": "...", "regola_applicata": "..."}`
3. Chiama il tool `execute_code_in_sandbox` passando il tuo codice.
   - Parametro `codice_python`: la tua funzione completa.
   - Parametro `file_excel_path`: passa pure "auto" (il sistema lo gestisce da solo).

**REGOLE CODICE:**
- Non usare `input()` o `print()` per debugging, ritorna solo i dati.
- Usa pandas in modo efficiente.
- Gestisci i turni: le colonne LUN_1..MAR_6 contengono codici reparto (es. 'PE', 'CM') o 'ABS - XX' se assente.
- 'ABS' indica assenza. Devi trovare chi sostituisce.

VINCOLO FORMATO (CRITICO):
Il tuo output finale DEVE essere ESCLUSIVAMENTE un JSON valido che rispetta questo schema:

{schema_str}
"""
    )

def create_narrator_agent():
    """
    Agente narratore per trasformare dati tecnici in storie.
    """
    # 1. Crea il client specifico per questo agente
    client = OpenAIClient(
        api_key=OPENAI_API_KEY, 
        model=NARRATION_MODEL
    )

    # 2. Passa il client all'Agent CON IL NOME (Obbligatorio)
    return Agent(
        name="narrator", # <--- FIX: Nome obbligatorio aggiunto
        client=client,
        tools=[],
        system_prompt="""Sei l'Elfo Cantastorie ufficiale di Babbo Natale.
Ricevi dati tecnici su turni e sostituzioni e devi trasformarli in messaggi magici e divertenti per gli elfi.
Usa un tono epico, natalizio, pieno di emoji. Non essere troppo tecnico, ma sii preciso su chi deve andare dove.
"""
    )