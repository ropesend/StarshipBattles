# PROJ-281: BattleScreen Legacy Fallback Removal (migrate start(team0,team1) tests)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-281` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-281 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Build `make_minimal_spec(ships_by_team)` test helper | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Audit and migrate 47 callers of `BattleScreen.start(team0, team1)` | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Delete the `start()` shim and `_build_fallback_outcome` (~90 lines) | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Documentation update | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Phase 2 — Task 2.1 complete; Tasks 2.2-2.5 (47-caller migration) pending fresh session
**Last Action:** Phase 2 Task 2.1 complete. Added module-level helper [tests/fixtures/battle.py::start_battle_screen_with_minimal_spec](../../../tests/fixtures/battle.py) that encapsulates the spec-based migration pattern into a single function call. Added 4 smoke tests in `TestStartBattleScreenWithMinimalSpec` — 23 helper tests pass total. With the helper in place, each of the 47 migrations becomes a 1-line replacement instead of 8 lines of boilerplate.
**Next Action:** Phase 2 Tasks 2.2-2.5 — migrate the 47 callers using the new `start_battle_screen_with_minimal_spec` helper. Start with the smallest file (`test_battle_setup_logic.py`, 3 callers) to validate the pattern end-to-end including the assertion-reshaping issue documented below.
**Blockers:** None.

**Context for Next Agent (Phase 2 migration):**
- **Use the helper:** `from tests.fixtures.battle import start_battle_screen_with_minimal_spec`
- **Canonical migration:**
  ```python
  # Before:
  scene.start([ship1], [ship2], headless=True)

  # After:
  controller = start_battle_screen_with_minimal_spec(
      scene, {0: [ship1], 1: [ship2]}, headless=True,
  )
  ```
- **IMPORTANT — assertion reshape:** tests that assert on `scene.ships`, `scene.ai_controllers`, `scene.projectiles` directly (seen in `test_battle_setup_logic.py`) need assertion updates because those attrs now live on the controller's engine. Use `controller.service.get_engine().ships` etc., OR verify if `BattleScreen.start_battle(controller)` proxies these (check during migration).
- **Shim-specific tests:** `test_battle_scene_clear_state` in `test_battle_setup_logic.py` tests the shim's "calling start() twice clears state" behavior. Under the spec path, each battle creates a new controller — the "clearing" contract doesn't map cleanly. Recommend: delete this test (shim behavior going away) OR rewrite to test controller-level state management. Escalate to user if ambiguous.
- **Migration order suggestion:** start with `test_battle_setup_logic.py` (3 callers, small file) to validate the pattern + uncover any surprises; then `test_battle_screen.py` (7 callers); then `test_battle_screen_simulation.py` (37 callers, bulk).
- Phase 2 validation: `pytest tests/unit/ui/test_battle_screen.py tests/unit/ui/test_battle_screen_simulation.py tests/unit/ui/screens/test_battle_setup_logic.py` should pass
- Phase 3 (delete shim) comes AFTER Phase 2 migration completes — zero callers remain

## Overview
[BattleScreen.start(team0, team1)](../../../game/ui/screens/battle_screen.py) is a deprecated 2-team test convenience shim retained for ~46 unit tests that predate the spec-in contract. It synthesizes a minimal `BattleOutcome` via `_build_fallback_outcome` (~90 lines of manual ship-outcome assembly). Per the codebase's eradicate-old-systems policy ([CLAUDE.md System Migration Policy](../../../CLAUDE.md)), this should be removed: build a small test helper that constructs a minimal `BattleSpec`, migrate all ~46 tests to the spec-in path, then delete both the shim and the fallback outcome builder.

## Goals
- One-line test helper: `make_minimal_spec(ships_by_team) -> BattleSpec`
- All ~46 callers migrated to spec-based setup
- `BattleScreen.start(team0, team1)` shim deleted
- `_build_fallback_outcome` (~90 lines) deleted
- BattleScreen has only ONE entry path: `start_battle(controller)` consuming a running BattleController
- Documentation updated to remove all references to the deprecated path

## Scope
**In:**
- New test helper `tests/helpers/battle_spec_helpers.py::make_minimal_spec(ships_by_team)` (or co-located with existing test helpers)
- Audit all callers of `BattleScreen.start(team0, team1)` — confirm count and list
- Migrate each test caller to use `make_minimal_spec` + the spec-in entry path
- Delete `BattleScreen.start(team0, team1)` and any internal compat plumbing
- Delete `_build_fallback_outcome()` and any helpers it uses exclusively
- Update [docs/systems/combat_simulation.md](../../../docs/systems/combat_simulation.md) to remove the "test-convenience shim" mention
- Update [combat_lab/COMBAT_LAB_DOCUMENTATION.md](../../../combat_lab/COMBAT_LAB_DOCUMENTATION.md) if it references the shim

**Out:**
- Any change to the production spec-in path (`BattleScreen.start_battle(controller)`)
- Any change to BattleController, run_battle, or BattleEngine
- Refactoring of unrelated BattleScreen behavior (panels, rendering, hit effects)

## Key Files
| Component | File Path |
|-----------|-----------|
| Legacy shim | `game/ui/screens/battle_screen.py` (`start(team0, team1)`) |
| Fallback outcome builder | `game/ui/screens/battle_screen.py` (`_build_fallback_outcome`) |
| New test helper | `tests/helpers/battle_spec_helpers.py` (NEW) |
| Existing test helpers (potential co-location) | `tests/conftest.py`, existing fixture files |
| Test files using legacy shim | ~46 files (audit in Phase 1.2) |
| Doc references | `docs/systems/combat_simulation.md` |

## Decisions Log
See [decisions.md](decisions.md) for full rationale.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-17 | Approach: migrate then delete (Option A) | User chose "Migrate then delete (Recommended)". Single PR, no transition state, follows the codebase's eradicate-old-systems policy. Rejected: delete-first-fix-reactively (messier middle); keep-shim-replace-fallback-only (kept dual paths) |
| 2026-04-17 | Sequencing: AFTER PROJ-280 | Lets the Combat Lab cluster (PROJ-278/279/280) close before opening the UI cleanup cluster. Independent technically, but cleaner cognitive grouping |
| 2026-04-17 | One PR (no incremental delivery within this project) | Migration + deletion in one commit means no orphaned state in `main`. Test churn happens once |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Grep for `BattleScreen.start(` returns zero hits
- [ ] Grep for `_build_fallback_outcome` returns zero hits
- [ ] User verified
