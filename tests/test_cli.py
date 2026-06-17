import json

import yaml

from lleval import cli
from lleval.config import load_config

_EXAMPLE = "examples/rag-app/eval.yaml"


def _write_config(tmp_path, baseline_path, **overrides):
    cfg = {
        "dataset": "examples/rag-app/predictions.jsonl",
        "baseline": str(baseline_path),
        "metrics": ["keyword_coverage", "llm_judge"],
        "threshold": 0.05,
        "judge": "heuristic",
        **overrides,
    }
    path = tmp_path / "eval.yaml"
    path.write_text(yaml.safe_dump(cfg), encoding="utf-8")
    return path


def test_load_config_roundtrip():
    config = load_config(_EXAMPLE)
    assert config.dataset.endswith("predictions.jsonl")
    assert "llm_judge" in config.metrics


def test_cli_gate_passes_on_bundled_baseline():
    # Runs from the repo root (pytest rootdir); example paths resolve.
    assert cli.main(["run", "--config", _EXAMPLE]) == 0


def test_cli_update_baseline_then_pass(tmp_path):
    baseline = tmp_path / "baseline.json"
    config = _write_config(tmp_path, baseline)
    assert cli.main(["run", "--config", str(config), "--update-baseline"]) == 0
    assert "llm_judge" in json.loads(baseline.read_text())
    # A second run against the just-written baseline passes.
    assert cli.main(["run", "--config", str(config)]) == 0


def test_cli_gate_fails_on_regression(tmp_path):
    baseline = tmp_path / "baseline.json"
    baseline.write_text(json.dumps({"keyword_coverage": 1.0, "llm_judge": 1.0}))
    config = _write_config(tmp_path, baseline)
    assert cli.main(["run", "--config", str(config)]) == 1


def test_cli_writes_html(tmp_path):
    baseline = tmp_path / "baseline.json"
    cli.main(["run", "--config", str(_write_config(tmp_path, baseline)),
              "--update-baseline"])
    html = tmp_path / "report.html"
    code = cli.main(
        ["run", "--config", str(_write_config(tmp_path, baseline)),
         "--html", str(html)]
    )
    assert code == 0
    assert html.exists()
    assert "<table" in html.read_text()
