"""
Orchestrator Agent - Master agent che coordina gli specialist agents
"""

from datapizza.agents import Agent
from datapizza.clients.openai import OpenAIClient
from datapizza.memory import Memory
from typing import Optional
from src.agents.config import ORCHESTRATOR_SYSTEM_PROMPT

def create_orchestrator_agent(
    api_key: str,
    code_agent: Agent,
    explainer_agent: Agent,
    narrator_agent: Agent,
    model: str = "gpt-4o",
    memory: Optional[Memory] = None
) -> Agent:
    """
    Crea l'agente orchestratore master che coordina tutti gli specialist agents.
    
    Args:
        api_key: OpenAI API key
        code_agent: Agent specializzato nella generazione codice
        explainer_agent: Agent specializzato nelle spiegazioni
        narrator_agent: Agent specializzato nelle narrazioni
        model: Modello LLM da usare (default: gpt-4o per reasoning complesso)
        memory: Memoria conversazionale (opzionale, può essere passata al run)
    
    Returns:
        Agent orchestratore configurato con can_call() agli specialists
    """
    client = OpenAIClient(api_key=api_key, model=model)
    
    orchestrator = Agent(
        name="orchestrator",
        client=client,
        tools=[],  # Nessun tool diretto, usa can_call() per delegare
        memory=memory,  # Memoria conversazionale
        system_prompt=ORCHESTRATOR_SYSTEM_PROMPT,
        max_steps=10, 
        terminate_on_text=True
    )
    
    # Registra gli specialist agents con can_call
    # Secondo la documentazione, can_call accetta una lista di agents [web:10]
    orchestrator.can_call([code_agent, explainer_agent, narrator_agent])
    
    return orchestrator