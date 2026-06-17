"""Ragas adapter.

Maps a ``Prediction`` to a Ragas ``SingleTurnSample`` and scores it with a
Ragas single-turn metric. Install with ``pip install lleval[ragas]``. The Ragas
call is isolated in ``_score`` (lazy import) and injectable for tests.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from ..dataset import Prediction
from ..metrics.base import Score

# scorer(record, metric_name) -> awaitable float
Scorer = Callable[[Prediction, str], Awaitable[float]]


# pragma: no cover reason — needs the ragas package and a live LLM/embeddings.
async def _score(record: Prediction, metric_name: str) -> float:  # pragma: no cover
    from ragas import metrics as rm
    from ragas.dataset_schema import SingleTurnSample

    sample = SingleTurnSample(
        user_input=record.input,
        response=record.output,
        reference=record.reference,
        retrieved_contexts=record.contexts or None,
    )
    factory = {
        "answer_relevancy": rm.ResponseRelevancy,
        "faithfulness": rm.Faithfulness,
        "context_precision": rm.LLMContextPrecisionWithReference,
    }[metric_name]
    return float(await factory().single_turn_ascore(sample))


class RagasMetric:
    """Adapter over a Ragas single-turn metric."""

    requires = ("reference",)

    def __init__(
        self, metric: str = "answer_relevancy", scorer: Scorer | None = None
    ) -> None:
        self.metric = metric
        self.name = f"ragas:{metric}"
        self._scorer = scorer or _score

    async def score(self, record: Prediction) -> Score:
        value = await self._scorer(record, self.metric)
        return Score(value=float(value), trace=self.name)
