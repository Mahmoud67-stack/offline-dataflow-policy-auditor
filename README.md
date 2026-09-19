# Offline Dataflow Policy Auditor

The auditor is an offline check for unsafe movement of sensitive inputs through a declarative pipeline graph before execution. It parses local JSON, validates the graph and policy, propagates source labels, and reports forbidden source-to-sink flows with paths. It does not claim to measure production risk reduction.

## Architecture

The implementation is a single-process Python package. It contains strict JSON parsing and validation, DAG construction and cycle detection, forward taint propagation, policy evaluation, diagnostic rendering, and deterministic JSON serialization. Internal `Node` records are immutable. The CLI reads explicit local files and never executes node commands or manifest values.

## Setup

The project targets Python 3.12. Runtime dependencies are empty; development dependencies are pinned in `requirements-dev.txt` and include pytest, Ruff, Mypy, and setuptools.

Install the package and development tools in an existing offline environment as appropriate for that environment. The configured console entry point is `pipeline-auditor`.

## Local execution

The supplied example can be run through the installed console script:

```bash
pipeline-auditor examples/pipeline.json --policy examples/policy.json --json
```

The example manifest contains ten nodes and the example policy forbids `sensitive`; the analysis therefore returns the policy-violation status. [evidence: examples/pipeline.json] [evidence: examples/policy.json]

The package does not provide `pipeline_auditor.__main__`, so `python -m pipeline_auditor ...` is not a supported invocation in this implementation. Running `src/pipeline_auditor/cli.py` directly is also not the documented interface because it uses package-relative imports.

Without `--json`, the CLI prints `clean` for a report without violations or a violation summary followed by source, sink, and path information. With `--json`, it emits machine-readable report data. The CLI returns status `0` for clean analysis, `1` when violations are found, and `2` for malformed or unreadable input. [evidence: src/pipeline_auditor/cli.py]

## Input formats

A manifest is an object containing only a `nodes` list. Each node has a unique non-empty string `id`, an optional `kind` of `source`, `transform`, or `sink`, and optional string-list `labels` and `inputs`. The default kind is `transform`. Source labels are taint origins; labels are joined across incoming edges.

A policy is an object with optional `forbidden` string labels and `exceptions`. Exceptions map named sink identifiers to allowed labels. Unknown fields and references, duplicate identifiers or list values, empty strings, invalid kinds, cycles, and malformed fields are rejected with `AnalysisError` diagnostics. [evidence: src/pipeline_auditor/core.py]

Reports contain nodes sorted by identifier, each with its joined taint labels, and violations containing the sink, source, label, and path. Distinct source origins remain distinct even when they use the same label. Stable sorting makes repeated in-process analysis and JSON rendering reproducible. [evidence: tests/test_cli.py] [evidence: tests/test_cli_determinism.py] [evidence: tests/test_taint_analysis.py]

## Verification

Run the available checks locally:

```bash
python -m pytest -q
python -m mypy src
python -m ruff check .
```

The latest objective gates reported that compilation, linting, type checking, dependency validation, secret scanning, placeholder scanning, required documentation, and the pytest suite passed. The pytest gate reported all collected tests passing. [evidence: objective evidence]

The independent review found that the core analysis and library-level validation are implemented and tested, but it did not verify the documented example command. It also found that the determinism and validation tests do not exercise the installed CLI through subprocesses as specified by the acceptance criteria. [evidence: objective evidence]

## Data provenance and security

There are no datasets or external services. The supplied examples are local, hand-authored JSON fixtures. Keep fixture values synthetic and do not place real secrets in manifests or policies. The analyzer operates on parsed in-memory data and explicit local input files, does not execute pipeline nodes, and does not interpolate manifest values into shell commands.

## Limitations and future work

The analyzer reasons only about declared graph structure and exact string labels. It does not infer runtime behavior, inspect commands, detect flows absent from the manifest, support wildcard labels, or consume an external policy source. Policy objects lacking both fields are currently accepted. Boundary coverage for empty or disconnected graphs and malformed JSON through the CLI is limited. [evidence: src/pipeline_auditor/core.py] [evidence: objective evidence]

Future work supported by the review findings would include adding the package module entry point, exercising the installed CLI through subprocess tests, asserting CLI nonzero statuses for validation failures, strengthening boundary-case coverage, and deciding whether policies with neither `forbidden` nor `exceptions` should be rejected. These are proposed improvements, not completed capabilities.