from pipeline_auditor.core import analyze


def test_same_label_origins_are_reported_separately() -> None:
    manifest = {"nodes": [
        {"id": "a", "kind": "source", "labels": ["secret"]},
        {"id": "b", "kind": "source", "labels": ["secret"]},
        {"id": "sink", "kind": "sink", "inputs": ["a", "b"]},
    ]}
    violations = analyze(manifest, {"forbidden": ["secret"]})["violations"]
    assert [(item["source"], item["path"]) for item in violations] == [
        ("a", ["a", "sink"]), ("b", ["b", "sink"])
    ]
