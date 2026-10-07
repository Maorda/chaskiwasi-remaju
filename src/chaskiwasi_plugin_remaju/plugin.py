"""Registro del plugin REMAJU para Chaskiwasi 0.3.x."""

from __future__ import annotations

from typing import Sequence
import re

from chaskiwasi.classification.strategies.base_strategy import BaseStrategy
from chaskiwasi.classification.strategies.context_overlap_strategy import ContextOverlapStrategy
from chaskiwasi.classification.strategies.cpu_regex_strategy import CPURegexStrategy, RegexRule
from chaskiwasi.plugins.contracts import ExtractionContext, PluginContext, PluginDefinition

from .domain_rules import extract_remaju_data
from .gemini_rules import get_gemini_extraction_config
from .query_rules import get_query_rules
from .taxonomy import SectionEnum, SourceEnum, get_taxonomy


def create_strategies(context: PluginContext) -> Sequence[BaseStrategy]:
    taxonomy = context.taxonomy
    if not taxonomy.contains_source(SourceEnum.REMAJU_RESOLUTION):
        raise ValueError("La taxonomía activa no corresponde a REMAJU.")

    rules = [
        RegexRule(
            source=SourceEnum.REMAJU_RESOLUTION,
            section=SectionEnum.HEADER,
            patterns=[
                r"\bEXPEDIENTE\s*[:#]",
                r"\bDEMANDANTE\s*[:|]",
                r"\bDEMANDADO\s*[:|]",
                r"\bEJECUTANTE\s*[:|]",
                r"\bEJECUTADO\s*[:|]",
            ],
        ),
        RegexRule(
            source=SourceEnum.REMAJU_RESOLUTION,
            section=SectionEnum.BODY,
            patterns=[
                r"\bDESCRIPCI(?:Ó|O)N\s*[:.]",
                r"\bUBICACI(?:Ó|O)N\s*[:.]",
                r"\bINMUEBLE\b",
                r"\bDIRECCI(?:Ó|O)N\b",
                r"\bTASACI(?:Ó|O)N\b",
                r"\bVALOR\s+COMERCIAL\b",
            ],
        ),
        RegexRule(
            source=SourceEnum.REMAJU_RESOLUTION,
            section=SectionEnum.FOOTER,
            patterns=[
                r"\bF[IÍ]JE(?:SE|NSE)?\b",
                r"\bORD[EÉ]NE(?:SE|NSE)?\b",
                r"\bDISP[ÓO]NGA(?:SE|N)?\b",
                r"\bCARTEL(?:ES)?\b",
                r"\bNOTIF[IÍ]QUE(?:SE|N)?\b",
                r"\bPUBLICIDAD\b",
            ],
        ),
    ]
    return (CPURegexStrategy(rules), ContextOverlapStrategy())


def _extractor(context: ExtractionContext) -> dict:
    """Primera línea determinista; Gemini solo se activa ante necesidad explícita."""
    result = extract_remaju_data(context)

    import os

    enabled = os.getenv("REMAJU_ENABLE_GEMINI", "").strip().lower() in {"1", "true", "yes", "si", "sí"}
    if not enabled:
        return result

    if not _needs_semantic_fallback(context.text, result):
        return result

    from .semantic_extractor import RemaJuSemanticExtractor

    semantic_extractor = RemaJuSemanticExtractor()
    chunks = semantic_extractor.split_chunks(context.text)
    semantic = semantic_extractor.extract_from_candidates(
        chunks,
        (
            r"\bDEMANDANTE\b",
            r"\bDEMANDADO\b",
            r"\bEJECUTANTE\b",
            r"\bEJECUTADO\b",
            r"\bINMUEBLE\b",
            r"\bDIRECCI(?:Ó|O)N\b",
            r"\bUBICACI(?:Ó|O)N\b",
            r"\bPUBLICIDAD\b",
            r"\bCARTEL(?:ES)?\b",
        ),
    )
    return _merge_deterministic_and_semantic(result, semantic)


def _needs_semantic_fallback(text: str, result: dict) -> bool:
    """Determina si queda una extracción ambigua que justifica gastar tokens."""
    remate = result.get("remate") or {}
    inmuebles = result.get("inmuebles") or []
    direccion = str(inmuebles[0].get("direccion", "")) if inmuebles else ""

    if not remate.get("demandantes") or not remate.get("demandados"):
        if any(token in text.upper() for token in ("DEMANDANTE", "DEMANDADO", "EJECUTANTE", "EJECUTADO")):
            return True

    if not direccion and any(token in text.upper() for token in ("INMUEBLE", "DIRECCIÓN", "DIRECCION", "UBICACIÓN", "UBICACION")):
        return True

    complex_address = re.search(
        r"\b(?:MZ\.?|MANZANA|LOTE|CENTRO POBLADO|SECTOR|ETAPA|ASOCIACI(?:Ó|O)N|\bCON FRENTE A)\b",
        direccion,
        re.IGNORECASE,
    )
    return bool(complex_address)


def _merge_deterministic_and_semantic(deterministic: dict, semantic: dict) -> dict:
    result = {
        "remate": {
            "demandantes": list(deterministic.get("remate", {}).get("demandantes", [])),
            "demandados": list(deterministic.get("remate", {}).get("demandados", [])),
        },
        "inmuebles": list(deterministic.get("inmuebles", [])),
    }

    remate = semantic.get("remate") or {}
    if not result["remate"]["demandantes"]:
        result["remate"]["demandantes"] = list(remate.get("demandantes") or [])
    if not result["remate"]["demandados"]:
        result["remate"]["demandados"] = list(remate.get("demandados") or [])

    semantic_properties = semantic.get("inmuebles") or []
    if not result["inmuebles"] and semantic_properties:
        result["inmuebles"] = semantic_properties
    elif result["inmuebles"] and semantic_properties:
        first = result["inmuebles"][0]
        semantic_first = semantic_properties[0]
        if not first.get("direccion") and semantic_first.get("direccion"):
            first["direccion"] = semantic_first["direccion"]
        if not first.get("requiere_cartel") and semantic_first.get("requiere_cartel"):
            first["requiere_cartel"] = True

    return result


def create_plugin() -> PluginDefinition:
    return PluginDefinition(
        name="remaju",
        taxonomy=get_taxonomy(),
        strategy_factory=create_strategies,
        query_rules_factory=get_query_rules,
        extractor=_extractor,
        metadata={
            "domain": "remates judiciales peruanos",
            "gemini_extraction_config": get_gemini_extraction_config(),
        },
    )
