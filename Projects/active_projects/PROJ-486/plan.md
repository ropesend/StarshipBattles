# PROJ-486: Legacy removal — dead BattleController.load_state (2026-05-20)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-486` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-486 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Delete `load_state` + retire 4 test callers | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Audit remediation (Codex consult 2026-05-23) | Complete | [phase_2_checklist.md](phase_2_checklist.md) |

## Current State
**Last Updated:** 2026-05-23
**Active Phase:** Complete
**Last Action:** Deleted `BattleController.load_state` (~87 LOC) and retired 4 dead test callers in `test_state.py` (test_load_state_restores_battle, test_load_state_handles_error, and the entire TestBattleControllerLoadStateProjectiles class with its 2 tests + helper). Removed unused `BattleConfig` import from test file. Renamed `TestBattleControllerStateSaveLoad` class to `TestBattleControllerStateSave` since only save tests remain. 97/97 tests in tests/unit/simulation/battle_controller/ pass.
**Next Action:** User verification, then commit.
**Blockers:** None

## Overview
`BattleController.load_state` (~87 LOC at `game/simulation/battle_controller.py:509-595`) has zero production callers — its own inline comment at line 510 records this. The independent verifier confirmed 0 production callers but discovered 4 test callers in `tests/unit/simulation/battle_controller/test_state.py` (lines 90, 128, 245, 268) that the audit's verifier missed. Delete `load_state` and migrate/retire the 4 test callers.

> Note: line refs refreshed 2026-05-22 after merge `67116932d` (PROJ-460 Phase 2 extracted `start_from_spec` to a sibling module, shifting `load_state` upward from 612-698 to 509-595; same size, still dead).

## Goals
- Delete the `load_state` method (~87 LOC).
- Migrate or retire the 4 test callers in `tests/unit/simulation/battle_controller/test_state.py`.

## Scope
**In:** `BattleController.load_state` (lines 509-595) and the 4 test callers in `test_state.py`.
**Out:**
- `save_state` — keep. The inline note says `load_state` exists "for test coverage + internal `save_state()` symmetry," but `save_state` itself may have production usage and is not in scope here. If it turns out `save_state` is also dead, surface as a separate finding.
- The save/restore *contract documentation* — if the only purpose of `load_state` was to specify the save format, capture that as a docstring on `save_state` or a separate document before deletion.
- REJECTED and OUT_OF_SCOPE findings: see [findings/verification_report.md](findings/verification_report.md).
- Other legacy-audit clusters: see siblings PROJ-484, PROJ-485, PROJ-487, PROJ-488, PROJ-489, PROJ-490.

## Key Files
| Component | File Path |
|-----------|-----------|
| `BattleController.load_state` [EDIT] | `game/simulation/battle_controller.py` |
| 4 test callers [EDIT] | `tests/unit/simulation/battle_controller/test_state.py` |

## Related Documents
- [design.md](design.md)
- [decisions.md](decisions.md)
- [findings/verification_report.md](findings/verification_report.md)
- [findings/source_audit.md](findings/source_audit.md)
- [findings/bundling_decisions.md](findings/bundling_decisions.md)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
