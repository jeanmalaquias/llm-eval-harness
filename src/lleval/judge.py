"""LLM-as-Judge backends.

The judge rates an output against its reference and returns a score plus a
reasoning trace (kept for audit). ``HeuristicJudge`` is deterministic and
offline so CI is hermetic; a real judge (Claude or any provider) implements the
same ``Judge`` protocol and is selected by config.
"""

from __future__ import annotations

import re
from typing import Protocol, runtime_checkable

from pydantic import BaseModel

from .dataset import Prediction

_WORD = re.compile(r"[a-z0-9]+")


def _tokens(text: str) -> set[str]:
    return set(_WORD.findall(text.lower()))


class Judgement(BaseModel):
    """A judge's score with the reasoning behind it."""

    value: float
    trace: str


@runtime_checkable
class Judge(Protocol):
    """Rates an output against its reference."""

    name: str

    async def judge(self, record: Prediction) -> Judgement:
        ...


class HeuristicJudge:
    """Deterministic judge: token overlap (F1) between output and reference."""

    name = "heuristic"

    async def judge(self, record: Prediction) -> Judgement:
        ref = _tokens(record.reference or "")
        out = _tokens(record.output)
        if not ref:
            return Judgement(value=1.0, trace="No reference; treated as pass.")
        if not out:
            return Judgement(value=0.0, trace="Empty output.")
        overlap = ref & out
        precision = len(overlap) / len(out)
        recall = len(overlap) / len(ref)
        f1 = 0.0 if precision + recall == 0 else 2 * precision * recall / (
            precision + recall
        )
        trace = (
            f"Overlap {len(overlap)} tokens; precision={precision:.2f}, "
            f"recall={recall:.2f}, F1={f1:.2f}."
        )
        return Judgement(value=round(f1, 4), trace=trace)


_JUDGES: dict[str, type] = {"heuristic": HeuristicJudge}


def get_judge(name: str) -> Judge:
    """Return a judge backend by name."""
    try:
        return _JUDGES[name]()
    except KeyError:
        known = ", ".join(sorted(_JUDGES))
        raise ValueError(f"Unknown judge '{name}'. Known: {known}") from None
