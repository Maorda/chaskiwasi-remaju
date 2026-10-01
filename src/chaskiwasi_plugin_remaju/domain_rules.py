# D:\libs\chaskiwasi_plugin_remaju\src\chaskiwasi_plugin_remaju\domain_rules.py
"""
Reglas de extracción determinista (Regex) específicas del dominio de resoluciones REMAJU.
"""
import re
from typing import Dict, Any

def extract_remaju_data(text: str, section_texts: Dict[str, str]) -> Dict[str, Any]:
    # Lazy Loading: ehenói nde SectionEnum tee nde plugin gui
    from chaskiwasi_plugin_remaju.taxonomy import SectionEnum

    header_text = section_texts.get(SectionEnum.HEADER.value, text)
    body_text = section_texts.get(SectionEnum.BODY.value, text)
    footer_text = section_texts.get(SectionEnum.FOOTER.value, text)

    extracted_data = {}

    # 1. Extracción de Demandantes (HEADER)
    demandantes = []
    demandante_match = re.search(r"DEMANDANTE\s*[:|]\s*(.+)", header_text, re.IGNORECASE)
    if demandante_match:
        name = demandante_match.group(1).strip().rstrip(",")
        if name:
            demandantes.append(name)
    extracted_data["demandantes"] = demandantes

    # 2. Extracción de Demandados (HEADER)
    demandados = []
    demandado_block = re.search(
        r"DEMANDADO\s*[:|]\s*(.+?)(?=\n\s*\n|\n[A-Z\s]+[:|]|\Z)",
        header_text,
        re.IGNORECASE | re.DOTALL,
    )
    if demandado_block:
        block_text = demandado_block.group(1)
        lines = [line.strip() for line in block_text.split("\n") if line.strip()]
        for line in lines:
            clean_line = re.sub(r"^[:|]\s*", "", line).strip()
            if clean_line:
                demandados.append(clean_line)
    extracted_data["demandados"] = demandados

    # 3. Extracción de Dirección del Inmueble (BODY)
    direccion_match = re.search(r"Ubicación:\s*(.+)", body_text, re.IGNORECASE)
    if direccion_match:
        extracted_data["direccion_inmueble"] = direccion_match.group(1).strip()
    else:
        extracted_data["direccion_inmueble"] = None

    # 4. Extracción de Indicador de Cartel (FOOTER)
    has_cartel = bool(re.search(r"(?i)\bcartel(?:es)?\b", footer_text))
    extracted_data["requiere_cartel"] = has_cartel

    return extracted_data

def get_domain_rules():
    return {
        "extractor": extract_remaju_data
    }