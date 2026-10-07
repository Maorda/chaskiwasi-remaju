from chaskiwasi.plugins.contracts import ExtractionContext, PluginContext

from chaskiwasi_plugin_remaju.domain_rules import extract_remaju_data
from chaskiwasi_plugin_remaju.taxonomy import get_taxonomy


def context(text: str) -> ExtractionContext:
    taxonomy = get_taxonomy()
    return ExtractionContext(
        plugin=PluginContext("remaju", taxonomy),
        document_id="TEST-001",
        text=text,
        sections={},
    )


def test_extracts_parties_without_confusing_martillero():
    text = """
    EXPEDIENTE : 00157-2014-0-2406-JM-CI-01
    MATERIA : EJECUCION DE GARANTIAS
    JUEZ : VALENTIN MACEDONIO INOCENTE PAULINO
    MARTILLERO : RAMOS ROMANI, RUDY OSCAR
    PERITO : BRAVO MONDOÑEDO, JOAN CARLO
    DEMANDADO : MUCHA HINOSTROZA, CASIO FELIX
                 HUAYTA VILLANUEVA, HECTOR LUIS
    DEMANDANTE : DECAROPE SAC
    """
    result = extract_remaju_data(context(text))
    assert result["remate"]["demandantes"] == ["DECAROPE SAC"]
    assert result["remate"]["demandados"] == [
        "MUCHA HINOSTROZA, CASIO FELIX",
        "HUAYTA VILLANUEVA, HECTOR LUIS",
    ]


def test_extracts_markdown_table_parties():
    text = """
    | DEMANDANTE | DECAROPE SAC |
    | DEMANDADO | MUCHA HINOSTROZA, CASIO FELIX |
    """
    result = extract_remaju_data(context(text))
    assert result["remate"]["demandantes"] == ["DECAROPE SAC"]
    assert result["remate"]["demandados"] == ["MUCHA HINOSTROZA, CASIO FELIX"]


def test_cartel_requires_effective_order():
    historical = "Se publicaron avisos y carteles de remate anteriormente."
    effective = "Se dispone fijar carteles de remate en el local del juzgado y en el inmueble."
    assert extract_remaju_data(context(historical))["inmuebles"] == []
    result = extract_remaju_data(context(effective))
    assert result["inmuebles"][0]["requiere_cartel"] is True


def test_complex_address_is_collected_without_geocoding():
    text = """
    INMUEBLE : Centro Poblado Campo Verde Mz. 20 Lote 5A
    con frente al Psje. Central
    Distrito de Campo Verde, Provincia de Coronel Portillo,
    Departamento de Ucayali.
    """
    result = extract_remaju_data(context(text))
    assert "Centro Poblado Campo Verde" in result["inmuebles"][0]["direccion"]
    assert "Mz. 20 Lote 5A" in result["inmuebles"][0]["direccion"]
    assert "Ucayali" in result["inmuebles"][0]["direccion"]
