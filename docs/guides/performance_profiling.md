# Performance Profiling

> **Last verified:** 2026-05-08 - Checked against `Tools/profiling/run_scalene.py`, `Tools/profiling/README.md`, `game/core/profiling.py`, and the profiling workflow tests.

Use Scalene for evidence, not permission to bypass engineering rules. Write or identify a failing or characterization test first, profile a repeatable scenario, fix root causes only, and rerun the same test/profile before claiming improvement. Do not add compatibility shims, hidden globals, cross-layer imports, monkey patches, benchmark-only branches, or duplicate profiling paths.

## Wrapper Contract

- Wrapper: `Tools/profiling/run_scalene.py`; it is a developer tool and is not imported by production code.
- Output: `output/profiles/scalene/` as JSON, ignored by git.
- Notes template: `Tools/profiling/workflows/profile-pass-template.md`.
- Dependency: `scalene>=2.2.1` from `requirements-dev.txt`.
- Root discovery walks upward from the script until it finds `game/` and `data/`; do not replace this with machine-specific paths.
- Default `--profile-only` is `game,combat_lab`, keeping Scalene focused on project code.
- Default output names are `<timestamp>-<scenario>-<mode>.json`; use `--timestamp` for comparable reruns.
- Default profiles are reduced hotspot views; use `--no-reduced-profile` only when line coverage matters.
- `--dry-run` prints the exact Scalene command and output path without executing it.
- If Scalene is missing, the wrapper exits with code `2` and points to `pip install -r requirements-dev.txt`.

Setup:

```powershell
python -m pip install -r requirements-dev.txt
```

## Commands

Dry-run first when constructing a new pass:

```powershell
python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/path/to/test.py --pytest-filter test_name --dry-run
```

CPU mode is the standard first pass:

```powershell
python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/performance
python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/path/to/test.py --pytest-filter test_name
python Tools/profiling/run_scalene.py app --mode cpu
python Tools/profiling/run_scalene.py combat-lab --mode cpu
```

Use full mode only after CPU results raise allocation, leak, or copy-volume questions:

```powershell
python Tools/profiling/run_scalene.py app --mode full
python Tools/profiling/run_scalene.py pytest --mode full --pytest-target tests/path/to/test.py --pytest-filter test_name
```

Pass scenario-specific arguments after `--`:

```powershell
python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/unit -- --maxfail=1
python Tools/profiling/run_scalene.py app --mode cpu -- --force-resolution
python Tools/profiling/run_scalene.py combat-lab --mode cpu -- --filter smoke
```

Render results:

```powershell
python -m scalene view output/profiles/scalene/<profile>.json --html
python -m scalene view output/profiles/scalene/<profile>.json --cli
```

## Scenario Selection

Prefer narrow, deterministic scenarios:

- Battle simulation: one deterministic battle test or Combat Lab scenario.
- Strategy turns: a representative turn-processing test or script.
- Galaxy generation: one fixed-size generation path such as `tests/performance/bench_galaxy_planet_star.py`.
- UI startup/rendering: `app` scenario uses `launcher.py`; override with `--entrypoint` only when profiling a different real-Pygame path.
- Asset processing: profile the relevant `Tools/` script or add a targeted test first.

Avoid profiling the full suite first; it usually measures pytest and setup overhead more than game behavior. The pytest scenario adds `-n 0` unless xdist is explicitly requested, because Scalene profiles process trees and pytest-xdist makes output noisy. Use `--allow-xdist` only for a multiprocessing investigation.

On Windows, avoid tests whose main behavior is spawning subprocesses. Scalene wraps the Python executable during profiled runs, so subprocess harness tests can fail for reasons unrelated to game performance.

## Interpretation

| Signal | Meaning | Typical action |
|--------|---------|----------------|
| Python time | Project Python code repeats or does expensive work | Improve algorithm, data shape, cache boundary, or loop |
| Native time | C/native library calls dominate | Reduce call count, conversions, surface work, or array churn |
| System time | I/O, waiting, sleeping, or OS work dominates | Batch/defer I/O and remove accidental blocking |
| Memory growth | Allocations accumulate | Reuse objects, narrow lifetimes, or fix ownership |
| Copy volume | Data crosses Python/native boundaries too often | Avoid conversions and duplicate buffers |

Loop: find the first stable hotspot that explains the symptom, classify it, confirm the target layer, protect the behavior or contract with a focused test, fix the root cause, rerun the same test/profile, and record before/after notes when the result should be durable.

Do not optimize from one noisy run. Repeat enough times to distinguish stable hotspots from test-load variance.

## Internal Profiler

`game/core/profiling.py` is for named in-game action timing and UI-visible profiling state. `Profiler` is created through `ApplicationContext` or explicit tests, while `set_default_profiler()` supports `profile_action()` and `profile_block()` convenience hooks. Records contain `name`, `duration_ms`, `timestamp`, and `metadata`; `save_history()` writes via `game.core.json_utils` to `Paths.PROFILING_HISTORY`.

Use the internal profiler to identify broad actions and startup phases. Use Scalene to find source-line/function CPU, allocation, native-call, and copy-volume hotspots. Startup instrumentation writes greppable names like `startup: <subphase>` into `ctx.profiler.records` and `[startup] <subphase>: X.XXs` log lines.

## Extension Recipes

Add a new wrapper scenario:

1. Add `_build_<scenario>_command(args) -> ProfileCommand` in `Tools/profiling/run_scalene.py`.
2. Add a subparser in `_build_parser()` and call `_add_common_args()` so `--mode`, `--output-dir`, `--profile-only`, `--timestamp`, `--no-reduced-profile`, and `--dry-run` stay consistent.
3. Route it in `build_command()` and use a stable scenario name for output files.
4. Add or update `tests/unit/tools/test_scalene_profiling_workflow.py`.
5. Update `Tools/profiling/README.md`, this guide, and the repo-local profiling skill if the workflow changes.

Add a durable performance gate:

1. Prefer deterministic count/contract assertions over exact wall-clock thresholds.
2. Put broad perf gates under `tests/performance/`; put behavior-preserving characterization tests near the layer they protect.
3. If timing is unavoidable, keep thresholds loose, document variance, and print measured values for visibility.
4. Run the focused test directly before using it as a profiling target.

Add internal action timing:

1. Use `ctx.profiler` at composition roots or `profile_block()` / `profile_action()` for named spans.
2. Keep names stable and grep-friendly.
3. Include metadata only when it helps correlate user-visible scenarios.
4. Do not add internal timing as a substitute for a Scalene pass when line-level hotspot evidence is needed.

## Verification Commands

```powershell
python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/unit/core --pytest-filter sample_case --timestamp 20260428T000000 --dry-run
pytest tests/unit/tools/test_scalene_profiling_workflow.py
pytest tests/unit/core/profiling tests/unit/test_app_bootstrap_profiling.py
pytest tests/performance
```

