"""Extracción determinista REMAJU antes de recurrir a IA."""

from __future__ import annotations

import re
from typing import Iterable, Mapping, Sequence

from chaskiwasi.plugins.contracts import ExtractionContext

_LABELS = (
    "EXPEDIENTE",
    "MATERIA",
    "JUEZ",
    "ESPECIALISTA",
    "MARTILLERO",
    "PERITO",
    "DEMANDADO",
    "DEMANDANTE",
    "EJECUTADO",
    "EJECUTANTE",
    "INMUEBLE",
    "DIRECCION",
    "DIRECCIÓN",
    "UBICACION",
    "UBICACIÓN",
    "PUBLICIDAD",
    "CARTEL",
    "AVISO",
)

_PARTY_LABELS = {
    "demandante": ("DEMANDANTE", "EJECUTANTE"),
    "demandado": ("DEMANDADO", "EJECUTADO"),
}

_NEXT_LABEL_RE = re.compile(
    r"^\s*(?:[-*•]\s*)?(?:DEMANDANTE|DEMANDADO|EJECUTANTE|EJECUTADO|"
    r"EXPEDIENTE|MATERIA|JUEZ|ESPECIALISTA|MARTILLERO|PERITO|INMUEBLE|"
    r"DIRECCI(?:Ó|O)N|UBICACI(?:Ó|O)N|PUBLICIDAD|CARTEL|AVISO)\s*[:|.-]?\s*",
    re.IGNORECASE,
)

_LABEL_RE = {
    label: re.compile(
        rf"^\s*(?:[-*•]\s*)?{re.escape(label)}\s*(?:[:|.-])?\s*(.*)$",
        re.IGNORECASE,
    )
    for label in _LABELS
}

_CARTEL_EFFECTIVE_PATTERNS = (
    r"\b(?:f[ií]j(?:e|ese|en|ense)|fijar|fijese|fíjese)\b[^.\n]{0,180}\bcartel(?:es)?\b",
    r"\b(?:peg(?:ar|ado|uen|uense)|pegue|pegar)\b[^.\n]{0,180}\bcartel(?:es)?\b",
    r"\b(?:coloc(?:ar|ado|uen|quese)|coloque|colocar)\b[^.\n]{0,180}\bcartel(?:es)?\b",
)


def _clean(value: str) -> str:
    value = re.sub(r"[*_`#]+", "", value)
    value = re.sub(r"\s+", " ", value)
    return value.strip(" \t|:-")


def _lines(text: str) -> list[str]:
    result: list[str] = []
    for raw in text.splitlines():
        line = _clean(raw)
        if line:
            result.append(line)
    return result


def _is_label_line(line: str) -> bool:
    return bool(_NEXT_LABEL_RE.match(line))


def _looks_like_party(value: str) -> bool:
    value = _clean(value)
    if not value or len(value) < 3:
        return False
    upper = value.upper()
    if upper in _LABELS:
        return False
    if re.search(r"\b(?:JUEZ|ESPECIALISTA|MARTILLERO|PERITO|SECRETARIO|ABOGAD[OA])\b", upper):
        return False
    return True


def _dedupe(values: Iterable[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        clean = _clean(value)
        key = re.sub(r"\s+", " ", clean).casefold()
        if clean and key not in seen:
            seen.add(key)
            result.append(clean)
    return result


def _extract_labeled_values(text: str, labels: Sequence[str]) -> list[str]:
    lines = _lines(text)
    normalized = {label.upper() for label in labels}
    values: list[str] = []
    active = False

    for line in lines:
        matched_label = None
        inline = ""
        for label in normalized:
            match = _LABEL_RE[label].match(line)
            if match:
                matched_label = label
                inline = _clean(match.group(1))
                break

        if matched_label is not None:
            active = True
            if inline and _looks_like_party(inline):
                values.append(inline)
            continue

        if active:
            if _is_label_line(line):
                active = False
                continue
            if _looks_like_party(line):
                values.append(line)

    return _dedupe(values)


def _extract_party_from_tables(text: str, labels: Sequence[str]) -> list[str]:
    target = {label.upper() for label in labels}
    values: list[str] = []
    for raw in text.splitlines():
        cells = [_clean(cell) for cell in raw.split("|")]
        cells = [cell for cell in cells if cell]
        if not cells:
            continue
        first = cells[0].upper()
        if first in target:
            values.extend(cell for cell in cells[1:] if _looks_like_party(cell))
    return _dedupe(values)


def _extract_parties(text: str) -> tuple[list[str], list[str]]:
    demandantes = _extract_labeled_values(text, _PARTY_LABELS["demandante"])
    demandados = _extract_labeled_values(text, _PARTY_LABELS["demandado"])

    if not demandantes:
        demandantes = _extract_party_from_tables(text, _PARTY_LABELS["demandante"])
    if not demandados:
        demandados = _extract_party_from_tables(text, _PARTY_LABELS["demandado"])

    return demandantes, demandados


def _extract_address(text: str) -> str:
    lines = _lines(text)
    candidates: list[str] = []
    active = False

    for line in lines:
        match = None
        for label in ("INMUEBLE", "DIRECCION", "DIRECCIÓN", "UBICACION", "UBICACIÓN"):
            match = _LABEL_RE[label].match(line)
            if match:
                break
        if match:
            inline = _clean(match.group(1))
            active = True
            if inline and len(inline) >= 8:
                candidates.append(inline)
            continue

        if active:
            if _is_label_line(line):
                break
            if re.search(
                r"\b(?:JR\.?|JIRON|AV\.?|AVENIDA|CALLE|PASAJE|PSJE\.?|MZ\.?|MANZANA|LOTE|"
                r"URB\.?|URBANIZACI(?:Ó|O)N|CENTRO POBLADO|DISTRITO|PROVINCIA|DEPARTAMENTO|"
                r"SECTOR|ETAPA|ASOCIACI(?:Ó|O)N)\b",
                line,
                re.IGNORECASE,
            ):
                candidates.append(line)

    return _clean(" ".join(_dedupe(candidates)))


def _requires_cartel(text: str) -> bool:
    return any(re.search(pattern, text, re.IGNORECASE | re.DOTALL) for pattern in _CARTEL_EFFECTIVE_PATTERNS)


def extract_remaju_data(context: ExtractionContext) -> dict:
    """Extrae primero de forma determinista; IA condicional se agrega en plugin.py."""
    demandantes, demandados = _extract_parties(context.text)
    direccion = _extract_address(context.text)
    requiere_cartel = _requires_cartel(context.text)

    return {
        "remate": {
            "demandantes": demandantes,
            "demandados": demandados,
        },
        "inmuebles": [
            {
                "direccion": direccion,
                "requiere_cartel": requiere_cartel,
            }
        ]
        if direccion or requiere_cartel
        else [],
    }


def get_domain_rules() -> Mapping[str, object]:
    """Expone patrones del dominio para inspección y pruebas."""
    return {
        "party_labels": _PARTY_LABELS,
        "cartel_patterns": _CARTEL_EFFECTIVE_PATTERNS,
    }
