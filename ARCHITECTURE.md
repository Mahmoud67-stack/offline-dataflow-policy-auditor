# Architecture

## Components

The package is a single-process Python implementation with these cooperating parts:

- `load_json` reads an explicitly supplied local file and converts file or JSON errors into `AnalysisError`.
- `_parse` validates the manifest and policy and converts nodes into immutable, frozen `Node` records.
- Graph construction derives parent-to-child adjacency lists and indegrees.
- Kahn's topological sort processes the DAG with a heap and detects cycles when not all nodes can be ordered.
- Forward analysis propagates source labels and origin/path records through the topological order.
- Policy evaluation compares labels reaching sinks with forbidden label/sink pairs and applies sink-specific exceptions.
- `cli.main` renders human-readable diagnostics or compact JSON and maps analysis outcomes to process statuses.

## Data flow

The CLI receives a manifest path and a policy path. `load_json` parses both local files. `_parse` checks the manifest shape, node identifiers, kinds, labels, inputs, references, policy fields, and exception sinks. Valid nodes become immutable records.

The analyzer builds reverse adjacency information from each node's `inputs`. A heap-backed topological traversal produces a stable processing order and rejects cycles. A source contributes its declared labels and origin path. Each downstream node receives every label and every origin/path record from its inputs; at a merge, label sets are unioned and path records are retained per source origin. Sink evaluation emits a violation for each reachable forbidden source-to-sink flow not covered by that sink's exception.

The report contains identifier-sorted node taint data and stably sorted violation records. JSON serialization uses sorted keys and compact separators in the CLI. [evidence: src/pipeline_auditor/core.py] [evidence: src/pipeline_auditor/cli.py]

## Control flow and error handling

The CLI catches `AnalysisError`. Invalid files, malformed JSON, invalid schema data, undefined references, duplicate identifiers or values, invalid exception sinks, and cycles produce an actionable error and status `2`. A valid report produces status `1` when violations exist and status `0` otherwise. Human-readable input errors are written to standard error; JSON mode emits an error object. [evidence: src/pipeline_auditor/cli.py] [evidence: tests/test_validation_errors.py]

Analysis is iterative over the finite graph rather than recursive. Manifest content is treated as data: no node command is executed, and the implementation does not interpolate manifest values into shell commands.

## Engineering decisions

- **Immutable parsed records:** frozen `Node` values separate validated input from analysis state.
- **Topological processing:** DAG order makes forward propagation explicit and makes cycles a validation error.
- **Set-based label joins:** union models the fact that every declared incoming taint label reaches a merge.
- **Origin-aware paths:** path records include the source node, label, and complete route, so equal labels from different sources remain separately actionable.
- **Stable ordering:** sorted identifiers, labels, inputs, paths, and report fields provide reproducible output without depending on input ordering.
- **Local-only operation:** explicit file inputs and no execution or network access keep the audit reviewable and offline.

## Alternatives and trade-offs

A recursive traversal could be shorter, but the implemented iterative topological approach makes cycle detection explicit and avoids recursion-depth dependence. A label-only analysis would use less state, but it could not report separate paths for distinct origins sharing one label. Retaining origin/path records increases state relative to simple taint sets, in exchange for explainable diagnostics.

The analyzer intentionally uses exact string labels rather than wildcard matching or an external policy language. This keeps the policy representation small and deterministic, but limits expressiveness. The implementation reports declared-graph behavior rather than runtime behavior; that trade-off supports explainability and offline review but cannot identify undeclared flows or command-level behavior.

## Verification and known gaps

The objective gates passed compilation, Ruff, Mypy, dependency validation, secret scanning, placeholder scanning, required documentation, and the pytest suite. [evidence: objective evidence]

The review confirmed the core parser, cycle detection, topological ordering, taint joins, per-origin paths, exceptions, deterministic reporting, and status mapping. It also identified gaps: the package lacks `__main__.py`; the documented module invocation is unsupported; the example command was not independently evidenced; determinism and validation tests call code in-process rather than exercising the CLI as subprocesses; boundary coverage is thin; and policies with neither field are accepted. [evidence: objective evidence]