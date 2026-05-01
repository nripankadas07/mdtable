"""Tests for alignment specification handling."""

from __future__ import annotations

import pytest

from mdtable import AlignmentError, normalize_alignment, render


def _separator(out: str) -> str:
    return out.splitlines()[1]


def test_alignment_left_writes_leading_colon() -> None:
    out = render(["a"], [["x"]], align="left")
    assert _separator(out).strip().startswith("| :")
