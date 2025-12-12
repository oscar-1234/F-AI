"""
Agents package - Sistema multi-agente per gestione emergenze Fabbrica Elfi
"""

from .code_generator import create_code_generator_agent
from .explainer import create_explainer_agent
from .narrator import create_narrator_agent
from .orchestrator import create_orchestrator_agent
from .factory import create_multi_agent_system

__all__ = [
    "create_code_generator_agent",
    "create_explainer_agent",
    "create_narrator_agent",
    "create_orchestrator_agent",
    "create_multi_agent_system"
]
