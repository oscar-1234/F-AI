"""
Narrator Agent - Specialist per creare narrazioni natalizie
"""

from datapizza.agents import Agent
from datapizza.clients.openai import OpenAIClient
from src.agents.config import NARRATOR_SYSTEM_PROMPT

def create_narrator_agent(api_key: str, model: str = "gpt-4o-mini") -> Agent:
    """
    Crea l'agente specializzato nella creazione di storie natalizie.
    
    Args:
        api_key: OpenAI API key
        model: Modello LLM da usare (default: gpt-4o-mini, economico per storytelling)
    
    Returns:
        Agent configurato per narrazione
    """
    client = OpenAIClient(api_key=api_key, model=model)
    
    agent = Agent(
        name="narrator",
        client=client,
        tools=[],  # Nessun tool, pure creative writing
        system_prompt=NARRATOR_SYSTEM_PROMPT,
        max_steps=3,
        terminate_on_text=True
    )
    
    return agent