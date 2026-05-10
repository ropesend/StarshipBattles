# Performance Profiling

Use this guide when investigating Starship Battles performance with Scalene. Profiling is evidence gathering; it does not relax architecture, TDD, dependency, or maintainability rules.

## Policy

- Write or identify a failing/characterization test before changing behavior.
- Profile a repeatable scenario before optimizing.
- Do not optimize from a single profile. Re-run enough times to separate stable hotspots from noise.
- Prefer root-cause fixes: algorithmic improvements, scoped caching with clear invalidation, reduced duplicate work, and fewer unnecessary allocations or copies.
- Do not add compatibility shims, hidden globals, cross-layer imports, monkey patches, or special-case benchmark paths.
- Keep profiles and notes out of source control unless they are small, intentional documentation artifacts.

## Tooling

Scalene is a dev dependency in `requirements-dev.txt`. Install it into your system Python 3.14:

```powershell
python -m pip install -r requirements-dev.txt
```

The wrapper lives at `Tools/profiling/run_scalene.py`. It writes profile JSON files under `output/profiles/scalene/`, which is ignored by git.

## How Scalene Helps

Scalene samples execution rather than tracing every call. It reports line-level and function-level CPU data, with time split into Python, native/library, and system/I/O categories. In full mode it also reports memory growth, likely leaks, and copy volume.

Use the split to decide what kind of fix is reasonable:

| Signal | Meaning | Typical action |
|--------|---------|----------------|
| Python time | Our Python code is doing repeated or expensive work | Improve algorithm, data structure, caching boundary, or loop shape |
| Native time | C/native library calls dominate | Reduce call count, conversions, surface work, or array churn |
| System time | I/O, waiting, sleeping, or OS work dominates | Batch or defer I/O, remove accidental blocking |
| Memory growth | Allocations accumulate | Reuse objects, narrow lifetimes, fix ownership |
| Copy volume | Data is copied across Python/native boundaries | Avoid conversions and duplicate buffers |

## Standard Pass

Start CPU-only:

```powershell
python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/performance
python Tools/profiling/run_scalene.py pytest --mode cpu --pytest-target tests/path/to/test.py --pytest-filter test_name
python Tools/profiling/run_scalene.py app --mode cpu
python Tools/profiling/run_scalene.py combat-lab --mode cpu
```

Use full mode only after CPU results suggest allocation, leak, or copying questions:

```powershell
python Tools/profiling/run_scalene.py app --mode full
python Tools/profiling/run_scalene.py pytest --mode full --pytest-target tests/path/to/test.py --pytest-filter test_name
```

Render results:

```powershell
python -m scalene view output/profiles/scalene/<profile>.json --html
python -m scalene view output/profiles/scalene/<profile>.json --cli
```

## Scenario Selection

Prefer focused scenarios:

- Battle simulation: use a single deterministic battle test or a Combat Lab scenario.
- Strategy turns: profile a test or script that processes a representative turn.
- Galaxy generation: profile one fixed-size generation path.
- UI startup or rendering: profile `launcher.py` only when the workflow needs real Pygame behavior.
- Asset processing: profile the relevant `Tools/` script directly or create a targeted test first.

Avoid starting with the full suite. Full-suite profiling usually measures pytest and setup overhead more than game behavior.

The pytest scenario adds `-n 0` by default. Scalene profiles a process tree, while pytest-xdist fans work out to worker processes; disabling xdist keeps profile output focused and avoids worker bootstrap issues on paths with spaces. Use `--allow-xdist` only for an explicit multiprocessing investigation.

On Windows, avoid choosing tests whose main behavior is spawning subprocesses. Scalene temporarily wraps the Python executable for profiled runs, and subprocess-focused tests can fail for reasons unrelated to the game code. Profile the underlying game workflow directly instead.

## Interpreting Results

1. Find the first hotspot that explains the symptom.
2. Classify it as Python, native, system, memory, or copy-volume dominated.
3. Check whether the hotspot belongs to the layer you plan to change.
4. Add or update a test that protects the intended behavior or performance-sensitive contract.
5. Implement the smallest maintainable root-cause fix.
6. Re-run the focused test and repeat the same profiling scenario.
7. Record the before/after result in the ticket, project, or `Reviews/results/` when the finding is durable.

Use `Tools/profiling/workflows/profile-pass-template.md` for notes.

## Relationship To Internal Profiling

`game/core/profiling.py` remains useful for named in-game action timing and UI-visible profiling state. Scalene answers a different question: which source lines, allocations, native calls, and copies dominate a repeatable run. Use the internal profiler to identify broad app actions and Scalene to investigate specific implementation hotspots.

## References

- Scalene PyPI: https://pypi.org/project/scalene/
- Scalene GitHub: https://github.com/plasma-umass/scalene
- Scalene paper: https://arxiv.org/abs/2006.03879
