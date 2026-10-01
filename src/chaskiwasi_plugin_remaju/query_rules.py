# D:\libs\chaskiwasi_plugin_remaju\src\chaskiwasi_plugin_remaju\query_rules.py
"""
Reglas de intención y detección de consultas para REMAJU.
"""
from typing import List

from chaskiwasi.query_engine.cross_filter import IntentRule
# Importación clave: Traemos los Enums directamente desde nuestro propio plugin
from chaskiwasi_plugin_remaju.taxonomy import SectionEnum, SourceEnum


def get_query_rules() -> List[IntentRule]:
    """
    Fábrica que expone las reglas de intención para el plugin REMAJU.
    Retorna la lista pura de IntentRules.
    """
    return [
        IntentRule(
            keywords=["remate", "remaju", "resolucion", "ejecucion de garantias", "convocatoria"],
            metadata_filter={
                "$and": [{"fuente": SourceEnum.REMAJU_RESOLUTION.value}]
            }
        ),
        IntentRule(
            keywords=["demandante", "demandado", "ejecutante", "ejecutado", "partes"],
            metadata_filter={
                "$and": [
                    {"fuente": SourceEnum.REMAJU_RESOLUTION.value},
                    {"tipo_seccion": SectionEnum.HEADER.value}
                ]
            }
        ),
        IntentRule(
            keywords=["ubicacion", "ubicación", "inmueble", "direccion", "dirección", "lote"],
            metadata_filter={
                "$and": [
                    {"fuente": SourceEnum.REMAJU_RESOLUTION.value},
                    {"tipo_seccion": SectionEnum.BODY.value}
                ]
            }
        ),
        IntentRule(
            keywords=["cartel", "carteles", "aviso", "fijese", "juzgado"],
            metadata_filter={
                "$and": [
                    {"fuente": SourceEnum.REMAJU_RESOLUTION.value},
                    {"tipo_seccion": SectionEnum.FOOTER.value}
                ]
            }
        )
    ]