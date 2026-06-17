"""Framework adapters — wrap external eval libraries behind the Metric protocol.

Each adapter loads its backend lazily, so the dependency is optional (install
the matching extra). The backend call is isolated behind an injectable hook, so
the harness-side mapping/normalization is unit-tested without the heavy lib.

- ``RagasMetric``    — Ragas single-turn metrics (async).
- ``DeepEvalMetric`` — DeepEval LLM metrics (sync ``measure``).
- ``PromptfooMetric``— ingests a Promptfoo results file (Promptfoo is a Node CLI
  suite-runner, not a per-record Python scorer).
"""

from .deepeval import DeepEvalMetric
from .promptfoo import PromptfooMetric, load_promptfoo_results
from .ragas import RagasMetric

__all__ = [
    "RagasMetric",
    "DeepEvalMetric",
    "PromptfooMetric",
    "load_promptfoo_results",
]
