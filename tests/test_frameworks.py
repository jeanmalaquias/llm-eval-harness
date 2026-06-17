import json

from lleval.dataset import Prediction
from lleval.frameworks import (
    DeepEvalMetric,
    PromptfooMetric,
    RagasMetric,
    load_promptfoo_results,
)
from lleval.judge import HeuristicJudge
from lleval.metrics import build_metrics


async def test_ragas_adapter_uses_injected_async_scorer():
    seen = {}

    async def fake(record, metric_name):
        seen["metric"] = metric_name
        return 0.77

    m = RagasMetric(scorer=fake)
    score = await m.score(Prediction(id="a", output="o", reference="r"))
    assert m.name == "ragas:answer_relevancy"
    assert score.value == 0.77
    assert seen["metric"] == "answer_relevancy"


async def test_deepeval_adapter_uses_injected_sync_scorer():
    m = DeepEvalMetric(metric="faithfulness", scorer=lambda rec, name: 0.5)
    score = await m.score(Prediction(id="a", output="o", reference="r"))
    assert m.name == "deepeval:faithfulness"
    assert score.value == 0.5


async def test_promptfoo_metric_hit_and_miss():
    m = PromptfooMetric(results={"q1": 0.9})
    hit = await m.score(Prediction(id="q1", output="o"))
    miss = await m.score(Prediction(id="q2", output="o"))
    assert hit.value == 0.9 and hit.trace == "promptfoo"
    assert miss.value == 0.0 and "no promptfoo result" in miss.trace


def test_load_promptfoo_results(tmp_path):
    f = tmp_path / "results.json"
    f.write_text(
        json.dumps(
            {
                "results": {
                    "results": [
                        {"vars": {"id": "q1"}, "score": 0.8},
                        {"vars": {"id": "q2"}, "success": True},
                        {"vars": {"id": "q3"}, "success": False},
                        {"vars": {}, "success": True},  # no id → skipped
                    ]
                }
            }
        ),
        encoding="utf-8",
    )
    results = load_promptfoo_results(f)
    assert results == {"q1": 0.8, "q2": 1.0, "q3": 0.0}


def test_build_metrics_supports_frameworks():
    metrics = build_metrics(
        ["ragas", "deepeval", "promptfoo"],
        HeuristicJudge(),
        promptfoo_results={"q1": 1.0},
    )
    names = [m.name for m in metrics]
    assert names == ["ragas:answer_relevancy", "deepeval:answer_relevancy", "promptfoo"]
