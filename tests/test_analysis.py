from pipeline_auditor.core import AnalysisError, analyze


def test_join_and_paths() -> None:
    manifest = {"nodes": [
        {"id": "a", "kind": "source", "labels": ["secret"]},
        {"id": "b", "kind": "source", "labels": ["public"]},
        {"id": "join", "inputs": ["a", "b"]},
        {"id": "out", "kind": "sink", "inputs": ["join"]},
    ]}
    report = analyze(manifest, {"forbidden": ["secret"]})
    assert report["nodes"][2]["taint"] == ["public", "secret"]
    assert report["violations"][0]["path"] == ["a", "join", "out"]


def test_exception_and_cycle() -> None:
    clean = {"nodes": [{"id": "s", "kind": "source", "labels": ["x"]}, {"id": "o", "kind": "sink", "inputs": ["s"]}]}
    assert not analyze(clean, {"forbidden": ["x"], "exceptions": {"o": ["x"]}})["violations"]
    cyclic = {"nodes": [{"id": "a", "inputs": ["b"]}, {"id": "b", "inputs": ["a"]}]}
    try:
        analyze(cyclic, {"forbidden": []})
        assert False
    except AnalysisError as exc:
        assert "cycle" in str(exc)
