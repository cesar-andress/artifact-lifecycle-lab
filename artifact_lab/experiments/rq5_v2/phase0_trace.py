"""Trace parsing and behavioral metrics for RQ5 v2 factorial runs."""

from __future__ import annotations

import json
from pathlib import Path

from artifact_lab.experiments.rq5_v2.models import FactorialCase
from artifact_lab.experiments.truth_decay.rq5_experiment.agents.cli_utils import (
    instruction_was_read,
    parse_claude_stream_json,
    reference_followed,
    shell_commands_from_events,
)
from artifact_lab.experiments.truth_decay.rq5_experiment.models import TraceEvent


def parse_trace_events(trace_path: Path, *, stdout_fallback: str = "") -> tuple[list[TraceEvent], dict]:
    """Load trace events from JSONL file or Claude stream-json stdout."""
    events: list[TraceEvent] = []
    meta: dict = {
        "iterations": 0,
        "tool_invocations": 0,
        "token_usage": None,
        "cost_usd": None,
        "tool_failures": 0,
    }

    raw = stdout_fallback
    if trace_path.exists() and trace_path.stat().st_size > 0:
        raw = trace_path.read_text(encoding="utf-8", errors="replace")

    if not raw.strip():
        return events, meta

    if raw.lstrip().startswith("{"):
        parsed, parsed_meta = parse_claude_stream_json(raw)
        events.extend(parsed)
        meta.update({k: parsed_meta.get(k, meta[k]) for k in meta})
        return events, meta

    for line in raw.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        if "event_type" in obj:
            events.append(
                TraceEvent(
                    timestamp=str(obj.get("timestamp", "")),
                    event_type=str(obj.get("event_type", "")),
                    payload=dict(obj.get("payload") or {}),
                )
            )
    return events, meta


def anchor_attempted(events: list[TraceEvent], cited_anchor: str) -> bool:
    """M1: tool event targets the cited path or derived command."""
    if reference_followed(events, cited_anchor):
        return True
    ref_base = cited_anchor.rstrip("/").split("/")[-1]
    for event in events:
        blob = json.dumps(event.payload)
        if cited_anchor in blob or ref_base in blob:
            return True
    return False


def enrich_result_from_trace(
    *,
    case: FactorialCase,
    cell_code: str,
    result_row: dict,
    trace_path: Path,
) -> dict:
    """Add trace-derived fields to a result row."""
    cell = case.get_cell(cell_code)
    events, meta = parse_trace_events(trace_path)
    row = dict(result_row)
    row["instruction_read"] = instruction_was_read(events, case.instruction_path) or bool(
        row.get("read_instruction")
    )
    row["read_instruction"] = row["instruction_read"]
    row["anchor_attempted"] = anchor_attempted(events, cell.cited_anchor) or bool(
        row.get("anchor_path_touched")
    )
    row["commands_executed"] = shell_commands_from_events(events) or int(row.get("commands_executed") or 0)
    row["iterations"] = int(meta.get("iterations") or row.get("iterations") or 0)
    row["tool_failures"] = int(meta.get("tool_failures") or row.get("tool_failures") or 0)
    if meta.get("cost_usd") is not None:
        row["cost_usd"] = meta["cost_usd"]
    if meta.get("token_usage") is not None:
        row["token_usage"] = meta["token_usage"]
    row["timed_out"] = "timeout" in str(row.get("error_message", "")).lower()
    return row
