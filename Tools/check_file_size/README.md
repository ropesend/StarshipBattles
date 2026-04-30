# check_file_size

Enforce the 500-LOC ceiling on production files (`game/`) per PROJ-309.

## Usage

```powershell
python Tools/check_file_size/check_file_size.py
```

Walks `game/` and prints any file that exceeds 500 lines (test files are
exempt; configured via the script's allowlist).

Exit code:
- `0` — all production files under 500 LOC.
- `1` — at least one file over the limit.

## Why a subdirectory

`Tools/README.md` requires every tool to have its own subdirectory and
README. This file was relocated from a loose `Tools/check_file_size.py`
into `Tools/check_file_size/check_file_size.py` during the support-system
cleanup pass on 2026-04-29.
