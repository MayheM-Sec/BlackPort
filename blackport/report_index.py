"""
MayheM-Sec Added

Local report indexing helpers for the BlackPort GUI.

The index reads only files in the configured local reports directory and
returns compact summaries suitable for the dashboard.
"""

from __future__ import annotations

import json
from pathlib import Path


def _risk_counts(results: list[dict]) -> dict[str, int]:
    counts = {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0}
    for item in results:
        risk = str(item.get("risk", "")).upper()
        if risk in counts:
            counts[risk] += 1
        mayhem = item.get("mayhem_sec") or {}
        mayhem_risk = (mayhem.get("risk") or {}).get("severity")
        if mayhem_risk and mayhem_risk in counts and risk not in counts:
            counts[mayhem_risk] += 1
    return counts


def summarize_report(path: Path) -> dict | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

    stat = path.stat()
    summary = {
        "name": path.name,
        "path": str(path),
        "modified": stat.st_mtime,
        "protocol": "tcp",
        "target": None,
        "findings": 0,
        "open": 0,
        "open_filtered": 0,
        "risk": {"CRITICAL": 0, "HIGH": 0, "MEDIUM": 0, "LOW": 0},
        "enriched": path.name.endswith(".mayhem.json"),
    }

    if isinstance(payload, dict) and payload.get("protocol") == "udp":
        results = payload.get("results") or []
        summary["protocol"] = "udp"
        summary["target"] = payload.get("target")
        summary["findings"] = len(results)
        summary["open"] = sum(1 for r in results if r.get("state") == "open")
        summary["open_filtered"] = sum(1 for r in results if r.get("state") == "open|filtered")
        return summary

    if isinstance(payload, list):
        summary["findings"] = len(payload)
        summary["open"] = len(payload)
        summary["risk"] = _risk_counts([r for r in payload if isinstance(r, dict)])
        if payload:
            summary["target"] = payload[0].get("target") if isinstance(payload[0], dict) else None
        return summary

    return None


def list_reports(report_dir: Path, limit: int = 50) -> list[dict]:
    if not report_dir.exists():
        return []
    items = []
    for path in report_dir.glob("*.json"):
        summary = summarize_report(path)
        if summary:
            items.append(summary)
    items.sort(key=lambda item: item["modified"], reverse=True)
    return items[: max(1, min(limit, 200))]


def load_report(report_dir: Path, name: str) -> dict | list:
    """MayheM-Sec Added: safely load one report by basename only."""
    candidate = (report_dir / Path(name).name).resolve()
    base = report_dir.resolve()
    if candidate.parent != base or not candidate.exists() or candidate.suffix.lower() != ".json":
        raise FileNotFoundError("Report not found")
    return json.loads(candidate.read_text(encoding="utf-8"))
