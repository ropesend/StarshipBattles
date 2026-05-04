# Profiling

Repeatable Scalene profiling commands for Starship Battles.

## Purpose

Use this tool when investigating performance with evidence instead of intuition. It standardizes where Scalene profiles are written and keeps profiling commands out of production code.

No production code imports this tool. It is a developer workflow wrapper around `python -m scalene run`.

## Requirements

Install development dependencies first:

```powershell
python -m pip install -r requirements-dev.txt
```

`scalene>=2.2.1` is declared in `requirements-dev.txt`.

## Usage

```powershell
python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/performance
python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/path/to/test.py --pytest-filter test_name
python Tools/profiling/run_scalene.py app --mode cpu
python Tools/profiling/run_scalene.py combat-lab --mode cpu
python Tools/profiling/run_scalene.py app --mode full
```

Use `--dry-run` to print the command without executing it.

### Modes

- `cpu` - passes `--cpu-only`; use this first because it has lower overhead and cleaner signal.
- `full` - omits `--cpu-only`; use this after a CPU pass when allocation, leak, or copy-volume evidence matters.

### Arguments

- `--profile-only` - comma-separated filename fragments to profile. Defaults to `game,combat_lab`.
- `--output-dir` - output folder. Defaults to `output/profiles/scalene`.
- `--timestamp` - stable timestamp for repeatable output names.
- `--no-reduced-profile` - ask Scalene to show all profiled lines.
- `--pytest-target` - pytest path for the `pytest` scenario.
- `--pytest-filter` - optional pytest `-k` expression.
- `--allow-xdist` - do not add `-n 0`. The default disables xdist because worker processes make Scalene output noisy and can fail on paths with spaces.

Additional scenario arguments can be passed after `--`.

On Windows, avoid profiling tests whose main behavior is spawning subprocesses. Scalene wraps the Python executable during profiled runs, which can make subprocess harness tests fail for reasons unrelated to game performance.

## Output

Profiles are written as JSON under:

```text
output/profiles/scalene/
```

Render a profile with:

```powershell
python -m scalene view output/profiles/scalene/<profile>.json --html
python -m scalene view output/profiles/scalene/<profile>.json --cli
```

Generated profile files are ignored by git.
