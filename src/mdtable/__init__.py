"""mdtable — render GFM Markdown tables from headers + rows."""
from __future__ import annotations
from typing import Iterable, List, Sequence, Union

__all__ = ["render", "AlignmentError", "normalize_alignment"]
__version__ = "0.1.0"


class AlignmentError(ValueError):
    """Raised for invalid alignment specifiers."""


_ALIGN_MAP = {
    "l": "left", "left": "left",
    "c": "center", "center": "center",
    "r": "right", "right": "right",
    "": "default", None: "default",
}


def normalize_alignment(spec) -> str:
    if spec is None:
        return "default"
    s = str(spec).strip().lower()
    if s in _ALIGN_MAP:
        return _ALIGN_MAP[s]
    if s == "default":
        return "default"
    raise AlignmentError(f"invalid alignment: {spec!r}")


_SEP = {"default": "---", "left": ":---", "center": ":---:", "right": "---:"}


def _escape(cell: object) -> str:
    return str(cell).replace("\\", "\\\\").replace("|", "\\|").replace("\n", " ")


def _pad(value: str, width: int, align: str) -> str:
    if align == "right":
        return value.rjust(width)
    if align == "center":
        return value.center(width)
    return value.ljust(width)


def render(headers, rows, align=None):
    headers_e = [_escape(h) for h in headers]
    rows_e: List[List[str]] = [[_escape(c) for c in r] for r in rows]
    n = len(headers_e)
    if any(len(r) != n for r in rows_e):
        raise ValueError("every row must have the same number of cells as headers")
    if align is None:
        aligns = ["default"] * n
    elif isinstance(align, str):
        aligns = [normalize_alignment(align)] * n
    else:
        aligns = [normalize_alignment(a) for a in align]
        if len(aligns) != n:
            raise AlignmentError(f"alignment list length {len(aligns)} != columns {n}")
    seps = [_SEP[a] for a in aligns]
    widths = [
        max(len(headers_e[i]), len(seps[i]), *(len(r[i]) for r in rows_e))
        for i in range(n)
    ]
    body_aligns = ["left" if a == "default" else a for a in aligns]
    out = ["| " + " | ".join(_pad(headers_e[i], widths[i], body_aligns[i]) for i in range(n)) + " |"]
    out.append("| " + " | ".join(
        seps[i].ljust(widths[i], "-") if aligns[i] == "default"
        else _adjust_sep(seps[i], widths[i], aligns[i])
        for i in range(n)
    ) + " |")
    for r in rows_e:
        out.append("| " + " | ".join(_pad(r[i], widths[i], body_aligns[i]) for i in range(n)) + " |")
    return "\n".join(out)


def _adjust_sep(sep: str, width: int, align: str) -> str:
    leading = sep.startswith(":")
    trailing = sep.endswith(":")
    body_len = width - (1 if leading else 0) - (1 if trailing else 0)
    body = "-" * max(body_len, 3)
    return ("" if not leading else ":") + body + ("" if not trailing else ":")
