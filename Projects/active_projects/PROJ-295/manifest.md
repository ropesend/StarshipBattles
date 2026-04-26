# PROJ-295 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files

| File | Type | Status | Notes |
|------|------|--------|-------|
| Tools/qa_observer/observer.py | Production (Tool) | Complete | Phase 1: pyaudio → sounddevice. ~25 lines refactored in `record_audio_loop`. SAMPLE_WIDTH/DTYPE constants replace pyaudio.paInt16. |
| Tools/qa_observer/audio_monitor.py | Production (Tool) | Complete | Phase 1: pyaudio → sounddevice. Same pattern as observer.py. self.pa removed. |
| Tools/qa_observer/requirements.txt | Config | Complete | Phase 1: pyaudio → sounddevice. Phase 3: + audioop-lts ; python_version >= "3.13" marker. |
| requirements-dev.txt | Config | Complete | Phase 1: pyaudio → sounddevice. Phase 3: + audioop-lts marker. |
| pyproject.toml | Config (NEW) | Complete | Phase 3: 8 lines, declares `requires-python = ">=3.13"` + `name`/`description`. |
| .python-version | Config (NEW) | Complete | Phase 4: pyenv hint. Single line `3.13.13`. |
| .venv/ | Local env (NEW, gitignored) | Complete | Phase 3: created via `py -3.13 -m venv .venv`. Not committed. |
| tests/unit/ui/screens/test_strategy_renderer_animation.py | Test | Complete | Phase 3 Task 3.6: `test_different_warp_points_get_different_offsets` rewritten from fragile single-pair check to statistical 100-pair distribution check. Robust to any randomized hash. |
| CLAUDE.md | Doc | Complete | Phase 4: Tech Stack updated to "Python 3.13+", baseline 14420 → 15112 tests. |
| combat_lab/README.md | Doc | Complete | Phase 4: System Requirements "Python 3.10+" → "Python 3.13+". |
| C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\proj_295_python_upgrade.md | Memory (NEW, out-of-tree) | Complete | Phase 4: Topic file with full upgrade detail. |
| C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\MEMORY.md | Memory (out-of-tree) | Complete | Phase 4: One-line index entry pointing to topic file. |

## Production code: 0 source files modified

The `game/` package is unchanged. PROJ-295 is purely environment + tooling + docs. The only production-code file touched is the `Tools/qa_observer/` audio handling, which is QA tooling not game code.

## Test files: 1 modified

`tests/unit/ui/screens/test_strategy_renderer_animation.py` — improved a fragile-by-design test that flaked under Python 3.13's hash randomization. Test still verifies the underlying claim ("different inputs → varied offsets") more robustly.
