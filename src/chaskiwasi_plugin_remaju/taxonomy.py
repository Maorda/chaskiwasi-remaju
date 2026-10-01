# D:\libs\chaskiwasi_plugin_remaju\src\chaskiwasi_plugin_remaju\taxonomy.py
"""
Registro de taxonomía para el plugin REMAJU.
"""
from enum import Enum


class SourceEnum(Enum):
    REMAJU_RESOLUTION = "remaju_resolution"


class SectionEnum(Enum):
    HEADER = "header"
    BODY = "body"
    FOOTER = "footer"


def get_taxonomy_registry():
    """
    Función contractual que el Entry Point invocará dinámicamente.
    Retorna la tupla exacta (Source, Section) requerida por el core de chaskiwasi.
    """
    return SourceEnum, SectionEnum