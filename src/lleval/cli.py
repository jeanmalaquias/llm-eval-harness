"""lleval CLI and CI gate: ``lleval run --config eval.yaml``.

Scores recorded predictions, diffs against the baseline, writes reports, and
exits non-zero on regression. ``--update-baseline`` records the current
aggregate as the new baseline.
"""

from __future__ import annotations

import argparse
import asyncio
import json
from datetime import UTC, datetime
from pathlib import Path

from .config import load_config
from .dataset import load_predictions
from .frameworks import load_promptfoo_results
from .judge import get_judge
from .metrics import build_metrics
from .report import to_html, to_markdown
from .runner import compare_to_baseline, run_eval


async def _run(args: argparse.Namespace) -> int:
    config = load_config(args.config)
    predictions = load_predictions(config.dataset)
    promptfoo = (
        load_promptfoo_results(config.promptfoo_results)
        if config.promptfoo_results
        else None
    )
    metrics = build_metrics(config.metrics, get_judge(config.judge), promptfoo)
    report = await run_eval(predictions, metrics)

    if args.history:
        entry = {
            "timestamp": datetime.now(UTC).isoformat(),
            "aggregate": report.aggregate,
        }
        with Path(args.history).open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry) + "\n")

    if args.update_baseline:
        Path(config.baseline).write_text(
            json.dumps(report.aggregate, indent=2), encoding="utf-8"
        )
        print(to_markdown(report))
        print(f"\nBaseline updated: {config.baseline}")
        return 0

    baseline = json.loads(Path(config.baseline).read_text(encoding="utf-8"))
    regressions = compare_to_baseline(report, baseline, config.threshold)

    if args.html:
        Path(args.html).write_text(to_html(report, baseline), encoding="utf-8")

    print(to_markdown(report, regressions))
    if regressions:
        return 1
    print("\nNo regressions. Gate passed.")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="lleval")
    sub = parser.add_subparsers(dest="command", required=True)
    run_p = sub.add_parser("run", help="Run the eval suite and gate on regression.")
    run_p.add_argument("--config", required=True)
    run_p.add_argument("--html", help="Optional path to write an HTML report.")
    run_p.add_argument(
        "--history",
        help="Append this run's aggregate to a JSONL history (for the dashboard).",
    )
    run_p.add_argument("--update-baseline", action="store_true")
    args = parser.parse_args(argv)
    return asyncio.run(_run(args))


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
