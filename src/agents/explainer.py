"""
Explainer Agent - Specialist per spiegare decisioni e ragionamenti
"""

from datapizza.agents import Agent
from datapizza.clients.openai import OpenAIClient
from src.agents.config import EXPLAINER_SYSTEM_PROMPT

def create_explainer_agent(api_key: str, model: str = "gpt-4o") -> Agent:
    """
    Crea l'agente specializzato nello spiegare decisioni.
    
    Args:
        api_key: OpenAI API key
        model: Modello LLM da usare (default: gpt-4o per reasoning accurato)
    
    Returns:
        Agent configurato per spiegazioni
    """
    client = OpenAIClient(api_key=api_key, model=model)
    
    agent = Agent(
        name="explainer",
        client=client,
        tools=[],  # Nessun tool, pure reasoning
        system_prompt=EXPLAINER_SYSTEM_PROMPT,
        max_steps=2,
        terminate_on_text=True
    )
    
    return agent