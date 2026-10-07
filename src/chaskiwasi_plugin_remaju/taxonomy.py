"""Taxonomía propia del plugin REMAJU."""

from __future__ import annotations

from enum import Enum

from chaskiwasi.config.taxonomy_registry import Taxonomy, TaxonomyRegistry


class SourceEnum(Enum):
    REMAJU_RESOLUTION = "remaju_resolution"


class SectionEnum(Enum):
    HEADER = "header"
    BODY = "body"
    FOOTER = "footer"


def get_taxonomy() -> Taxonomy:
    return Taxonomy(
        name="remaju",
        source_enum=SourceEnum,
        section_enum=SectionEnum,
    )


def get_taxonomy_registry() -> TaxonomyRegistry:
    """Registra y retorna la taxonomía REMAJU en el registro del core."""
    taxonomy = get_taxonomy()
    TaxonomyRegistry.register("remaju", taxonomy)
    return TaxonomyRegistry
