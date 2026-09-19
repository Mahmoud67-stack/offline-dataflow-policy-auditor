# Portfolio and verification notes

## Truthful role evidence

This project is evidence of work relevant to application security engineering, static analysis engineering, and developer tooling:

- Built a typed Python analyzer for declarative dataflow manifests.
- Implemented strict input validation, DAG construction, cycle detection, forward taint propagation, sink policy evaluation, path reconstruction, and deterministic reporting.
- Implemented an offline argparse-based CLI with human-readable and JSON output and distinct clean, violation, and invalid-input statuses.
- Designed tests for taint joins, policy exceptions, cycles, undefined references, duplicate identifiers, malformed policy fields, same-label origins, and deterministic reports. [evidence: tests/test_analysis.py] [evidence: tests/test_cli.py] [evidence: tests/test_cli_determinism.py] [evidence: tests/test_taint_analysis.py] [evidence: tests/test_validation_errors.py]

## Skill evidence

- **Abstract interpretation and taint analysis:** labels are propagated forward through a DAG and joined at merges.
- **Graph algorithms:** heap-backed Kahn topological ordering detects cycles and supplies analysis order.
- **Policy as code:** forbidden labels and sink-specific exceptions are parsed and evaluated as data.
- **Deterministic serialization:** stable sorting produces repeatable node, path, violation, and JSON output.
- **CLI design:** local file loading, actionable errors, human-readable diagnostics, JSON output, and status mapping are implemented in `cli.py`. [evidence: src/pipeline_auditor/core.py] [evidence: src/pipeline_auditor/cli.py]

## Interview talking points

- Explain why origin-aware path records are retained instead of keeping only labels: two sources with the same label must still produce separate actionable flows.
- Explain how topological ordering both supports forward propagation and exposes cycles before analysis.
- Discuss why deterministic sorting matters for reviewable reports and tests.
- Discuss the boundary between declared-graph auditing and runtime security claims.
- Describe the trade-off between exact string policies and a more expressive policy language.
- Be explicit that the package has no `__main__.py`, so the documented `python -m pipeline_auditor` form is unsupported, and that CLI subprocess coverage remains incomplete. [evidence: objective evidence]

## Challenges and trade-offs

The main design challenge was preserving explainable paths while propagating labels through joins. The implementation stores both taint sets and origin/path records, trading additional analysis state for diagnostics that identify source, label, sink, and route.

The tool favors a small, offline, exact-label policy model over runtime inspection or wildcard policy semantics. This makes behavior reviewable but means it cannot infer undeclared flows, inspect node commands, detect runtime behavior, or use an external policy source. Policies with neither `forbidden` nor `exceptions` are currently accepted. [evidence: src/pipeline_auditor/core.py] [evidence: objective evidence]

## Description options

- Offline Python CLI that audits declarative pipeline graphs for forbidden tainted flows and emits deterministic, path-based diagnostics.
- Typed dataflow policy auditor combining DAG validation, origin-aware taint propagation, sink exceptions, and reproducible JSON reporting.
- Explainable static analysis tool for local pipeline manifests, designed for review before execution rather than claims about production risk reduction.

## Bullet options

- Implemented an offline Python dataflow auditor that validates manifests, detects cycles and undefined references, propagates taint labels through DAG joins, and reports forbidden sink flows with source-to-sink paths.
- Added deterministic node and violation ordering plus JSON and human-readable CLI diagnostics to make policy findings reproducible and reviewable.
- Tested policy exceptions, malformed inputs, cycle detection, taint joins, same-label source origins, and stable report generation. [evidence: tests/]
- Verified the repository with the configured pytest, Ruff, and Mypy checks; review findings document remaining CLI invocation and subprocess-coverage gaps. [evidence: objective evidence]

These statements describe implementation and verification evidence only; they do not claim production deployment, measured performance, or business impact.