"""Extractor semántico opcional de REMAJU con contexto mínimo."""

from __future__ import annotations

import json
import os
from typing import Any, Callable, Mapping

from .context_window import CandidateWindowSelector
from .gemini_rules import get_gemini_extraction_config


GenerateFn = Callable[[str, Mapping[str, Any]], str]


class RemaJuSemanticExtractor:
    """Invoca Gemini únicamente cuando la extracción determinista necesita fallback."""

    def __init__(
        self,
        generate: GenerateFn | None = None,
        selector: CandidateWindowSelector | None = None,
    ) -> None:
        self._generate = generate
        self._selector = selector or CandidateWindowSelector()
        self._config = get_gemini_extraction_config()

    @property
    def selector(self) -> CandidateWindowSelector:
        return self._selector

    def split_chunks(self, text: str) -> list[str]:
        return self._selector.split(text)

    @property
    def enabled(self) -> bool:
        return self._generate is not None or bool(os.getenv("GEMINI_API_KEY", "").strip())

    def _default_generate(self, text: str, config: Mapping[str, Any]) -> str:
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:
            raise RuntimeError(
                "La extracción Gemini requiere instalar el extra '[gemini]' del plugin."
            ) from exc

        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("No existe la variable de entorno GEMINI_API_KEY.")

        client = genai.Client(api_key=api_key)
        model_name = os.getenv("REMAJU_GEMINI_MODEL", str(config["model_name"]))
        max_output = int(os.getenv("REMAJU_GEMINI_MAX_OUTPUT_TOKENS", "256"))
        response = client.models.generate_content(
            model=model_name,
            contents=config["prompt_template"].format(text=text),
            config=types.GenerateContentConfig(
                system_instruction=config["system_instruction"],
                temperature=0.0,
                max_output_tokens=max_output,
                response_mime_type="application/json",
                response_schema=config["response_schema"],
            ),
        )
        return str(getattr(response, "text", "") or "")

    def generate(self, text: str) -> dict[str, Any]:
        generator = self._generate or self._default_generate
        raw = generator(text, self._config)
        if not raw.strip():
            return {}
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            raise ValueError("Gemini no devolvió un objeto JSON.")
        return parsed

    def extract_from_candidates(
        self,
        chunks: list[str],
        candidate_patterns: tuple[str, ...],
    ) -> dict[str, Any]:
        indexes = self._selector.candidate_indexes(chunks, candidate_patterns)
        if not indexes:
            return {}

        windows = self._selector.grouped_windows(chunks, indexes)
        merged: dict[str, Any] = {}
        for window in windows:
            result = self.generate(window.text)
            if result:
                merged = _merge_results(merged, result)
        return merged


def _merge_results(base: dict[str, Any], incoming: Mapping[str, Any]) -> dict[str, Any]:
    result = dict(base)
    base_remate = dict(result.get("remate") or {})
    incoming_remate = dict(incoming.get("remate") or {})
    base_remate["demandantes"] = _merge_lists(base_remate.get("demandantes"), incoming_remate.get("demandantes"))
    base_remate["demandados"] = _merge_lists(base_remate.get("demandados"), incoming_remate.get("demandados"))
    result["remate"] = base_remate

    incoming_properties = incoming.get("inmuebles") or []
    if incoming_properties:
        result["inmuebles"] = list(result.get("inmuebles") or []) + list(incoming_properties)
    elif "inmuebles" not in result:
        result["inmuebles"] = []
    return result


def _merge_lists(first: Any, second: Any) -> list[str]:
    result: list[str] = []
    for value in list(first or []) + list(second or []):
        clean = str(value).strip()
        if clean and clean.casefold() not in {item.casefold() for item in result}:
            result.append(clean)
    return result
