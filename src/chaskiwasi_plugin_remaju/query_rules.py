"""Reglas de consulta propias del plugin REMAJU."""

from __future__ import annotations

from chaskiwasi.query_engine.cross_filter import IntentRule


def get_query_rules() -> list[IntentRule]:
    return [
        IntentRule(
            keywords=("remate", "remaju", "resolución", "resolucion", "convocatoria"),
            metadata_filter={"fuente": "REMAJU_RESOLUTION"},
            priority=100,
        )
    ]
