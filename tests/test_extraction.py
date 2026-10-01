from chaskiwasi_plugin_remaju import create_cascade_factory, get_query_rules
from chaskiwasi_plugin_remaju.domain_rules import extract_remaju_data


def test_extract_remaju_data():
    # Simulación de texto extraído del PDF
    sample_text = """
    5°JUZGADO CIVIL-COMERCIAL
    EXPEDIENTE : 28649-2024-0-1828-JR-CO-05
    DEMANDADO : ROMERO VASQUEZ, RONY WILFREDO
    : ROMERO VASQUEZ, JHONNY ORLANDO
    DEMANDANTE : BANCO BBVA PERU

    A. DESCRIPCIÓN:
    - Ubicación: casa de 1 piso con frente a la Calle 32, Manzana A-2, lote 6 de la Urbanización Zárate-Sector A, distrito de San Juan de Lurigancho, Provincia y Departamento de Lima.

    F. FÍJESE los Carteles en el local del Juzgado y en los inmuebles materia de ejecución
    """

    # Prueba directa de la función de extracción
    data = extract_remaju_data(sample_text, {})

    # Validaciones contractuales de extracción
    assert "BANCO BBVA PERU" in data["demandantes"]
    assert "ROMERO VASQUEZ, RONY WILFREDO" in data["demandados"]
    assert data["direccion_inmueble"] is not None
    assert "San Juan de Lurigancho" in data["direccion_inmueble"]
    assert data["requiere_cartel"] is True


def test_factory_and_rules_loading():
    # Validación simple de que los Entry Points exponen sus fábricas correctamente
    rules = get_query_rules()
    factory = create_cascade_factory()

    assert rules is not None
    assert factory is not None