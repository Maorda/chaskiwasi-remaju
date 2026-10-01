# Plugin Chaskiwasi - REMAJU

Este plugin permite la detección y extracción estructurada de datos relevantes en resoluciones judiciales de remate electrónico (`REM@JU`):
- Nombres de Demandante(s)
- Nombres de Demandado(s)
- Dirección del Inmueble
- Indicador de requerimiento de fijación de Cartel

## Instalación
```bash
pip install -e .
```
---

## 3. `src/chaskiwasi_remaju/__init__.py`
```python

"""
Módulo principal del plugin chaskiwasi-remaju.
Aplica Lazy Loading estricto para no importar enums globales a nivel de módulo.
"""

def get_taxonomy_registry():
    from chaskiwasi_remaju.taxonomy import get_taxonomy_registry as _get_taxonomy
    return _get_taxonomy()

def get_query_rules():
    from chaskiwasi_remaju.query_rules import get_query_rules as _get_query_rules
    return _get_query_rules()

def create_cascade_factory():
    from chaskiwasi_remaju.factory import create_cascade_factory as _create_factory
    return _create_factory()

__all__ = [
    "get_taxonomy_registry",
    "get_query_rules",
    "create_cascade_factory",
]
```