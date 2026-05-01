# mdtable

Render GitHub-Flavored-Markdown tables from headers + rows with strict
pipe escaping and per-column alignment. Zero runtime dependencies.

`mdtable` is the Markdown-only companion to
[`csvtable`](https://github.com/nripankadas07/csvtable). It is intended
for code that emits Markdown â generators for documentation pages,
release notes, status reports, README badges â where source-Markdown
fidelity matters more than raw print speed.

## Why mdtable

A surprising amount of "render a Markdown table" code ships in
production with one of three quiet bugs:

1. **Pipes inside cells split the row.** If a cell contains `a|b`,
   most naive renderers emit `| a|b |`, which downstream Markdown
   parsers interpret as two cells.
2. **Newlines inside cells split the row.** A cell containing
   `line1\nline2` will be parsed as two physical rows.
3. **Center alignment isn't actually centered** because the separator
   row (`:---:`) is shorter than 5 chars.

`mdtable` fixes all three: pipes are escaped as `\|`, newlines are
folded to the GFM-standard `<br>`, and the separator row is padded to
match data-cell widths so the source Markdown stays visually aligned.

## Install

```bash
pip install mdtable
```

(or, in this repository's checkout: `pip install -e .`)

## Quick start

```python
from mdtable import render

print(render(
    ["Name", "Score", "Notes"],
    [
        ["Alice", 42, "passing"],
        ["Bob", 7, "needs review"],
        ["Carol|Dean", 100, "tied for first\nwith Eve"],
    ],
    align=["left", "right", "center"],
))
```

```text
| Name       | Score | Notes                  |
| :--------- | ----: | :--------------------: |
| Alice      |    42 |        passing         |
| Bob        |     7 |      needs review      |
| Carol\|Dean |   100 | tied for first<br>with Eve |
```

The pipe inside `Carol|Dean` is escaped, the newline inside the third
row is folded to `<br>`, and the alignment row spec exactly matches
GFM (left â `:---`, right â `---:`, center â `:---:`).

## API reference

### `render(headers, rows=(), *, align=None, min_width=3) -> str`

Render a list of rows as GFM-Markdown source. Returns the table as a
string with no trailing newline.

* `headers` â non-empty iterable of column names. Coerced via `str()`.
* `rows` â iterable of rows. Every row must have `len(headers)` cells.
* `align` â `None`, a single specifier (broadcast to every column), or
  a list of specifiers (one per column). Accepted values:
  - `"left"` / `"l"` / `"<"`
  - `"right"` / `"r"` / `">"`
  - `"center"` / `"c"` / `"^"` (also `"centre"`)
  - `"default"` / `"-"` / `None` / `""`
* `min_width` â minimum visual column width in the source Markdown
  (default 3, matching GFM's separator-row minimum).

Raises `MdTableError` for empty headers / non-iterables / invalid
`min_width`, `RowLengthError` for mismatched row lengths, and
`AlignmentError` for invalid alignment specs.

### `make_table(headers, rows=(), *, align=None, min_width=3) -> Table`

Build a `Table` instance for incremental composition.

### `Table`

```python
table = Table(headers=["a", "b"], align="right")
table.append_row(["1", "2"])
table.extend([["3", "4"], ["5", "6"]])
table.clear()
print(table.render())
```

* `Table(headers, rows=None, align=None, min_width=3)` â construct
  directly. The constructor validates headers and alignment eagerly.
* `append_row(row)` â append one row, validating its column count
  immediately.
* `extend(rows)` â append several rows.
* `clear()` â drop every row (headers and alignment unchanged).
* `render()` â render to a Markdown string.
* `__str__()` is `render()`.

### `escape_cell(value) -> str`

Escape a single cell value. `None` becomes `""`, non-strings are
coerced via `str()`, then backslashes are doubled, pipes are escaped
as `\|`, and CR/LF/CRLF are folded to `<br>`.

### `stringify(value) -> str`

The pre-escape helper: `None` â `""`, strings pass through, anything
else goes through `str()`.

### `normalize_alignment(spec, columns) -> list[str]`

Normalize an alignment spec into a per-column canonical-form list
(`"left"`, `"right"`, `"center"`, `"default"`).

### Errors

* `MdTableError` â base class.
* `RowLengthError(row_index, expected, actual)` â row column count
  mismatch.
* `AlignmentError` â invalid or wrong-sized alignment spec.

## Behavioural guarantees

- **Pipe-safe.** Every emitted line has exactly `len(headers) + 1`
  unescaped `|` characters.
- **Newline-safe.** Cells with embedded `\n`, `\r`, or `\r\n` collapse
  to `<br>`. The output is always exactly
  `2 + len(rows)` lines.
- **Empty-rows-safe.** `render(headers)` (no rows) returns just the
  header + separator pair.
- **GFM-minimum-3-dashes.** The separator row contains at least 3
  dashes per column, even if data is narrower. Center alignment is at
  least 5 (`:---:`).

## Running tests

```bash
pip install -e ".[dev]"
pytest -q
pytest --cov=mdtable --cov-report=term-missing
```

## License

MIT
