"""Metric protocol and shared helpers."""

from __future__ import annotations

import re
from typing import Protocol, runtime_checkable

from pydantic import BaseModel

from ..dataset import Prediction

_WORD = re.compile(r"[a-z0-9]+")
_STOPWORDS = frozenset(
    {"the", "a", "an", "of", "to", "for", "and", "or", "is", "are", "in", "on"}
)


def tokens(text: str) -> list[str]:
    """Lowercase content tokens (stopwords removed)."""
    return [w for w in _WORD.findall(text.lower()) if w not in _STOPWORDS]


class Score(BaseModel):
    """A metric's score for one record, with an optional reasoning trace."""

    value: float
    trace: str = ""


@runtime_checkable
class Metric(Protocol):
    """Scores one prediction in [0, 1]."""

    name: str
    requires: tuple[str, ...]

    async def score(self, record: Prediction) -> Score:
        ...
