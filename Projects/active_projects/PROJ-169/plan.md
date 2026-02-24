# PROJ-169: Dead Code and Orphaned File Cleanup

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-169` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-169 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Zero-Risk Deletes | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Script & Tool Cleanup | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Formation Editor Migration | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Polish | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-23 18:30
**Active Phase:** Planning
**Last Action:** Project created from dead code review findings
**Next Action:** User approves plan, then begin Phase 1
**Blockers:** None
**Context for Next Agent:** All findings validated by 6 review agents. Every deletion target verified for zero imports/references. See design.md for full review analysis. Review report at `Reviews/results/2026-02-23_180329_focused_dead-code-cleanup-audit/report.md`.

## Overview
Remove ~4,288 lines of confirmed dead Python code across 54 files, untrack 22.8MB of __pycache__ from git, consolidate a duplicate formation_editor.py, clean up 14 unused imports, and fix directory structure issues. All deletions verified for zero runtime dependencies.

## Goals
- Delete all confirmed dead code (legacy scripts, one-time tools, duplicate files)
- Untrack __pycache__ directories from git (22.8MB savings)
- Consolidate duplicate formation_editor.py and update all imports
- Remove unused standard library imports across 10 game/ files
- Fix directory structure issues (empty dirs, misnamed dirs, misplaced test)

## Scope
**In:**
- Category A: Legacy migration scripts in `docs/_legacy_docs/Tools/` (10 files)
- Category B: Duplicate `formatimg.py` in `assets/ShipThemes/` (5 files)
- Category D: Dead files in `Tools/` (8 files + __init__.py)
- Category E: Dead scripts in `scripts/` (13 files + 2 subdirectories)
- Category F: `__pycache__` tracked in git (176 dirs, 1,593 .pyc files)
- Category I: Unused imports in `game/` (14 imports across 10 files)
- Duplicate `Tools/formation_editor.py` consolidation
- Empty directory cleanup (`game/ui/hud/`, `game/simulation/entities/mixins/`)
- Directory rename (`tests/refactor/` -> merge into `tests/regression/`)
- Test file relocation (`tests/unit/builder/test_formation_editor_logic.py`)
- Configuration updates (`pytest.ini`)

**Out:**
- `test_framework/` — confirmed ACTIVE (Combat Lab UI dependency, unique functionality)
- `Debugging/` — confirmed ACTIVE (bug tracking workflow)
- `game/ui/services/tkinter_utils.py` — confirmed WELL PLACED (intentional consolidation)
- `game/ui/panels/battle_panels.py` BattlePanel — confirmed CORRECT PATTERN (active abstract base)
- Any code changes beyond deletion/relocation

## Key Files
| Component | File Path |
|-----------|-----------|
| Legacy scripts (delete) | `docs/_legacy_docs/Tools/*.py` |
| Duplicate formatimg (delete) | `assets/ShipThemes/**/formatimg.py` |
| Dead Tools (delete) | `Tools/component_manager.py`, `Tools/component_graphic_picker.py`, etc. |
| Dead scripts (delete) | `scripts/apply_resource_costs.py`, `scripts/reorg_tests.py`, etc. |
| Formation editor (game version) | `game/ui/screens/formation_editor.py` |
| Formation editor (duplicate, delete) | `Tools/formation_editor.py` |
| App import to update | `game/app.py:22` |
| Test to relocate | `tests/unit/builder/test_formation_editor_logic.py` |
| Config to update | `pytest.ini:3,5` |

## Related Documents
- [design.md](design.md) - Review analysis and agent findings summary
- [decisions.md](decisions.md) - Full decisions log
- Review report: `Reviews/results/2026-02-23_180329_focused_dead-code-cleanup-audit/report.md`
- Agent reports: `Reviews/results/2026-02-23_180329_focused_dead-code-cleanup-audit/findings/`

---

## Phases

### Phase 1: Zero-Risk Deletes [Simple]
**Objective:** Delete files with zero dependencies — legacy scripts, duplicate image processors, untrack __pycache__
**Status:** Not Started
See [phase_1_checklist.md](phase_1_checklist.md) for detailed tasks.

### Phase 2: Script & Tool Cleanup [Simple]
**Objective:** Delete confirmed dead files from Tools/ and scripts/ directories
**Status:** Not Started
See [phase_2_checklist.md](phase_2_checklist.md) for detailed tasks.

### Phase 3: Formation Editor Migration [Medium]
**Objective:** Consolidate duplicate formation_editor.py, update imports and config, delete Tools/ directory
**Status:** Not Started
See [phase_3_checklist.md](phase_3_checklist.md) for detailed tasks.

### Phase 4: Polish [Simple]
**Objective:** Remove unused imports, fix directory structure, clean up empty directories
**Status:** Not Started
See [phase_4_checklist.md](phase_4_checklist.md) for detailed tasks.

---

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing: `pytest tests/ -n 12`
- [ ] No imports broken (verified per-phase)
- [ ] `pytest.ini` updated correctly
- [ ] Tools/ directory fully removed
- [ ] User verified
