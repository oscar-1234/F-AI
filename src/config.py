"""
Configurazione centrale del progetto
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

# ========================================
# API KEYS
# ========================================
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
E2B_API_KEY = os.getenv("E2B_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY non trovata nel file .env")
if not E2B_API_KEY:
    raise ValueError("❌ E2B_API_KEY non trovata nel file .env")

# ========================================
# LLM MODELS
# ========================================

REASONING_MODEL = "gpt-4o" 
BASE_MODEL = "gpt-4o-mini"

# ========================================
# STREAMLIT CONFIG
# ========================================

PAGE_CONFIG = {
    "page_title": "🎄 Fabbrica Elfi AI - Sistema di Gestione Emergenze",
    "page_icon": "🎅",
    "layout": "wide",
    "initial_sidebar_state": "expanded",
    "menu_items": {
        'Get Help': 'https://github.com/oscar-1234/FGBN',
        'Report a bug': 'https://github.com/oscar-1234/FGBN/issues',
        'About': """
        # 🎄 Fabbrica Elfi AI - Sistema di Gestione Emergenze
        Sistema intelligente di gestione emergenze per la Fabbrica di Giocattoli del Polo Nord.
        
        **Datapizza Christmas AI Challenge 2025**
        """
    }
}

# ========================================
# PATHS
# ========================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "app" / "data"
FILE_DIR = PROJECT_ROOT / "src" / "data"

# Create directories if none exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
FILE_DIR.mkdir(parents=True, exist_ok=True)

# Template Global initialization
TEMPLATES_FILE = PROJECT_ROOT / "src" / "templates" / "default_templates.yaml"

# ========================================
# E2B CONFIG
# ========================================

E2B_TIMEOUT = 300  # 5 minute sandbox timeout
E2B_SANDBOX_TEMPLATE = "python"

# ========================================
# LOGGING CONFIG
# ========================================

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
ENABLE_TRACING = os.getenv("ENABLE_TRACING", "true").lower() == "true"