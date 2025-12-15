"""
Tool custom per l'esecuzione di codice Python in sandbox E2B.
"""

from datapizza.tools import tool
from e2b_code_interpreter import Sandbox
import json
import os
import traceback
from pathlib import Path

# Import assoluto invece di relativo
from src.config import E2B_API_KEY, DATA_DIR


@tool
def execute_code_in_sandbox(
    codice_python: str,
    file_excel_path: str = "auto"
) -> str:
    """
    Esegue codice Python generato dall'LLM in una sandbox E2B sicura.
    """
    try:
        if not DATA_DIR.exists():
            return json.dumps({"success": False, "error": f"Directory dati non trovata: {DATA_DIR}"})
        
        excel_files = sorted(DATA_DIR.glob("*.xlsx"), key=lambda p: p.stat().st_mtime, reverse=True)
        if not excel_files:
            return json.dumps({"success": False, "error": "Nessun file Excel trovato in app/data."})
        
        real_file_path = excel_files[0]
        remote_filename = "orario_input.xlsx"
        
        os.environ["E2B_API_KEY"] = E2B_API_KEY
        
        with Sandbox(api_key=E2B_API_KEY) as sandbox:
            with open(real_file_path, 'rb') as f:
                sandbox.files.write(remote_filename, f.read())
            
            # Wrapper con struttura sicura
            codice_wrapper = f"""
import pandas as pd
import json
import traceback

# 1. CODICE UTENTE (Definizioni funzioni, import, costanti)
{codice_python}

# 2. LOGICA DI ESECUZIONE CONTROLLATA
try:
    # Setup dati
    remote_filename = '{remote_filename}'
    df = pd.read_excel(remote_filename, header=0)
    
    # Verifica esistenza funzione
    if 'calcola_sostituzioni' not in locals():
        raise NameError("La funzione 'calcola_sostituzioni(df)' non è stata definita.")
    
    # Esecuzione
    risultati = calcola_sostituzioni(df)
    
    # Output
    print(json.dumps({{"success": True, "output": risultati}}, ensure_ascii=False))

except Exception as e:
    print(json.dumps({{
        "success": False,
        "error": str(e),
        "traceback": traceback.format_exc()
    }}, ensure_ascii=False))
"""
            
            execution = sandbox.run_code(codice_wrapper)
            
            if execution.error:
                return json.dumps({
                    "success": False,
                    "error": f"Errore Runtime Sandbox: {execution.error.name}: {execution.error.value}",
                    "traceback": execution.error.traceback
                })
            
            output_text = execution.text or ""
            if not output_text and execution.logs.stdout:
                output_text = "\n".join(execution.logs.stdout)
            
            if not output_text:
                return json.dumps({"success": False, "error": "Nessun output ricevuto dalla sandbox."})
            
            return output_text
    
    except Exception as e:
        return json.dumps({
            "success": False,
            "error": f"Errore interno tool: {str(e)}",
            "traceback": traceback.format_exc()
        })