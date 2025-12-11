"""
Funzioni di utilità generiche
"""

import pandas as pd
from pathlib import Path
from typing import Dict, Any, Optional
import hashlib
from datetime import datetime


def save_uploaded_file(uploaded_file, target_dir: str) -> Path:
    """
    Salva un file caricato da Streamlit sul filesystem
    
    Args:
        uploaded_file: File da st.file_uploader
        target_dir: Directory di destinazione
    
    Returns:
        Path del file salvato
    """
    target_path = Path(target_dir)
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Genera nome file univoco con timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = Path(uploaded_file.name).suffix
    unique_name = f"orario_{timestamp}{file_extension}"
    
    file_path = target_path / unique_name
    
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    return file_path


def validate_excel_structure(file_path: str) -> Dict[str, Any]:
    """
    Valida la struttura di base del file Excel
    
    Args:
        file_path: Path del file Excel
    
    Returns:
        Dict con 'valid' (bool), 'issues' (list), 'info' (dict)
    """
    issues = []
    info = {}
    
    try:
        df = pd.read_excel(file_path, header=0)
        
        # Info base
        info['righe'] = len(df)
        info['colonne'] = len(df.columns)
        info['nomi_colonne'] = df.columns.tolist()
        
        # Check minimo 2 colonne (Nome + Cappello/Tag)
        if len(df.columns) < 2:
            issues.append("Il file deve avere almeno 2 colonne")
        
        # Check minimo 1 riga dati
        if len(df) < 1:
            issues.append("Il file deve contenere almeno una riga di dati")
        
        # Check presenza colonna che sembra "nome"
        first_col = df.columns[0].lower()
        if 'nome' not in first_col and 'elfo' not in first_col:
            issues.append("La prima colonna dovrebbe contenere i nomi (es. 'Nome Elfo')")
        
        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "info": info
        }
    
    except Exception as e:
        return {
            "valid": False,
            "issues": [f"Errore lettura Excel: {str(e)}"],
            "info": {}
        }


def format_trace_summary(trace_data: Optional[Dict]) -> str:
    """
    Formatta i dati di tracing per visualizzazione
    
    Args:
        trace_data: Dict con span OpenTelemetry
    
    Returns:
        Stringa formattata human-readable
    """
    if not trace_data:
        return "Nessun trace disponibile"
    
    output = "📊 Performance Breakdown:\n\n"
    
    total_duration = trace_data.get('duration', 0)
    output += f"⏱️  Durata Totale: {total_duration:.2f}s\n\n"
    
    spans = trace_data.get('spans', [])
    for i, span in enumerate(spans, 1):
        name = span.get('name', 'Unknown')
        duration = span.get('duration', 0)
        percentage = (duration / total_duration * 100) if total_duration > 0 else 0
        
        output += f"{i}. {name}\n"
        output += f"   ├─ Tempo: {duration:.2f}s ({percentage:.1f}%)\n"
        
        # Mostra attributi se presenti
        attrs = span.get('attributes', {})
        if attrs:
            output += f"   └─ Info: {attrs}\n"
        output += "\n"
    
    return output


def estimate_openai_cost(
    model: str,
    input_tokens: int,
    output_tokens: int
) -> float:
    """
    Stima il costo di una chiamata OpenAI
    
    Args:
        model: Nome del modello (es. 'gpt-4o', 'gpt-4o-mini')
        input_tokens: Token in input
        output_tokens: Token in output
    
    Returns:
        Costo stimato in euro
    """
    # Prezzi al 10/12/2025 (in $ per 1M token)
    PRICES = {
        "gpt-4o": {"input": 2.50, "output": 10.00},
        "gpt-4o-mini": {"input": 0.15, "output": 0.60},
        "gpt-4-turbo": {"input": 10.00, "output": 30.00}
    }
    
    # Tasso di cambio USD -> EUR (approssimato)
    USD_TO_EUR = 0.92
    
    model_prices = PRICES.get(model, PRICES["gpt-4o-mini"])
    
    cost_usd = (
        (input_tokens / 1_000_000) * model_prices["input"] +
        (output_tokens / 1_000_000) * model_prices["output"]
    )
    
    return cost_usd * USD_TO_EUR


def generate_story_hash(content: str) -> str:
    """
    Genera un hash univoco per una storia (per evitare duplicati)
    
    Args:
        content: Contenuto della storia
    
    Returns:
        Hash MD5 (primi 8 caratteri)
    """
    return hashlib.md5(content.encode()).hexdigest()[:8]


def format_sostituzioni_table(sostituzioni: list) -> str:
    """
    Formatta lista sostituzioni come tabella Markdown
    
    Args:
        sostituzioni: Lista di dict con sostituzioni
    
    Returns:
        Stringa Markdown
    """
    if not sostituzioni:
        return "Nessuna sostituzione necessaria."
    
    table = "| Giorno | Ora | Reparto | Assente | Sostituto | Regola |\n"
    table += "|--------|-----|---------|---------|-----------|--------|\n"
    
    for s in sostituzioni:
        table += f"| {s['giorno']} | {s['ora']}^ | {s['reparto']} | "
        table += f"{s['assente']} | {s['sostituto']} | {s['regola_applicata']} |\n"
    
    return table
