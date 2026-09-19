import json
import tempfile

from pytest import CaptureFixture

from pipeline_auditor.cli import main


def test_json_is_deterministic(capsys: CaptureFixture[str]) -> None:
    manifest = {"nodes": [{"id": "z", "kind": "sink", "inputs": ["s"]}, {"id": "s", "kind": "source", "labels": ["x"]}]}
    policy = {"forbidden": ["x"]}
    with tempfile.TemporaryDirectory() as directory:
        m, p = f"{directory}/m.json", f"{directory}/p.json"
        with open(m, "w") as manifest_file:
            manifest_file.write(json.dumps(manifest))
        with open(p, "w") as policy_file:
            policy_file.write(json.dumps(policy))
        assert main([m, "--policy", p, "--json"]) == 1
        first = capsys.readouterr().out
        assert main([m, "--policy", p, "--json"]) == 1
        assert first == capsys.readouterr().out
