"""
Factory per creare il sistema multi-agente completo
"""

from datapizza.agents import Agent
from datapizza.memory import Memory
from typing import Optional

from .code_generator import create_code_generator_agent
from .explainer import create_explainer_agent
from .narrator import create_narrator_agent
from .orchestrator import create_orchestrator_agent

# Setup path per importare src
from pathlib import Path
import sys
BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.append(str(BASE_DIR))
from src.config import REASONING_MODEL, BASE_MODEL

def create_multi_agent_system(
    api_key: str,
    code_model: str = REASONING_MODEL,
    explainer_model: str = REASONING_MODEL,
    narrator_model: str = BASE_MODEL,
    orchestrator_model: str = REASONING_MODEL,
    memory: Optional[Memory] = None
) -> Agent:
    """
    Crea l'intero sistema multi-agente con tutti gli specialist coordinati dall'orchestrator.
    
    Args:
        api_key: OpenAI API key
        code_model: Modello per code generator (default: gpt-4o)
        explainer_model: Modello per explainer (default: gpt-4o)
        narrator_model: Modello per narrator (default: gpt-4o-mini economico)
        orchestrator_model: Modello per orchestrator (default: gpt-4o)
        memory: Memoria conversazionale condivisa (opzionale)
    
    Returns:
        Agent orchestratore pronto per ricevere richieste utente
    
    Example:
        ```
        from datapizza.memory import Memory
        from src.agents.factory import create_multi_agent_system
        
        memory = Memory()
        orchestrator = create_multi_agent_system(
            api_key="your-key",
            memory=memory
        )
        
        response = orchestrator.run("Gestisci le assenze di martedì")
        print(response.text)
        ```
    """
    # Crea gli specialist agents
    code_agent = create_code_generator_agent(
        api_key=api_key,
        model=code_model
    )
    
    explainer_agent = create_explainer_agent(
        api_key=api_key,
        model=explainer_model
    )
    
    narrator_agent = create_narrator_agent(
        api_key=api_key,
        model=narrator_model
    )
    
    # Crea l'orchestrator che coordina tutti
    orchestrator = create_orchestrator_agent(
        api_key=api_key,
        code_agent=code_agent,
        explainer_agent=explainer_agent,
        narrator_agent=narrator_agent,
        model=orchestrator_model,
        memory=memory
    )
    
    return orchestrator
