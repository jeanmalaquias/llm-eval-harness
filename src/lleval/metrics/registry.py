"""Metric registry — resolves metric names from config to instances."""

from __future__ import annotations

from ..judge import Judge
from .base import Metric
from .builtins import ExactMatch, Groundedness, KeywordCoverage, LLMJudge

# Reference-free / judge-free metrics that instantiate with no args.
_SIMPLE: dict[str, type] = {
    ExactMatch.name: ExactMatch,
    KeywordCoverage.name: KeywordCoverage,
    Groundedness.name: Groundedness,
}

# Framework adapters selectable by a short name (defaults applied).
_FRAMEWORKS: frozenset[str] = frozenset({"ragas", "deepeval", "promptfoo"})

METRIC_NAMES: list[str] = sorted([*_SIMPLE, LLMJudge.name, *_FRAMEWORKS])


def build_metrics(
    names: list[str],
    judge: Judge,
    promptfoo_results: dict[str, float] | None = None,
) -> list[Metric]:
    """Instantiate the named metrics.

    ``llm_judge`` gets the judge; ``promptfoo`` gets pre-loaded results;
    ``ragas`` / ``deepeval`` use their default sub-metric.
    """
    # Lazy import to avoid a frameworks <-> metrics import cycle.
    from ..frameworks import DeepEvalMetric, PromptfooMetric, RagasMetric

    metrics: list[Metric] = []
    for name in names:
        if name == LLMJudge.name:
            metrics.append(LLMJudge(judge))
        elif name in _SIMPLE:
            metrics.append(_SIMPLE[name]())
        elif name == "ragas":
            metrics.append(RagasMetric())
        elif name == "deepeval":
            metrics.append(DeepEvalMetric())
        elif name == "promptfoo":
            metrics.append(PromptfooMetric(results=promptfoo_results))
        else:
            known = ", ".join(METRIC_NAMES)
            raise ValueError(f"Unknown metric '{name}'. Known: {known}")
    return metrics
