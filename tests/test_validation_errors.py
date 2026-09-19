from typing import Any

import pytest

from pipeline_auditor.core import AnalysisError, analyze


@pytest.mark.parametrize("manifest, policy, message", [
    ({"nodes": [{"id": "x", "inputs": ["missing"]}]}, {}, "undefined"),
    ({"nodes": [{"id": "x"}, {"id": "x"}]}, {}, "duplicate"),
    ({"nodes": [{"id": "x"}]}, {"forbidden": [""]}, "non-empty"),
    ({"nodes": [{"id": "x"}]}, {"exceptions": {"x": []}}, "sink"),
])
def test_invalid_inputs_are_actionable(
    manifest: dict[str, Any], policy: dict[str, Any], message: str
) -> None:
    with pytest.raises(AnalysisError, match=message):
        analyze(manifest, policy)
