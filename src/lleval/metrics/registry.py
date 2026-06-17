"""Metric registry — resolves metric names from config to instances."""

from __future__ import annotations

from ..judge import Judge
from .base import Metric
from .builtins import ExactMatch, Groundedness, KeywordCoverage, LLMJudge

# Reference-free metrics instantiate with no args; llm_judge needs a judge.
_SIMPLE: dict[str, type] = {
    ExactMatch.name: ExactMatch,
    KeywordCoverage.name: KeywordCoverage,
    Groundedness.name: Groundedness,
}

METRIC_NAMES: list[str] = sorted([*_SIMPLE, LLMJudge.name])


def build_metrics(names: list[str], judge: Judge) -> list[Metric]:
    """Instantiate the named metrics, injecting the judge into ``llm_judge``."""
    metrics: list[Metric] = []
    for name in names:
        if name == LLMJudge.name:
            metrics.append(LLMJudge(judge))
        elif name in _SIMPLE:
            metrics.append(_SIMPLE[name]())
        else:
            known = ", ".join(METRIC_NAMES)
            raise ValueError(f"Unknown metric '{name}'. Known: {known}")
    return metrics
