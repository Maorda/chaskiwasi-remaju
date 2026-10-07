from chaskiwasi_plugin_remaju.context_window import CandidateWindowSelector
from chaskiwasi_plugin_remaju.semantic_extractor import RemaJuSemanticExtractor


def test_gemini_receives_only_candidate_window():
    calls = []

    def fake_generate(text, config):
        calls.append(text)
        return '{"remate":{"demandantes":[],"demandados":[]},"inmuebles":[{"direccion":"Mz. 20 Lote 5A","requiere_cartel":false}]}'

    selector = CandidateWindowSelector(initial_radius=1, max_radius=3)
    extractor = RemaJuSemanticExtractor(generate=fake_generate, selector=selector)
    chunks = ["ruido 0", "INMUEBLE:", "Mz. 20 Lote 5A", "ruido 3", "ruido 4"]
    result = extractor.extract_from_candidates(chunks, (r"\bINMUEBLE\b",))

    assert len(calls) == 1
    assert "INMUEBLE" in calls[0]
    assert "ruido 3" not in calls[0]
    assert "ruido 4" not in calls[0]
    assert result["inmuebles"][0]["direccion"] == "Mz. 20 Lote 5A"


def test_gemini_config_does_not_invoke_network():
    from chaskiwasi_plugin_remaju.gemini_rules import get_gemini_extraction_config

    config = get_gemini_extraction_config()
    assert config["model_name"] == "gemini-1.5-flash"
    assert "TEXTO:" in config["prompt_template"]


def test_semantic_fallback_is_conditional():
    from chaskiwasi_plugin_remaju.plugin import _needs_semantic_fallback

    complete = {
        "remate": {"demandantes": ["DECAROPE SAC"], "demandados": ["MUCHA HINOSTROZA"]},
        "inmuebles": [{"direccion": "Jr. Lima 100", "requiere_cartel": False}],
    }
    assert _needs_semantic_fallback("DEMANDANTE: DECAROPE SAC", complete) is False

    missing_party = {
        "remate": {"demandantes": [], "demandados": ["MUCHA HINOSTROZA"]},
        "inmuebles": [],
    }
    assert _needs_semantic_fallback("DEMANDANTE: pendiente", missing_party) is True

    complex_address = {
        "remate": {"demandantes": ["DECAROPE SAC"], "demandados": ["MUCHA HINOSTROZA"]},
        "inmuebles": [{"direccion": "Centro Poblado Campo Verde Mz. 20 Lote 5A", "requiere_cartel": False}],
    }
    assert _needs_semantic_fallback("INMUEBLE", complex_address) is True
