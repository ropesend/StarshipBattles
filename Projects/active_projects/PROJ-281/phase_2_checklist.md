# Phase 2: Migrate 47 test callers off `BattleScreen.start(team0, team1)`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-281 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Migrate every test caller of `self.scene.start([ship1], [ship2], ...)` to use the spec-based path (`make_minimal_spec` + `BattleController.start_from_spec` or headless `run_battle(spec)`). Phase 1 shipped the `make_minimal_spec` helper; this phase wires it into 47 call sites across 3 files.

**Prerequisite:** Phase 1 complete — `tests/fixtures/battle.py::make_minimal_spec` exists with 19 unit tests + 2 smoke integration tests passing.

**Scope boundary:** This phase does NOT delete the `BattleScreen.start()` shim or `_build_fallback_outcome` — Phase 3 does that after Phase 2 verifies zero callers remain.

---

## Canonical Migration Pattern

```python
# BEFORE:
self.scene.start([self.ship1], [self.ship2], headless=True)

# AFTER (controller path — for tests that need the full visual-mode lifecycle):
from tests.fixtures.battle import make_minimal_spec
from game.simulation.battle_controller import BattleController
from game.ai.ai_factory import AIControllerFactory

ships = [self.ship1, self.ship2]
spec = make_minimal_spec({0: [self.ship1], 1: [self.ship2]})

def _builder(ship_spec, team_id):
    _ = ship_spec
    return ships[team_id]

controller = BattleController()
controller.start_from_spec(spec, ai_factory=AIControllerFactory(), ship_builder=_builder)
self.scene.start_battle(controller)

# AFTER (headless path — simpler, for tests that only care about the outcome):
from game.simulation.battle_runner import run_battle
outcome = run_battle(spec, ai_factory=AIControllerFactory(), ship_builder=_builder)
```

**Recommendation:** Add a test-class-local helper method (`_start_minimal_battle(ship1, ship2, **kwargs)`) that wraps the boilerplate. With 47 callers, avoid repeating the builder closure.

---

## Tasks

### Task 2.1: Write a module-level migration helper [Simple]
**File:** `tests/fixtures/battle.py`
**Tests:** `pytest tests/fixtures/test_make_minimal_spec.py`

- [x] Decided: module-level helper (reduces per-call-site diff from ~8 lines to 1 line; worth it for 47 callers)
- [x] Added `start_battle_screen_with_minimal_spec(screen, ships_by_team, *, headless=False, start_paused=False, seed=0, max_ticks=1000) -> BattleController` to `tests/fixtures/battle.py`
- [x] Added 4 smoke tests in a new `TestStartBattleScreenWithMinimalSpec` class in `tests/fixtures/test_make_minimal_spec.py`: returns controller, screen has running controller, ships materialized via builder (identity preserved), single-ship-team works
- [x] 23 tests pass total (19 existing + 4 new)

**Notes:** Helper internally wires `make_minimal_spec` + `BattleController` + `ship_builder` + `BattleConfig`. Ship identity is preserved — the builder returns the exact ship objects passed in (in iteration order). This matters for tests that assert `ship in engine.ships` or depend on ship object identity post-start.

**Canonical Phase 2.2/2.3/2.4 migration pattern (using the new helper):**
```python
# BEFORE:
self.scene.start([self.ship1], [self.ship2], headless=True)

# AFTER:
from tests.fixtures.battle import start_battle_screen_with_minimal_spec

controller = start_battle_screen_with_minimal_spec(
    self.scene, {0: [self.ship1], 1: [self.ship2]}, headless=True,
)
# For tests that need the engine: engine = controller.service.get_engine()
# For tests that query scene.ships: that still works — screen.start_battle(controller) wires them
```

**Complication discovered in `test_battle_setup_logic.py`:** Some tests assert on `scene.ships`, `scene.ai_controllers`, `scene.projectiles` directly. Under the spec-based path, these live on the controller's engine. Tests querying these attributes need to change assertions to use `controller.service.get_engine()` or equivalent. `test_battle_scene_clear_state` specifically tests the shim's "calling start() twice clears state" contract — that test may need to be deleted or rewritten since the spec path uses a fresh controller per battle.

### Task 2.2: Migrate `tests/unit/ui/test_battle_screen.py` [Medium]
**File:** `tests/unit/ui/test_battle_screen.py` (7 callers at lines 57, 67, 83, 93, 117, 137, 149)
**Tests:** `pytest tests/unit/ui/test_battle_screen.py`

- [x] Read the full file first — understand each test's intent and what assertions depend on post-`.start()` state
- [x] Add any required imports (`start_battle_screen_with_minimal_spec`)
- [x] Replace each `self.scene.start([...], [...], headless=...)` call using the canonical pattern from Task 2.1
- [x] For `headless=True` callers: kept the controller path (helper) — simpler and more consistent than splitting into `run_battle(spec, ...)`
- [x] Run `pytest tests/unit/ui/test_battle_screen.py` — all 7 pass
- [x] Grep the file for any remaining `.start(` calls against a BattleScreen instance — zero

