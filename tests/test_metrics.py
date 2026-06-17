import pytest

from lleval.dataset import Prediction
from lleval.judge import HeuristicJudge, get_judge
from lleval.metrics import build_metrics
from lleval.metrics.builtins import (
    ExactMatch,
    Groundedness,
    KeywordCoverage,
    LLMJudge,
)


async def _val(metric, **kwargs):
    return (await metric.score(Prediction(**kwargs))).value


async def test_exact_match():
    m = ExactMatch()
    assert await _val(m, id="a", output="Hi", reference="hi") == 1.0
    assert await _val(m, id="b", output="Hi", reference="bye") == 0.0
    # No reference → 0.0 (nothing to match).
    assert await _val(m, id="c", output="Hi") == 0.0


async def test_keyword_coverage():
    m = KeywordCoverage()
    full = await _val(m, id="a", output="vector search db", reference="vector search")
    assert full == 1.0
    half = await _val(m, id="b", output="vector x", reference="vector search")
    assert half == 0.5
    # No reference keywords (all stopwords) → vacuously complete.
    assert await _val(m, id="c", output="x", reference="the") == 1.0


async def test_groundedness():
    m = Groundedness()
    rec = Prediction(id="a", output="vector search", contexts=["vector search rocks"])
    assert (await m.score(rec)).value == 1.0
    # Empty output → vacuously grounded.
    assert (await m.score(Prediction(id="b", output=""))).value == 1.0


async def test_llm_judge_metric_uses_judge():
    m = LLMJudge(HeuristicJudge())
    score = await m.score(
        Prediction(id="a", output="vector search", reference="vector search")
    )
    assert score.value == 1.0
    assert "F1" in score.trace


async def test_build_metrics_and_unknown():
    metrics = build_metrics(
        ["exact_match", "keyword_coverage", "groundedness", "llm_judge"],
        HeuristicJudge(),
    )
    assert [m.name for m in metrics] == [
        "exact_match",
        "keyword_coverage",
        "groundedness",
        "llm_judge",
    ]
    with pytest.raises(ValueError, match="Unknown metric"):
        build_metrics(["nope"], HeuristicJudge())


async def test_heuristic_judge_edges():
    judge = HeuristicJudge()
    assert (await judge.judge(Prediction(id="a", output="x"))).value == 1.0  # no ref
    empty = await judge.judge(Prediction(id="b", output="", reference="vector"))
    assert empty.value == 0.0


def test_get_judge_unknown():
    with pytest.raises(ValueError, match="Unknown judge"):
        get_judge("nope")
