"""Render eval results as Markdown, JSON, and a standalone HTML diff report."""

from __future__ import annotations

import json

from jinja2 import Template

from .runner import Regression, Report

_HTML = Template(
    """<!doctype html>
<html lang="en"><head><meta charset="utf-8"><title>lleval report</title>
<style>
 body{font-family:system-ui,sans-serif;margin:2rem;color:#1a1a1a}
 table{border-collapse:collapse;margin:1rem 0}
 th,td{border:1px solid #ddd;padding:.4rem .8rem;text-align:left}
 th{background:#f4f4f4}
 .down{color:#b00020;font-weight:600}.up{color:#0a7d28}
</style></head><body>
<h1>LLM Eval Report</h1>
<h2>Aggregate</h2>
<table><tr><th>Metric</th><th>Score</th><th>Baseline</th><th>Δ</th></tr>
{% for m, score in report.aggregate.items() %}
 <tr><td>{{ m }}</td><td>{{ '%.3f'|format(score) }}</td>
 <td>{{ '%.3f'|format(baseline[m]) if m in baseline else '—' }}</td>
 <td class="{{ 'down' if m in baseline and score < baseline[m] else 'up' }}">
 {{ '%+.3f'|format(score - baseline[m]) if m in baseline else '—' }}</td></tr>
{% endfor %}
</table>
<h2>Per-case scores</h2>
<table><tr><th>id</th>{% for m in metrics %}<th>{{ m }}</th>{% endfor %}</tr>
{% for c in report.cases %}
 <tr><td>{{ c.id }}</td>
 {% for m in metrics %}<td>{{ '%.3f'|format(c.scores[m]) }}</td>{% endfor %}</tr>
{% endfor %}
</table>
</body></html>"""
)


def to_markdown(report: Report, regressions: list[Regression] | None = None) -> str:
    lines = ["| metric | score |", "| --- | --- |"]
    for metric, score in report.aggregate.items():
        lines.append(f"| {metric} | {score:.3f} |")
    if regressions:
        lines.append("\nREGRESSIONS:")
        for r in regressions:
            lines.append(
                f"  {r.metric}: {r.baseline:.3f} -> {r.current:.3f} ({r.delta:+.3f})"
            )
    return "\n".join(lines)


def to_json(report: Report) -> str:
    return json.dumps(report.model_dump(), indent=2)


def to_html(report: Report, baseline: dict[str, float]) -> str:
    metrics = list(report.aggregate.keys())
    return _HTML.render(report=report, baseline=baseline, metrics=metrics)
