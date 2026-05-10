# PROJ-256: Centralize All File Paths via Paths Class

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-256` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-256 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Expand Paths Constants & Move ships/ | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Migrate Data File References | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Migrate Asset Path References | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Migrate Remaining Hardcoded Paths | Complete | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. Verification & Documentation | Complete | [phase_5_checklist.md](phase_5_checklist.md) |

## Current State
**Last Updated:** 2026-04-07
**Active Phase:** Complete
**Next Action:** Project complete — all phases done.
**Blockers:** None
**Context for Next Agent:** All 5 phases complete. 25+ files migrated to use Paths constants. ships/ moved to output/ships/. 14737 tests passing. Convention documented in docs/03_CONVENTIONS.md. A few Tools/ files (component_visuals_manager, image_comparator) still have hardcoded paths but are standalone MCP servers outside the game package.

## Overview

The project has a centralized path configuration class (`game/core/paths.py::Paths`) that defines constants for directories and files. However, ~40 call sites across ~25 files bypass it with hardcoded string literals like `"data/components.json"`, `os.path.join("assets", "ShipThemes", ...)`, and `"ships"`. This creates:

- **Fragility**: Renaming or moving a directory requires a codebase-wide search instead of a single constant change.
- **Inconsistency**: Some callers use `Paths.DATA_DIR`, others hardcode `"data/"` — same intent, different code.
- **Architecture smell**: The `ships/` directory (user-created designs) lives at project root instead of under `output/` with all other user-generated data (saves, screenshots, logs, settings, races).

## Goals

1. Move `ships/` under `output/` to match the established user-data pattern.
2. Add missing constants to `Paths` for all referenced directories and files.
3. Replace every hardcoded path in production code with the appropriate `Paths` constant.
4. Ensure no future drift by establishing the pattern clearly.

## Design Decisions

- **`Paths` is in `game/core/`** (bottom layer) so every layer can import it. No dependency violations.
- **Default parameters**: Functions with `file_path="data/components.json"` defaults will change to `file_path=None` with `Paths.COMPONENTS_FILE` applied inside the function body. This avoids module-load-order issues with class-level defaults.
- **`os.path.join` vs `pathlib`**: Keep existing style per file. Don't mix — if a file uses `os.path`, use `Paths.X` (str). If it uses `pathlib`, use `Paths.get_x()` (Path).
- **Test files**: Out of scope. Test files may legitimately use relative paths to test-specific data directories.
- **Scripts/Tools**: Fix `Tools/qa_observer/observer.py`. Scripts that use CLI `--output` args are fine as-is.

## Risk Assessment

- **Low risk**: Each change is a simple constant substitution. Behavior is identical.
- **Medium risk**: Moving `ships/` to `output/ships/` changes the save/load location. Existing ship JSON files need to be physically moved. The file dialog in ShipIO will open to the new location.
- **Mitigation**: TDD — write tests that verify paths resolve correctly before and after each change. Run full suite after each phase.

## Phases

### Phase 1: Expand Paths Constants & Move ships/
Add missing constants to `Paths`. Move `SHIPS_DIR` under `OUTPUT_DIR`. Update `ShipIO` and the 3 other files that reference the ships directory. Move existing ship JSON files.

### Phase 2: Migrate Data File References
Replace hardcoded `"data/..."` paths in `component.py`, `resources.py`, `ship_loader.py`, `registry_loader.py`, `build_queue_source.py`, and the 3 strategy generation loaders.

### Phase 3: Migrate Asset Path References
Replace hardcoded `"assets/..."` paths in `sprites.py`, `build_queue_portraits.py`, `planet_report_panel.py`, `design_image_helper.py`, `portraits.py`, `right_panel.py`, and `game_config.py`.

### Phase 4: Migrate Remaining Hardcoded Paths
Fix `formation_editor.py`, `setup_screen.py` (battles dir), `homeworld_presets.py`, `race_randomizer.py`, `qa_observer/observer.py`, and any stragglers found during verification.

### Phase 5: Verification & Documentation
Run full test suite. Grep for any remaining hardcoded path patterns. Update `docs/` if `Paths` or directory structure is documented anywhere.
