import json

from pipeline_auditor.core import analyze


def test_ten_node_report_is_valid_and_ordered() -> None:
    with open("examples/pipeline.json", encoding="utf-8") as stream:
        manifest = json.load(stream)
    with open("examples/policy.json", encoding="utf-8") as stream:
        policy = json.load(stream)
    first = analyze(manifest, policy)
    second = analyze(manifest, policy)
    assert json.loads(json.dumps(first)) == first
    assert first == second
    assert len(first["nodes"]) == 10
    assert first["violations"] == sorted(
        first["violations"], key=lambda item: (item["sink"], item["source"], item["path"])
    )
