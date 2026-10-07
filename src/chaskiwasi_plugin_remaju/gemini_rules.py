"""Configuración opcional de extracción semántica para resoluciones REMAJU."""

from __future__ import annotations

from typing import Any


def get_gemini_extraction_config() -> dict[str, Any]:
    """Retorna configuración; no invoca Gemini."""
    return {
        "model_name": "gemini-1.5-flash",
        "system_instruction": (
            "Eres un experto en derecho procesal civil peruano y ejecuciones de garantías. "
            "Extrae únicamente información expresamente contenida en la resolución REMAJU. "
            "No completes nombres truncados ni inventes datos. Distingue demandantes o "
            "ejecutantes de abogados, representantes, jueces, secretarios, martilleros, "
            "peritos y terceros. Distingue demandados o ejecutados de propietarios, "
            "ocupantes, terceros y garantes salvo identificación expresa. Para la dirección "
            "usa únicamente la del inmueble materia del remate y conserva tipo y nombre de "
            "vía, número, manzana, lote, urbanización, asociación, sector, etapa, distrito "
            "y provincia cuando estén presentes. No geocodifiques ni agregues geografía. "
            "No combines fragmentos de propiedades distintas. requiere_cartel es true solo "
            "cuando exista una orden efectiva de fijar o colocar carteles; una mención histórica "
            "de carteles, publicaciones, edictos o avisos no basta. Si existe ambigüedad, usa false."
        ),
        "prompt_template": (
            "Extrae demandantes, demandados, dirección del inmueble y si la resolución ordena "
            "efectivamente fijar o colocar carteles. Devuelve únicamente JSON válido. "
            "Usa listas vacías o cadenas vacías cuando el dato no esté expresamente presente.\n\n"
            "TEXTO:\n{text}"
        ),
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "remate": {
                    "type": "OBJECT",
                    "properties": {
                        "demandantes": {"type": "ARRAY", "items": {"type": "STRING"}},
                        "demandados": {"type": "ARRAY", "items": {"type": "STRING"}},
                    },
                    "required": ["demandantes", "demandados"],
                },
                "inmuebles": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "direccion": {"type": "STRING"},
                            "requiere_cartel": {"type": "BOOLEAN"},
                        },
                        "required": ["direccion", "requiere_cartel"],
                    },
                },
            },
            "required": ["remate", "inmuebles"],
        },
    }
