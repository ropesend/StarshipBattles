# Lines of Code Counter

Counts lines of code across the Starship Battles project, broken down by source vs. test code.

## Purpose

Provides a quick overview of project size and test-to-source ratio. Useful for tracking codebase growth and ensuring test coverage keeps pace with production code.

## Requirements

Requires `tiktoken`, installed via `requirements-dev.txt`, for exact token counts.
If it is missing, the tool exits without a traceback and prints a `python -m pip
install -r "<repo-root>/requirements-dev.txt"` command based on the checkout that
contains `Tools/loc/loc.py`.

## Usage

```bash
python Tools/loc/loc.py             # simple summary table
python Tools/loc/loc.py --detailed  # JSON output with per-section, per-type breakdowns
```

### Arguments

| Argument     | Description                                                       |
|--------------|-------------------------------------------------------------------|
| `--detailed` | Output a JSON object with per-section breakdowns by file type (py, json, other). |

## Sections Counted

**Production code** (`game/`):
- `ai`, `assets`, `core`, `data`, `engine`, `research`, `simulation`, `strategy`, `ui`
- Top-level files in `game/`
- `launcher.py`

**Test code**:
- `tests/unit`, `tests/integration`, `tests/regression`, `tests/performance`, `tests/repro_issues`, `tests/fixtures`, `tests/infrastructure`
- `combat_lab/`
- `conftest.py`

**Excluded**: `__pycache__`, `.git`, `venv`, `node_modules`, `.VSCodeCounter`, `output/` directories, `combat_lab/test_history/` shards, legacy `test_history.json.migrated`, `.pyc` files.

## Output

### Simple mode (default)

A formatted table showing lines and file counts per section, with totals and test:source ratio:

```
  Starship Battles - Lines of Code
  ================================================================
  Source (game/)                            42,000       312 files
  ----------------------------------------------------------------
  Total source code                        42,000       312 files

  Tests (unit/)                            35,000       280 files
  Tests (integration/)                      5,000        40 files
  ----------------------------------------------------------------
  Total test code                          40,000       320 files

  ================================================================
  GRAND TOTAL                              82,000       632 files

  Test:Source ratio  0.95:1
```

### Detailed mode (`--detailed`)

A JSON object with per-section breakdowns including separate counts for `.py`, `.json`, and other file types.
