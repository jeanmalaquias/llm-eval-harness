"""Prediction records and JSONL loading.

A prediction is the unit of evaluation: the model's output for one input, plus
optional retrieved contexts and a gold reference. Datasets are JSONL so they
append cleanly and diff well in version control.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, Field


class Prediction(BaseModel):
    """One recorded model output to be scored."""

    id: str
    input: str = ""
    output: str
    contexts: list[str] = Field(default_factory=list)
    reference: str | None = None


def load_predictions(path: str | Path) -> list[Prediction]:
    """Load predictions from a JSONL file (one record per non-blank line)."""
    lines = Path(path).read_text(encoding="utf-8").splitlines()
    return [
        Prediction.model_validate_json(line) for line in lines if line.strip()
    ]
