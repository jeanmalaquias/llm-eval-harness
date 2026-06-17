"""Eval runner, report model, and baseline comparison."""

from __future__ import annotations

from statistics import mean

from pydantic import BaseModel

from .dataset import Prediction
from .metrics import Metric


class CaseResult(BaseModel):
    """Per-record metric scores and their reasoning traces."""

    id: str
    scores: dict[str, float]
    traces: dict[str, str]


class Report(BaseModel):
    """The full result of an eval run."""

    cases: list[CaseResult]
    aggregate: dict[str, float]


class Regression(BaseModel):
    """A metric whose aggregate dropped beyond the threshold vs baseline."""

    metric: str
    baseline: float
    current: float

    @property
    def delta(self) -> float:
        return self.current - self.baseline


async def run_eval(
    predictions: list[Prediction], metrics: list[Metric]
) -> Report:
    """Score every prediction with every metric and aggregate per metric."""
    cases: list[CaseResult] = []
    for record in predictions:
        scores: dict[str, float] = {}
        traces: dict[str, str] = {}
        for metric in metrics:
            result = await metric.score(record)
            scores[metric.name] = result.value
            traces[metric.name] = result.trace
        cases.append(CaseResult(id=record.id, scores=scores, traces=traces))

    aggregate = {
        metric.name: (
            mean(c.scores[metric.name] for c in cases) if cases else 0.0
        )
        for metric in metrics
    }
    return Report(cases=cases, aggregate=aggregate)


def compare_to_baseline(
    report: Report, baseline: dict[str, float], threshold: float
) -> list[Regression]:
    """Return metrics that regressed by more than ``threshold`` vs baseline."""
    regressions: list[Regression] = []
    for metric, current in report.aggregate.items():
        if metric in baseline and current < baseline[metric] - threshold:
            regressions.append(
                Regression(metric=metric, baseline=baseline[metric], current=current)
            )
    return regressions
