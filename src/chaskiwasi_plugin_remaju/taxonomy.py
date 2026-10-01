"""
Registro de taxonomía para el plugin REMAJU.
"""

def get_taxonomy_registry():
    # Lazy Loading: importación dentro de la función de fábrica
    from chaskiwasi.config.taxonomy_registry import (
        TaxonomyRegistry,
        SourceEnum,
        SectionEnum,
        FieldDefinition,
        FieldType,
    )

    registry = TaxonomyRegistry()
    
    # Registro de Fuente
    source = SourceEnum.REMAJU_RESOLUTION
    
    # Definición de Secciones
    registry.register_section_bounds(
        source=source,
        bounds={
            SectionEnum.HEADER: (0.0, 0.20),
            SectionEnum.BODY: (0.20, 0.80),
            SectionEnum.FOOTER: (0.80, 1.00),
        }
    )

    # Definición de Campos Objetivo
    fields = [
        FieldDefinition(
            name="demandantes",
            field_type=FieldType.LIST_STRING,
            section=SectionEnum.HEADER,
            description="Nombres y apellidos de la parte demandante/ejecutante",
        ),
        FieldDefinition(
            name="demandados",
            field_type=FieldType.LIST_STRING,
            section=SectionEnum.HEADER,
            description="Nombres y apellidos de la parte demandada/ejecutada",
        ),
        FieldDefinition(
            name="direccion_inmueble",
            field_type=FieldType.STRING,
            section=SectionEnum.BODY,
            description="Ubicación o dirección completa del inmueble a rematar",
        ),
        FieldDefinition(
            name="requiere_cartel",
            field_type=FieldType.BOOLEAN,
            section=SectionEnum.FOOTER,
            description="Indica si se ordena fijar carteles en los inmuebles o local del juzgado",
        ),
    ]

    for field in fields:
        registry.register_field(source=source, field=field)

    return registry