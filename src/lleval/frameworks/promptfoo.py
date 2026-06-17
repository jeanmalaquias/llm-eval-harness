"""Promptfoo adapter.

Promptfoo is a Node CLI that runs its own assertion suite and writes a results
file (``promptfoo eval -o results.json``). Rather than pretend it is a per-record
Python scorer, this adapter *ingests* those results: it maps each prediction's
``id`` to Promptfoo's per-case score. Wire it by running Promptfoo your way,
then loading the output with ``load_promptfoo_results``.
"""

from __future__ import annotations

import json
from pathlib import Path

from ..dataset import Prediction
from ..metrics.base import Score


def load_promptfoo_results(path: str | Path, id_var: str = "id") -> dict[str, float]:
    """Parse a Promptfoo JSON output file into ``{record_id: score}``.

    Promptfoo writes ``{"results": {"results": [{"vars": {...}, "success": bool,
    "score": float}, ...]}}``. We key by the ``id_var`` variable and fall back to
    1.0/0.0 from ``success`` when a numeric ``score`` is absent.
    """
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = data.get("results", {}).get("results", [])
    scores: dict[str, float] = {}
    for row in rows:
        key = str(row.get("vars", {}).get(id_var, ""))
        if not key:
            continue
        if "score" in row:
            scores[key] = float(row["score"])
        else:
            scores[key] = 1.0 if row.get("success") else 0.0
    return scores


class PromptfooMetric:
    """Adapter that scores from pre-computed Promptfoo results."""

    name = "promptfoo"
    requires = ()

    def __init__(self, results: dict[str, float] | None = None) -> None:
        self._results = results or {}

    async def score(self, record: Prediction) -> Score:
        value = self._results.get(record.id, 0.0)
        found = record.id in self._results
        return Score(
            value=float(value),
            trace="promptfoo" if found else f"no promptfoo result for '{record.id}'",
        )
