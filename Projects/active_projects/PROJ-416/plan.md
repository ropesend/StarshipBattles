# PROJ-416: Legacy removal — race_setup_screen.py shim + Game.running (PROJ-309 vestige) (2026-05-13)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-416` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-416 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Migrate 26 race_setup_screen.py imports + 4 test patches, then delete the shim | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Remove Game.running legacy attribute | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-13
**Active Phase:** Phase 1
**Last Action:** Project created from `2026-05-13_194106_legacy-audit` after independent verification
**Next Action:** Begin Phase 1 tasks
**Blockers:** None

## Overview
Removes two PROJ-309 decomposition vestiges: the 31-line `game/ui/screens/race_setup_screen.py` import shim (~25 executable imports across 2 production files + many test files, plus 4 test patches) and the `Game.running` legacy attribute on `game/app.py` (3 production write/read sites + 6 test usages).

Source: legacy audit `2026-05-13_194106_legacy-audit`, verified items in this bundle = 2.
Removal cluster: `proj309_vestige`.

### Notable callouts
- **Phase 2 scope is larger than originally assessed.** `Game.running` has 3 production write/read sites beyond `__init__`: `_request_shutdown()` (line ~266), `_handle_strategy_action("quit_game")` (line ~452), and `run()` (lines ~502-507). All must be removed; `game/app.py` edits are non-trivial. See decisions.md.
- **Shard 04 claim that `game/app.py` imports from the shim is false.** The actual production importers are `screen_router.py` and `new_game_setup_controller.py`. The shim docstring's `app.py:522` reference is stale. See decisions.md.
- **`test_race_setup_screen_public_api.py` must be deleted, not migrated.** It is a shim contract test with no behavior value beyond the shim lifetime. See decisions.md.

## Goals
- Migrate 26 race_setup_screen.py imports + 4 test patches, then delete the shim
- Remove Game.running legacy attribute

## Scope
**In:** removal cluster `proj309_vestige` — items MIN-002, MIN-001.
**Out:** other clusters' contents (siblings: PROJ-413, PROJ-414, PROJ-415, PROJ-417, PROJ-418, PROJ-419, PROJ-420, PROJ-421); REJECTED and OUT_OF_SCOPE findings (none in this run; see `findings/verification_report.md`).

## Key Files
| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/ui/screens/race_setup_screen.py` | Production | Delete | Whole file removed after caller migration |
| `game/screen_router.py`, `game/ui/screens/new_game_setup_controller.py` | Production | Edit | 2 production callers: migrate `RaceSetupScreen` import to canonical path |
| `tests/unit/ui/screens/test_race_setup_screen.py`, `tests/fixtures/test_race_setup_ui_builders.py` | Test | Edit | Migrate test imports; hoist inline imports |
| `tests/unit/ui/screens/test_race_setup_screen_public_api.py` | Test | Delete | Shim contract test — delete with the shim |
| `tests/unit/ui/test_new_game_setup.py`, `tests/unit/test_screen_router.py` | Test | Edit | Relocate 2 mock.patch strings; rewrite 1 sys.modules injection |
| `docs/02_PATTERNS.md`, `game/ui/screens/race_setup/__init__.py`, `game/ui/screens/race_setup/screen.py` | Docs/Production | Edit | Update stale references to the shim |
| `game/app.py` | Production | Edit | Phase 2: delete `self.running = True` (lines 124-127) AND remove 3 production write/read sites in `_request_shutdown`, `_handle_strategy_action`, `run()` |
| `tests/unit/test_app_delegators.py` | Test | Edit | Migrate 4 usages of `game.running` to behavior assertions |
| `tests/unit/ui/screens/test_strategy_menu_actions.py` | Test | Edit | Migrate 2 usages of `game.running` to behavior assertions |

## Related Documents
- [design.md](design.md) — architecture analysis and design rationale
- [decisions.md](decisions.md) — full decisions log
- [findings/verification_report.md](findings/verification_report.md) — third-pass verification output
- [findings/source_audit.md](findings/source_audit.md) — pointer to the originating audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — Phase D interactive bundling record

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
