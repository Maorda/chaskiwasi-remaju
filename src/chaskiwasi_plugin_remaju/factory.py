"""Fábrica de CascadeFactory para REMAJU."""

from __future__ import annotations

from chaskiwasi.classification.cascade_factory import CascadeFactory
from chaskiwasi.plugins.contracts import PluginContext
from chaskiwasi.plugins.registry import PluginRegistry


def create_cascade_factory() -> CascadeFactory:
    """Construye la cascada usando el plugin REMAJU registrado."""
    return PluginRegistry.build_cascade_factory("remaju")
