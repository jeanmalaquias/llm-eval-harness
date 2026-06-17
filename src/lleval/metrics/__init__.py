"""Metrics: plugin-style scorers. Adding a metric is one new file here."""

from .base import Metric, Score
from .registry import METRIC_NAMES, build_metrics

__all__ = ["Metric", "Score", "METRIC_NAMES", "build_metrics"]
