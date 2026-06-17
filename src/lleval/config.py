"""Eval configuration loaded from YAML."""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel


class Config(BaseModel):
    """An eval suite definition."""

    dataset: str
    baseline: str
    metrics: list[str]
    threshold: float = 0.05
    judge: str = "heuristic"


def load_config(path: str | Path) -> Config:
    """Load and validate an eval.yaml file."""
    data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    return Config.model_validate(data)
