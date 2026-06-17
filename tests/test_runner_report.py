from lleval.dataset import Prediction, load_predictions
from lleval.judge import HeuristicJudge
from lleval.metrics import build_metrics
from lleval.report import to_html, to_json, to_markdown
from lleval.runner import Report, compare_to_baseline, run_eval


def _predictions():
    return [
        Prediction(id="q1", output="vector search", reference="vector search"),
        Prediction(id="q2", output="cats", reference="dogs and birds"),
    ]


async def _report():
    metrics = build_metrics(["keyword_coverage", "llm_judge"], HeuristicJudge())
    return await run_eval(_predictions(), metrics)


async def test_run_eval_aggregates_and_keeps_traces():
    report = await _report()
    assert set(report.aggregate) == {"keyword_coverage", "llm_judge"}
    assert len(report.cases) == 2
    assert report.cases[0].traces["llm_judge"]


async def test_run_eval_empty_dataset():
    metrics = build_metrics(["keyword_coverage"], HeuristicJudge())
    report = await run_eval([], metrics)
    assert report.aggregate["keyword_coverage"] == 0.0


def test_compare_to_baseline():
    report = Report(cases=[], aggregate={"a": 0.80, "b": 0.99, "extra": 0.1})
    baseline = {"a": 0.95, "b": 1.00}
    regressions = compare_to_baseline(report, baseline, threshold=0.05)
    assert {r.metric for r in regressions} == {"a"}
    assert regressions[0].delta < 0


async def test_jsonl_loading_skips_blank_lines(tmp_path):
    f = tmp_path / "p.jsonl"
    f.write_text(
        '{"id":"q1","output":"a","reference":"a"}\n\n'
        '{"id":"q2","output":"b","reference":"b"}\n',
        encoding="utf-8",
    )
    assert len(load_predictions(f)) == 2


async def test_report_renderers():
    report = await _report()
    md = to_markdown(report)
    assert "keyword_coverage" in md
    # With regressions appended.
    from lleval.runner import Regression

    md2 = to_markdown(report, [Regression(metric="x", baseline=1.0, current=0.5)])
    assert "REGRESSIONS" in md2

    assert '"aggregate"' in to_json(report)

    html = to_html(report, {"keyword_coverage": 0.9})
    assert "<table" in html
    assert "keyword_coverage" in html
