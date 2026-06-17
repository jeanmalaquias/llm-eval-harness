"""Built-in, offline-deterministic metrics."""

from __future__ import annotations

from ..dataset import Prediction
from ..judge import Judge
from .base import Score, tokens


class ExactMatch:
    """1.0 if the normalized output equals the normalized reference."""

    name = "exact_match"
    requires = ("reference",)

    async def score(self, record: Prediction) -> Score:
        ref = (record.reference or "").strip().lower()
        out = record.output.strip().lower()
        return Score(value=1.0 if ref and out == ref else 0.0)


class KeywordCoverage:
    """Fraction of the reference's content keywords present in the output."""

    name = "keyword_coverage"
    requires = ("reference",)

    async def score(self, record: Prediction) -> Score:
        ref = set(tokens(record.reference or ""))
        if not ref:
            return Score(value=1.0, trace="No reference keywords.")
        out = set(tokens(record.output))
        hits = ref & out
        return Score(
            value=len(hits) / len(ref),
            trace=f"{len(hits)}/{len(ref)} reference keywords present.",
        )


class Groundedness:
    """Fraction of the output's content tokens supported by the contexts."""

    name = "groundedness"
    requires = ("contexts",)

    async def score(self, record: Prediction) -> Score:
        out = tokens(record.output)
        if not out:
            return Score(value=1.0, trace="Empty output.")
        supported = set()
        for ctx in record.contexts:
            supported |= set(tokens(ctx))
        grounded = sum(1 for t in out if t in supported)
        return Score(
            value=grounded / len(out),
            trace=f"{grounded}/{len(out)} output tokens found in contexts.",
        )


class LLMJudge:
    """LLM-as-Judge: delegates to a judge backend and keeps its trace."""

    name = "llm_judge"
    requires = ("reference",)

    def __init__(self, judge: Judge) -> None:
        self._judge = judge

    async def score(self, record: Prediction) -> Score:
        judgement = await self._judge.judge(record)
        return Score(value=judgement.value, trace=judgement.trace)
