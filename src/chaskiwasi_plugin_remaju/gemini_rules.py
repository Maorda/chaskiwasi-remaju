# D:\libs\chaskiwasi_plugin_remaju\src\chaskiwasi_plugin_remaju\gemini_rules.py

"""
Reglas de extracción inteligente mediante Gemini para resoluciones REMAJU.

Este módulo define exclusivamente la configuración de extracción.
Gemini debe extraer información explícitamente contenida en la resolución,
sin inferir, completar ni interpretar datos que no estén sustentados por
el texto del documento.
"""

from typing import Any, Dict


def get_gemini_extraction_config() -> Dict[str, Any]:
    """
    Retorna la configuración, instrucciones de sistema y esquema de salida
    para extraer información estructurada de resoluciones judiciales de
    remate REMAJU.

    La extracción es deliberadamente conservadora:
    - No se inventan datos.
    - No se completan nombres parcialmente identificados.
    - No se realizan inferencias jurídicas.
    - No se confunden partes procesales con abogados, representantes,
      terceros u otros intervinientes.
    - La dirección corresponde exclusivamente al inmueble materia de remate.
    - 'requiere_cartel' solo es true cuando la resolución contiene una
      orden o disposición efectiva de fijación de carteles.
    """

    return {
        
        "system_instruction": (
            "Eres un extractor especializado de información contenida en "
            "resoluciones judiciales de remate de inmuebles del sistema "
            "REMAJU del Perú. "
            "\n\n"
            "Tu función es EXTRAER información explícitamente contenida "
            "en el texto proporcionado. No debes realizar investigación "
            "externa, completar información faltante, corregir nombres "
            "mediante conocimiento externo ni inferir datos jurídicos que "
            "no estén expresamente sustentados por el documento. "
            "\n\n"
            "REGLAS OBLIGATORIAS DE EXTRACCIÓN:"
            "\n"
            "1. Devuelve únicamente JSON válido conforme al esquema "
            "proporcionado. No escribas explicaciones, comentarios, "
            "markdown ni texto fuera del JSON."
            "\n"
            "2. No inventes ningún dato."
            "\n"
            "3. Si un dato no aparece de forma suficientemente clara en "
            "el documento, utiliza una lista vacía para los campos de "
            "partes o una cadena vacía para la dirección."
            "\n"
            "4. No completes nombres truncados, ilegibles o incompletos."
            "\n"
            "5. No confundas demandantes o ejecutantes con abogados, "
            "apoderados, representantes, jueces, secretarios, martilleros, "
            "peritos, terceros u otras personas mencionadas en la resolución."
            "\n"
            "6. No confundas demandados o ejecutados con propietarios, "
            "ocupantes, terceros, garantes u otras personas, salvo que el "
            "texto identifique expresamente a esa persona como demandada "
            "o ejecutada."
            "\n"
            "7. Si existen varias personas pertenecientes a una misma "
            "parte procesal, incluye cada nombre por separado."
            "\n"
            "8. Conserva los nombres completos tal como aparecen en el "
            "documento. No los normalices ni los reordenes salvo que sea "
            "necesario para representar correctamente el nombre completo."
            "\n"
            "9. Para la dirección, identifica exclusivamente la dirección "
            "del inmueble que es materia del remate. No utilices domicilios "
            "procesales, domicilios de las partes, domicilios de abogados "
            "ni otras direcciones."
            "\n"
            "10. Si existen varias referencias al inmueble, utiliza la "
            "dirección que esté claramente vinculada al inmueble materia "
            "del remate. No combines fragmentos provenientes de inmuebles "
            "diferentes."
            "\n"
            "11. Conserva en la dirección los elementos explícitamente "
            "mencionados, incluyendo tipo y nombre de vía, número, "
            "manzana, lote, urbanización, asociación, sector, etapa, "
            "distrito, provincia u otros componentes que formen parte "
            "de la identificación del inmueble."
            "\n"
            "12. No conviertas ni geocodifiques la dirección. No agregues "
            "información geográfica que no aparezca en el documento."
            "\n"
            "13. 'requiere_cartel' debe ser true únicamente cuando la "
            "resolución contenga una orden, mandato o disposición efectiva "
            "relacionada con la fijación o colocación de carteles para "
            "el remate."
            "\n"
            "14. Una simple mención histórica de carteles, una referencia "
            "a una actuación anterior o una descripción de una publicación "
            "no debe considerarse por sí sola una orden actual de fijación "
            "de carteles."
            "\n"
            "15. No confundas carteles con edictos, publicaciones en "
            "diarios, publicaciones web, avisos judiciales u otros medios "
            "de publicidad, salvo que el documento ordene expresamente "
            "también la fijación de carteles."
            "\n"
            "16. Si la existencia de una orden de carteles es ambigua, "
            "utiliza false."
            "\n"
            "17. La ausencia de evidencia no equivale a una inferencia "
            "negativa sobre la situación jurídica del expediente; "
            "simplemente significa que el dato solicitado no fue "
            "identificado en el texto proporcionado."
        ),
        "prompt_template": (
            "Analiza exclusivamente el texto de la resolución judicial "
            "de remate proporcionado a continuación.\n\n"
            "Extrae los siguientes datos:\n\n"
            "1. 'demandantes': lista de nombres completos de las personas "
            "que el documento identifica expresamente como demandantes, "
            "ejecutantes o parte demandante.\n\n"
            "2. 'demandados': lista de nombres completos de las personas "
            "que el documento identifica expresamente como demandados, "
            "ejecutados o parte demandada.\n\n"
            "3. 'direccion_inmueble': dirección del inmueble que es materia "
            "del remate. Debe corresponder al inmueble objeto de la "
            "ejecución y no al domicilio procesal de ninguna de las partes. "
            "Conserva todos los componentes de la dirección que aparezcan "
            "explícitamente en el documento.\n\n"
            "4. 'requiere_cartel': true únicamente si la resolución "
            "contiene una orden o disposición efectiva de fijar o colocar "
            "carteles para el remate. Si solo menciona carteles como "
            "antecedente, actuación anterior o referencia general, utiliza "
            "false.\n\n"
            "REGLA FUNDAMENTAL:\n"
            "Si la información no puede determinarse de manera explícita "
            "y suficientemente clara a partir del texto proporcionado, "
            "no la inventes ni la infieras.\n\n"
            "Texto del documento:\n"
            "{document_text}"
        ),
        "response_schema": {
            "type": "OBJECT",
            "properties": {
                "remate": {
                    "type": "OBJECT",
                    "properties": {
                        "demandantes": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"},
                            "description": (
                        "Nombres completos de las personas identificadas "
                        "explícitamente en la resolución como demandantes, "
                        "ejecutantes o parte demandante. Lista vacía si "
                        "no se identifican de forma suficientemente clara."
                    )
                        },
                        "demandados": {
                            "type": "ARRAY",
                            "items": {"type": "STRING"},
                            "description": (
                        "Nombres completos de las personas identificadas "
                        "explícitamente en la resolución como demandados, "
                        "ejecutados o parte demandada. Lista vacía si "
                        "no se identifican de forma suficientemente clara."
                    )
                        }
                    }
                },
                "inmuebles": {
                    "type": "ARRAY",
                    "items": {
                        "type": "OBJECT",
                        "properties": {
                            "direccion": {
                                "type": "STRING",
                                "description": (
                        "Dirección explícita del inmueble materia de "
                        "remate. Debe excluir domicilios procesales y "
                        "otras direcciones ajenas al inmueble. Cadena "
                        "vacía si no puede identificarse de forma clara."
                    )
                            },
                            "requiere_cartel": {
                                "type": "BOOLEAN",
                                "description": (
                        "True únicamente cuando la resolución contiene "
                        "una orden o disposición efectiva de fijar o "
                        "colocar carteles para el remate. False cuando "
                        "solo existe una mención, antecedente, actuación "
                        "anterior o cuando no existe evidencia suficiente."
                    )
                            }
                        }
                    }
                }
            },
            "required": ["remate", "inmuebles"]
        }
    }
