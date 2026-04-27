# PROJ-309 File Manifest

## Files

### EDIT (convention)
| File | Type | Notes |
|------|------|-------|
| `CLAUDE.md` | Instructions | Add 500-LOC rule under Code Quality |
| `docs/03_CONVENTIONS.md` | Docs | Add §File Size section |

### EDIT or DELETE (decomposition targets — per Phase 2 design)
| File | Lines (current) | Likely fate |
|------|----------------:|-------------|
| `game/ui/screens/race_setup_screen.py` | 1588 | EDIT or DELETE (depending on Option A/B) |
| `game/ui/screens/strategy_renderer.py` | 1205 | EDIT or DELETE |
| `game/ui/screens/test_lab/renderer.py` | 1193 | EDIT or DELETE |
| `game/core/protocols.py` | 1087 | DELETE — replaced by `game/core/protocols/` package |
| `game/strategy/engine/command_handlers.py` | 1072 | EDIT (re-export shim) or DELETE |
| `game/ui/screens/test_lab/test_run_details.py` | 957 | EDIT or DELETE |
| `game/strategy/facade/strategy_session_facade.py` | 922 | EDIT (slices composed) |
| `game/ui/screens/workshop_viewmodel.py` | 873 | EDIT or DELETE |
| `game/app.py` | 849 | EDIT (probably keeps `app.py` as the entry point with bootstrap/run-loop/screen extracted) |
| `game/ui/screens/strategy_window_manager.py` | 817 | EDIT or DELETE |

### NEW (created by decompositions — final shape per Phase 2 designs)
- `game/ui/screens/race_setup/*.py` (sub-modules)
- `game/ui/screens/strategy_render/*.py`
- `game/ui/screens/test_lab/render/*.py` (or similar)
- `game/core/protocols/*.py` (package: combat, strategy, ai, ui, registry)
- `game/strategy/engine/handlers/*.py` (one handler per file)
- `game/strategy/facade/<domain>_slice.py`
- `game/ui/screens/workshop/*.py`
- `game/<bootstrap_or_runloop>.py` (split out of app.py)
- `game/ui/screens/strategy_windowing/*.py`

(Exact paths decided in Phase 2 per-file design docs.)

### NEW (project artifacts)
- `Projects/active_projects/PROJ-309/findings/<file>_decomposition.md` × 10 — Phase 2 deliverables
- `Tools/check_file_size.py` (OPTIONAL — Phase 4.4)

### NEW (tests)
- Per sub-phase: TDD contract tests for the public API surface preservation. Paths under `tests/unit/`

### EXPLICITLY EXCLUDED
- The other 52 files >500 LOC
- Test files (long test files often legitimate)
- Files where the public API surface intentionally changes (out of scope)
