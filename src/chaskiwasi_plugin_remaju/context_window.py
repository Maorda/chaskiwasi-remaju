"""Localización de candidatos y ventanas contextuales de bajo consumo."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Iterable, Sequence


@dataclass(frozen=True)
class ContextWindow:
    """Ventana de chunks alrededor de un candidato."""

    start: int
    end: int
    chunks: tuple[str, ...]

    @property
    def text(self) -> str:
        return "\n\n".join(chunk.strip() for chunk in self.chunks if chunk.strip())


class CandidateWindowSelector:
    """Localiza chunks candidatos y amplía contexto progresivamente."""

    def __init__(self, chunker=None, initial_radius: int = 1, max_radius: int = 3) -> None:
        if initial_radius < 0:
            raise ValueError("initial_radius no puede ser negativo.")
        if max_radius < initial_radius:
            raise ValueError("max_radius debe ser >= initial_radius.")
        self._chunker = chunker
        self.initial_radius = initial_radius
        self.max_radius = max_radius

    def split(self, text: str) -> list[str]:
        if self._chunker is None:
            from chaskiwasi.chunking.chunk_tokenizer import ChunkTokenizer

            self._chunker = ChunkTokenizer()
        return self._chunker.split_text(text)

    @staticmethod
    def _matches(chunk: str, patterns: Sequence[str]) -> bool:
        return any(re.search(pattern, chunk, re.IGNORECASE) for pattern in patterns)

    def candidate_indexes(self, chunks: Sequence[str], patterns: Sequence[str]) -> list[int]:
        indexes: list[int] = []
        for index, chunk in enumerate(chunks):
            if self._matches(chunk, patterns):
                indexes.append(index)
        return indexes

    @staticmethod
    def merge_indexes(indexes: Iterable[int]) -> list[int]:
        return sorted(set(indexes))

    def window(self, chunks: Sequence[str], index: int, radius: int | None = None) -> ContextWindow:
        selected_radius = self.initial_radius if radius is None else radius
        if selected_radius < 0:
            raise ValueError("radius no puede ser negativo.")
        start = max(0, index - selected_radius)
        end = min(len(chunks), index + selected_radius + 1)
        return ContextWindow(start=start, end=end, chunks=tuple(chunks[start:end]))

    def expand(self, chunks: Sequence[str], index: int, current_radius: int) -> ContextWindow | None:
        if current_radius >= self.max_radius:
            return None
        next_radius = min(self.max_radius, max(current_radius + 1, 1))
        return self.window(chunks, index, next_radius)

    def grouped_windows(self, chunks: Sequence[str], indexes: Sequence[int], radius: int | None = None) -> list[ContextWindow]:
        if not indexes:
            return []
        selected_radius = self.initial_radius if radius is None else radius
        ranges: list[tuple[int, int]] = []
        for index in sorted(set(indexes)):
            ranges.append((max(0, index - selected_radius), min(len(chunks), index + selected_radius + 1)))

        merged: list[tuple[int, int]] = []
        for start, end in ranges:
            if not merged or start > merged[-1][1]:
                merged.append((start, end))
            else:
                merged[-1] = (merged[-1][0], max(merged[-1][1], end))

        return [ContextWindow(start, end, tuple(chunks[start:end])) for start, end in merged]
