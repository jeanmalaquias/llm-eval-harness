"""DeepEval adapter.

Maps a ``Prediction`` to a DeepEval ``LLMTestCase`` and scores it with a
DeepEval metric (sync ``measure``). Install with ``pip install lleval[deepeval]``.
The DeepEval call is isolated in ``_deepeval_score`` (lazy import), injectable.
"""

from __future__ import annotations

from collections.abc import Callable

from ..dataset import Prediction
from ..metrics.base import Score

# scorer(record, metric_name) -> float
Scorer = Callable[[Prediction, str], float]


# pragma: no cover reason — needs the deepeval package and a live LLM.
def _deepeval_score(record: Prediction, metric_name: str) -> float:  # pragma: no cover
    from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
    from deepeval.test_case import LLMTestCase

    test_case = LLMTestCase(
        input=record.input,
        actual_output=record.output,
        expected_output=record.reference,
        retrieval_context=record.contexts or None,
    )
    metric = {
        "answer_relevancy": AnswerRelevancyMetric,
        "faithfulness": FaithfulnessMetric,
    }[metric_name]()
    metric.measure(test_case)
    return float(metric.score)


class DeepEvalMetric:
    """Adapter over a DeepEval LLM metric."""

    requires = ("reference",)

    def __init__(
        self, metric: str = "answer_relevancy", scorer: Scorer | None = None
    ) -> None:
        self.metric = metric
        self.name = f"deepeval:{metric}"
        self._scorer = scorer or _deepeval_score

    async def score(self, record: Prediction) -> Score:
        value = self._scorer(record, self.metric)
        return Score(value=float(value), trace=self.name)
