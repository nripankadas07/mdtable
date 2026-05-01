"""Happy-path tests for the renderer."""

from __future__ import annotations

from mdtable import render


def test_render_minimal_table() -> None:
    out = render(["A", "B"], [["1", "2"]])
    assert (
        out
        == "| A   | B   |\n"
        "| --- | --- |\n"
        "| 1   | 2   |"
    )


def test_render_default_alignment_uses_dashes() -> None:
    out = render(["x"], [["1"]])
    # default alignment â no leading or trailing colon on the separator.
    assert out.splitlines()[1] == "| --- |"
