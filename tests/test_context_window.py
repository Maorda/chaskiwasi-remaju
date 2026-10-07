from chaskiwasi_plugin_remaju.context_window import CandidateWindowSelector


def test_initial_window_contains_neighbors():
    selector = CandidateWindowSelector(initial_radius=1, max_radius=3)
    chunks = ["uno", "DEMANDADO", "tres", "cuatro"]
    window = selector.window(chunks, 1)
    assert window.start == 0
    assert window.end == 3
    assert window.chunks == ("uno", "DEMANDADO", "tres")


def test_nearby_candidates_are_grouped_into_one_window():
    selector = CandidateWindowSelector(initial_radius=1, max_radius=3)
    chunks = ["0", "DEMANDANTE", "2", "DEMANDADO", "4", "5"]
    windows = selector.grouped_windows(chunks, [1, 3])
    assert len(windows) == 1
    assert windows[0].chunks == tuple(chunks[:5])


def test_candidate_detection_is_zero_cost_and_deterministic():
    selector = CandidateWindowSelector(initial_radius=1, max_radius=3)
    chunks = ["texto", "INMUEBLE", "texto", "DIRECCIÓN", "texto"]
    indexes = selector.candidate_indexes(chunks, (r"\bINMUEBLE\b", r"\bDIRECCIÓN\b"))
    assert indexes == [1, 3]
