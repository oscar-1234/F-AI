"""
Funzioni di utilità generiche
"""

from pathlib import Path
from datetime import datetime

def save_uploaded_file(uploaded_file, target_dir: Path) -> Path:
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