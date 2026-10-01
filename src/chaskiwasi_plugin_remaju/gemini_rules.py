# D:\libs\chaskiwasi_plugin_remaju\src\chaskiwasi_plugin_remaju\gemini_rules.py
"""
Configuración de reglas y prompts de respaldo para Gemini (LLM).
"""

def get_gemini_rules():
    return {
        "system_instruction": (
            "Eres un experto extractor de información jurídica especializado en resoluciones de "
            "Remate Judicial Electrónico (REMAJU). Extrae con precisión los campos solicitados."
        ),
        "prompt_template": (
            "Analiza el siguiente texto de una resolución judicial y extrae:\n"
            "- demandantes: lista de nombres de la parte demandante o ejecutante.\n"
            "- demandados: lista de nombres de la parte demandada o ejecutada.\n"
            "- direccion_inmueble: dirección exacta del inmueble materia de remate.\n"
            "- requiere_cartel: valor booleano (true/false) si se indica fijar carteles.\n\n"
            "Texto del documento:\n{document_text}"
        ),
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "demandantes": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"}
                },
                "demandados": {
                    "type": "ARRAY",
                    "items": {"type": "STRING"}
                },
                "direccion_inmueble": {"type": "STRING"},
                "requiere_cartel": {"type": "BOOLEAN"}
            },
            "required": ["demandantes", "demandados", "direccion_inmueble", "requiere_cartel"]
        }
    }