# Phase 2: Migrate 47 test callers off `BattleScreen.start(team0, team1)`

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-281 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
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

### Task 2.1: Write a test-local migration helper (or extend the module-level helper) [Simple]
**File:** Decide during task — either inline per-file helpers, or extend `tests/fixtures/battle.py` with a higher-level helper
**Tests:** `pytest tests/fixtures/`

- [ ] Decide: module-level helper in `tests/fixtures/battle.py` (e.g. `start_minimal_battle_on_screen(screen, ships_by_team, **kwargs)`) OR test-class-local helpers per file
- [ ] If module-level: add it to `tests/fixtures/battle.py`, add 2-3 smoke tests
- [ ] If per-file: note the pattern in this checklist so the 3 file migrations stay consistent

**Notes:** A module-level helper that encapsulates the `make_minimal_spec + controller + ship_builder` dance would reduce the Phase 2 diff significantly. Consider a helper signature like:
```python
def start_minimal_battle_on_screen(
    screen, *, team0_ships, team1_ships, headless=False, seed=None, **spec_kwargs
) -> BattleController:
    ...
```

### Task 2.2: Migrate `tests/unit/ui/test_battle_screen.py` [Medium]
**File:** `tests/unit/ui/test_battle_screen.py` (7 callers at lines 57, 67, 83, 93, 117, 137, 149)
**Tests:** `pytest tests/unit/ui/test_battle_screen.py`

- [ ] Read the full file first — understand each test's intent and what assertions depend on post-`.start()` state
- [ ] Add any required imports (`make_minimal_spec`, `BattleController`, `AIControllerFactory`)
- [ ] Replace each `self.scene.start([...], [...], headless=...)` call using the canonical pattern from Task 2.1
- [ ] For `headless=True` callers: consider switching to `run_battle(spec, ...)` directly
- [ ] Run `pytest tests/unit/ui/test_battle_screen.py` — verify all pass
- [ ] Grep the file for any remaining `.start(` calls against a BattleScreen instance — should be zero

**Notes:**

### Task 2.3: Migrate `tests/unit/ui/test_battle_screen_simulation.py` [Complex]
**File:** `tests/unit/ui/test_battle_screen_simulation.py` (37 callers — bulk of the work)
**Tests:** `pytest tests/unit/ui/test_battle_screen_simulation.py`

- [ ] Read the full file — this is the heaviest migration file
- [ ] Identify repeated patterns; consider a fixture or class-level `_start` helper to reduce diff size
- [ ] Migrate the 37 call sites in batches (suggested: 10 at a time, run tests after each batch)
- [ ] Watch for tests that depend on engine state after `.start()` — `scene.engine` may not be available through the controller path; use `controller.service.get_engine()` if needed
- [ ] Watch for tests that use `start_paused=True` — `BattleConfig(start_paused=True)` in the controller config
- [ ] Run `pytest tests/unit/ui/test_battle_screen_simulation.py` after each batch; all pass by task end
- [ ] Grep verify zero remaining `.start([` calls

**Notes:**

### Task 2.4: Migrate `tests/unit/ui/screens/test_battle_setup_logic.py` [Simple]
**File:** `tests/unit/ui/screens/test_battle_setup_logic.py` (3 callers at lines 78, 100, 104)
**Tests:** `pytest tests/unit/ui/screens/test_battle_setup_logic.py`

- [ ] Read the full file
- [ ] Migrate 3 callers using the canonical pattern
- [ ] Run `pytest tests/unit/ui/screens/test_battle_setup_logic.py` — all pass
- [ ] Grep verify zero remaining callers

**Notes:** Note line 100 and 104 use `[ship, []]` (one team empty). The spec helper accepts `{0: [ship1], 1: []}` — verify empty-team handling still works, or filter empty teams out before calling `make_minimal_spec`.

### Task 2.5: Repo-wide grep verification [Simple]
**File:** N/A
**Tests:** Full PROJ-281 scope regression

- [ ] Grep `screen\.start(\[`, `scene\.start(\[`, `BattleScreen.*\.start(\[` across entire repo — zero hits in production/test code
- [ ] Grep `BattleScreen.start(` should only return the method definition in `game/ui/screens/battle_screen.py` and historical project docs
- [ ] `pytest tests/unit/ui/ tests/unit/ui/screens/` — all pass
- [ ] Combat Lab simulation suite still clean: `python -m combat_lab.run_tests --fast`

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] All 47 call sites migrated to the spec-based path
- [ ] `pytest tests/unit/ui/test_battle_screen.py tests/unit/ui/test_battle_screen_simulation.py tests/unit/ui/screens/test_battle_setup_logic.py` — all pass
- [ ] Grep returns zero production/test callers of `BattleScreen.start(team0, team1)` — only the method definition itself remains
- [ ] Combat Lab simulation: 162 passed
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 3 (delete the shim)
