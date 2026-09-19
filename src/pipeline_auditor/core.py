"""Parsing, validation, graph analysis, and deterministic reporting."""
from __future__ import annotations

import heapq
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class AnalysisError(ValueError):
    """An actionable manifest or policy error."""


@dataclass(frozen=True)
class Node:
    identifier: str
    kind: str
    labels: tuple[str, ...]
    inputs: tuple[str, ...]


def load_json(path: str) -> Any:
    try:
        with Path(path).open(encoding="utf-8") as stream:
            return json.load(stream)
    except (OSError, json.JSONDecodeError) as exc:
        raise AnalysisError(f"cannot read JSON file {path}: {exc}") from exc


def _strings(value: Any, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or any(not isinstance(item, str) or not item for item in value):
        raise AnalysisError(f"{field} must be a list of non-empty strings")
    if len(set(value)) != len(value):
        raise AnalysisError(f"{field} contains duplicate values")
    return tuple(sorted(value))


def _parse(manifest: Any, policy: Any) -> tuple[dict[str, Node], set[tuple[str, str]]]:
    if not isinstance(manifest, dict) or set(manifest) != {"nodes"} or not isinstance(manifest["nodes"], list):
        raise AnalysisError("manifest must contain only a nodes list")
    nodes: dict[str, Node] = {}
    for raw in manifest["nodes"]:
        if not isinstance(raw, dict) or not isinstance(raw.get("id"), str) or not raw["id"]:
            raise AnalysisError("each node requires a non-empty id")
        identifier = raw["id"]
        if identifier in nodes:
            raise AnalysisError(f"duplicate node identifier: {identifier}")
        if set(raw) - {"id", "kind", "labels", "inputs"}:
            raise AnalysisError(f"unknown field in node {identifier}")
        kind = raw.get("kind", "transform")
        if kind not in ("source", "transform", "sink"):
            raise AnalysisError(f"invalid kind for node {identifier}")
        nodes[identifier] = Node(
            identifier,
            kind,
            _strings(raw.get("labels", []), f"labels for {identifier}"),
            _strings(raw.get("inputs", []), f"inputs for {identifier}"),
        )
    for node in nodes.values():
        for parent in node.inputs:
            if parent not in nodes:
                raise AnalysisError(f"node {node.identifier} references undefined node {parent}")
    if not isinstance(policy, dict) or set(policy) - {"forbidden", "exceptions"}:
        raise AnalysisError("policy must be an object with forbidden and exceptions fields")
    forbidden = _strings(policy.get("forbidden", []), "policy forbidden")
    exceptions = policy.get("exceptions", {})
    if not isinstance(exceptions, dict):
        raise AnalysisError("policy exceptions must map sink ids to string lists")
    for sink, allowed in exceptions.items():
        if not isinstance(sink, str) or sink not in nodes or nodes[sink].kind != "sink":
            raise AnalysisError(f"exception references undefined sink {sink}")
        _strings(allowed, f"exception for {sink}")
    blocked = {
        (label, sink)
        for label in forbidden
        for sink, node in nodes.items()
        if node.kind == "sink" and label not in exceptions.get(sink, [])
    }
    return nodes, blocked


def analyze(manifest: Any, policy: Any) -> dict[str, Any]:
    nodes, blocked = _parse(manifest, policy)
    indegree = {key: len(node.inputs) for key, node in nodes.items()}
    children: dict[str, list[str]] = {key: [] for key in nodes}
    for node in nodes.values():
        for parent in node.inputs:
            children[parent].append(node.identifier)
    ready = [key for key, degree in indegree.items() if degree == 0]
    heapq.heapify(ready)
    order: list[str] = []
    while ready:
        current = heapq.heappop(ready)
        order.append(current)
        for child in sorted(children[current]):
            indegree[child] -= 1
            if indegree[child] == 0:
                heapq.heappush(ready, child)
    if len(order) != len(nodes):
        raise AnalysisError("graph contains a cycle")

    taint: dict[str, set[str]] = {key: set() for key in nodes}
    paths: dict[str, set[tuple[str, str, tuple[str, ...]]]] = {key: set() for key in nodes}
    for identifier in order:
        node = nodes[identifier]
        for label in node.labels if node.kind == "source" else ():
            taint[identifier].add(label)
            paths[identifier].add((identifier, label, (identifier,)))
        for parent in sorted(node.inputs):
            for source, label, path in sorted(paths[parent]):
                taint[identifier].add(label)
                paths[identifier].add((source, label, path + (identifier,)))

    violations: list[dict[str, Any]] = []
    for sink in sorted(nodes):
        if nodes[sink].kind != "sink":
            continue
        for source, label, path in sorted(paths[sink]):
            if (label, sink) in blocked:
                violations.append({"sink": sink, "source": source, "label": label, "path": list(path)})
    return {
        "nodes": [{"id": key, "taint": sorted(taint[key])} for key in sorted(nodes)],
        "violations": violations,
    }
