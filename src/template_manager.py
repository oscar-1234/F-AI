"""
Manage template loading and validation from YAML files
"""

import yaml
from pathlib import Path
from typing import Dict, Any
from pydantic import BaseModel, Field, ValidationError
from src.config import TEMPLATES_FILE
from src.models import Template

class TemplateManager:
    """Manages loading and access to templates"""
    
    def __init__(self, templates_file: Path):
        """
        Initializes the manager by loading templates from the YAML file
        
        Args:
            templates_file: Path to the YAML file containing the templates
        """
        self.templates_file = templates_file
        self._templates: Dict[str, Dict[str, Any]] = {}
        self._load_templates()
    
    def _load_templates(self) -> None:
        """Load and validate templates from the YAML file"""
        if not self.templates_file.exists():
            raise FileNotFoundError(
                f"File template non trovato: {self.templates_file}"
            )
        
        try:
            with open(self.templates_file, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            # Validate every template with Pydantic
            raw_templates = data.get('templates', {})
            for key, template_data in raw_templates.items():
                try:
                    validated = Template(**template_data)
                    self._templates[validated.nome] = {
                        "struttura": validated.struttura,
                        "regole": validated.regole,
                        "descrizione": validated.descrizione
                    }
                except ValidationError as e:
                    print(f"⚠️ Template '{key}' non valido: {e}")
                    continue
            
            if not self._templates:
                raise ValueError("Nessun template valido trovato nel file YAML")
                
        except yaml.YAMLError as e:
            raise ValueError(f"Errore parsing YAML: {e}")
    
    def get_all(self) -> Dict[str, Dict[str, Any]]:
        """Returns all available templates"""
        return self._templates.copy()
    
    def get(self, nome: str) -> Dict[str, Any]:
        """
        Get a name-specific template
        
        Args:
            nome: Template name
            
        Returns:
            Dictionary with structure, rules, description
            
        Raises:
            KeyError: If the template does not exist
        """
        if nome not in self._templates:
            raise KeyError(f"Template '{nome}' non trovato. Disponibili: {list(self._templates.keys())}")
        return self._templates[nome].copy()
        

try:
    _manager = TemplateManager(TEMPLATES_FILE)
    TEMPLATES = _manager.get_all()
except Exception as e:
    print(f"❌ Errore caricamento template: {e}")
    # Fallback: Empty template to avoid crashes
    TEMPLATES = {
        "Personalizzato": {
            "struttura": "Configura manualmente",
            "regole": "Configura manualmente",
            "descrizione": "Fallback per errore caricamento"
        }
    }