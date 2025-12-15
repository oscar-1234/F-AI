"""
Code Generator Agent - Specialist per generazione ed esecuzione codice Python
"""

from datapizza.agents import Agent
from datapizza.clients.openai import OpenAIClient
import json
from src.agents.config import CODE_GENERATOR_SYSTEM_PROMPT

# Import corretti con path assoluto src
from src.tools import execute_code_in_sandbox
from src.models import Sostituzione


def create_code_generator_agent(api_key: str, model: str = "gpt-4o") -> Agent:
    """
    Crea l'agente specializzato nella generazione di codice Python.
    """
    client = OpenAIClient(api_key=api_key, model=model)
    
    # Schema Pydantic per output validation
    schema_sostituzione = Sostituzione.model_json_schema()
    target_schema = {
        "type": "array",
        "items": schema_sostituzione,
        "description": "Una lista di oggetti Sostituzione validi"
    }
    schema_str = json.dumps(target_schema, indent=2)

    # Inietta la variabile schema_str dentro il template importato
    formatted_system_prompt = CODE_GENERATOR_SYSTEM_PROMPT.format(
        schema_str=schema_str
    )

    agent = Agent(
        name="code_generator",
        client=client,
        tools=[execute_code_in_sandbox],
        system_prompt=formatted_system_prompt,
        max_steps=4,
        terminate_on_text=True
    )
    
    return agent