**Notes:** `scene.ships`/`scene.ai_controllers`/`scene.projectiles` are already delegating properties on BattleScreen that go through `self.engine.*` — when `start_battle(controller)` swaps `self._battle_service` to `controller.service`, those assertions work transparently. No assertion reshape required. Discovered that `make_minimal_spec`'s default `TickLimitCondition(max_ticks=1000)` broke `test_battle_over_condition` (which relies on team-elimination semantics to signal battle-over). Fixed by overriding the spec's `end_condition` to `TeamEliminatedCondition()` inside `start_battle_screen_with_minimal_spec` — matches the legacy shim's default, keeps `max_ticks` as safety ceiling via `absolute_max_ticks`. `make_minimal_spec` itself is unchanged (still returns `TickLimitCondition` per its Phase 1 contract).

### Task 2.3: Migrate `tests/unit/ui/test_battle_screen_simulation.py` [Complex]
**File:** `tests/unit/ui/test_battle_screen_simulation.py` (37 callers — bulk of the work)
**Tests:** `pytest tests/unit/ui/test_battle_screen_simulation.py`

- [x] Read the full file — this is the heaviest migration file
- [x] Identified repeated patterns; used 5 `replace_all` edits covering all variants (2-team headless=True/False, team0=[ship1,ship3], single-with-ship3-param, start_paused=True)
- [x] Migrated all 35 remaining call sites (2 shim-specific tests deleted instead — see notes)
- [x] Used `scene.ships` etc. via engine properties (no reshape needed) and `start_paused=True` passed through the helper's kwarg
- [x] Run `pytest tests/unit/ui/test_battle_screen_simulation.py` — all 37 tests pass
- [x] Grep verify zero remaining `.start([` calls

**Notes:** Deleted two shim-specific tests that exist only to validate the shim's internals and cannot survive shim deletion in Phase 3:
- `test_start_with_empty_ship_lists` (lines 65–71 pre-deletion) — asserts `ships==0`, `sim_tick_counter==0`, `sim_paused is False` from an empty-list `start([], [])`. All three assertions describe the BattleScreen's initial state, which exists without calling `start()`. Purely a shim-behavior test.
- `test_start_constructs_controller_inline` (lines 114–130 pre-deletion) — patches `BattleController` inside `battle_screen` module and asserts the shim constructs it + calls `start_battle`. Tests the shim's implementation directly; no reason to exist after Phase 3 deletes the shim.

File went from 37 callers → 35 migrated callers + 2 deleted tests = 35 now in force.

### Task 2.4: Migrate `tests/unit/ui/screens/test_battle_setup_logic.py` [Simple]
**File:** `tests/unit/ui/screens/test_battle_setup_logic.py` (3 callers at lines 78, 100, 104)
**Tests:** `pytest tests/unit/ui/screens/test_battle_setup_logic.py`

- [x] Read the full file
- [x] Migrate 3 callers using the canonical pattern
- [x] Run `pytest tests/unit/ui/screens/test_battle_setup_logic.py` — all 3 pass
- [x] Grep verify zero remaining callers

**Notes:** Lines 100, 104 pass `[ship, []]` (team 1 empty). Migrated as `{0: [ship], 1: []}` — `make_minimal_spec` accepts empty ship lists (empty `SquadronSpec.ships=()`), `engine.start_teams` handles empty team lists (no-op loop), and `TeamEliminatedCondition` returns False while ships remain on ≥2 teams. All 3 tests pass without filtering empty teams. `test_battle_scene_clear_state` (double-start) works naturally because each helper call installs a fresh controller and `start_battle(controller)` swaps `self._battle_service` to the new controller's service.

### Task 2.5: Repo-wide grep verification [Simple]
**File:** N/A
**Tests:** Full PROJ-281 scope regression

- [x] Grep `scene\.start(\[` + `screen\.start(\[` across entire repo — zero hits in production/test code (only matches are docstring examples in `tests/fixtures/battle.py` and the historical PROJ-281 plan docs)
- [x] `BattleScreen.start(team0` matches remain in: the method definition in `game/ui/screens/battle_screen.py`, Phase 3 guard test `tests/unit/simulation/test_unified_entry_guard.py:565`, PROJ-281 planning docs, and archived PROJ-270/272 findings — none are callers
- [x] `pytest tests/unit/ui/test_battle_screen.py tests/unit/ui/test_battle_screen_simulation.py tests/unit/ui/screens/test_battle_setup_logic.py tests/fixtures/test_make_minimal_spec.py tests/integration/test_make_minimal_spec_smoke.py` — 72 passed
- [x] Affected-scope regression: `pytest tests/unit/ui/ tests/unit/test_lab/ tests/unit/combat_lab/ tests/fixtures/ tests/integration/` — 4687 passed, 2 skipped
- [x] Combat Lab simulation: 162 passed, 0 failed

**Notes:** Phase 2 complete. 47 migrations → 45 call-site replacements + 2 test deletions (shim-specific tests that cannot survive Phase 3). One helper enhancement (TeamEliminatedCondition override) kept `make_minimal_spec`'s Phase 1 contract intact.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] All 47 call sites migrated (45 replaced + 2 shim-specific tests deleted)
- [x] `pytest tests/unit/ui/test_battle_screen.py tests/unit/ui/test_battle_screen_simulation.py tests/unit/ui/screens/test_battle_setup_logic.py` — all pass (7 + 37 + 3 = 47)
- [x] Grep returns zero production/test callers of `BattleScreen.start(team0, team1)` — only the method definition itself, the Phase 3 guard test, and historical planning docs remain
- [x] Combat Lab simulation: 162 passed
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to Phase 3 (delete the shim)
