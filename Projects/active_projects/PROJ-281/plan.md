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
| 2. Audit and migrate 47 callers of `BattleScreen.start(team0, team1)` | Not Started | TBD |
| 3. Delete the `start()` shim and `_build_fallback_outcome` (~90 lines) | Not Started | TBD |
| 4. Documentation update | Not Started | TBD |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Phase 2 (ready to start) — migrate 47 test callers
**Last Action:** Phase 1 complete. `make_minimal_spec` helper shipped in [tests/fixtures/battle.py](../../../tests/fixtures/battle.py) with 19 unit tests ([tests/fixtures/test_make_minimal_spec.py](../../../tests/fixtures/test_make_minimal_spec.py)) + 2 smoke integration tests ([tests/integration/test_make_minimal_spec_smoke.py](../../../tests/integration/test_make_minimal_spec_smoke.py)) proving the helper feeds both `BattleController.start_from_spec` and headless `run_battle(spec)`. Audit confirmed 47 callers across 3 files (not "~46"): `test_battle_screen.py` (7), `test_battle_screen_simulation.py` (37), `test_battle_setup_logic.py` (3).
**Next Action:** Phase 2 — migrate the 47 callers to use `make_minimal_spec` + the spec-based entry path. This is the bulk of the project work (substantial grep + edit across 3 files). Defer to a fresh session — context budget matters here.
**Blockers:** None. Phase 1 unblocks Phase 2; no cross-project dependencies remain.

**Context for Next Agent (Phase 2):**
- Helper signature: `make_minimal_spec(ships_by_team: Dict[int, List[Ship]], *, seed=0, max_ticks=1000, telemetry_level=None) -> BattleSpec`
- Canonical migration pattern for each test:
  ```python
  # Before:
  self.scene.start([self.ship1], [self.ship2], headless=True)

  # After:
  from tests.fixtures.battle import make_minimal_spec
  from game.simulation.battle_controller import BattleController
  from game.ai.ai_factory import AIControllerFactory

  ships = [self.ship1, self.ship2]
  spec = make_minimal_spec({0: [self.ship1], 1: [self.ship2]})

  def _builder(ship_spec, team_id):
      return ships[team_id]

  controller = BattleController()
  controller.start_from_spec(spec, ai_factory=AIControllerFactory(), ship_builder=_builder)
  self.scene.start_battle(controller)
  ```
- For `headless=True` tests, consider using `run_battle(spec, ship_builder=_builder)` directly instead of the controller path — simpler
- Some tests may need `max_ticks` or seed overrides passed to `make_minimal_spec`
- A test-local helper (inside the test class or at module-top) that wraps the migration pattern is recommended to avoid repeating the builder boilerplate 47 times
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
