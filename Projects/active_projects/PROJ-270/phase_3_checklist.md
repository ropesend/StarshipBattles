# Phase 3: Battle Setup Spec Migration

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Risk:** MEDIUM
**Depends On:** Phase 1 (can parallel with Phase 2)
**Objective:** Migrate the Battle Setup production path through `build_manual_battle_spec`. Currently `app.py::start_battle` (line 543) inlines a `BattleController` setup using raw ship lists — the Battle Setup spec compiler exists but has zero production callers. After Phase 3, clicking "Start" in the Battle Setup screen compiles a `BattleSpec`, which is then handed to `BattleController` (which still drives the per-frame tick loop until Phase 4's outcome refactor).

---

## Tasks

### Task 3.1: Failing-test driven spec-flow for Battle Setup [Medium]
**File:** `tests/unit/ui/screens/test_battle_setup_spec_flow.py` (new)
**Tests:** `pytest tests/unit/ui/screens/test_battle_setup_spec_flow.py --tb=short`

- [ ] Write failing test asserting:
  - Clicking "Start" in a Battle Setup screen with 2 teams of ships produces a call to `build_manual_battle_spec` with the right ships, boundary, and complex-toggle modifiers
  - The resulting spec has `len(spec.teams) == 2` with the correct ship counts per team
  - `spec.modifier_stack` contains entries for each toggled complex
  - `spec.boundary` reflects the Battle Setup screen's boundary selection (or `None` if unbounded)
- [ ] Run test — confirm it fails (app.py::start_battle doesn't call `build_manual_battle_spec`)

**Notes:** [Filled during implementation]

---

### Task 3.2: Migrate `app.py::start_battle` through `build_manual_battle_spec` [Medium]
**File:** `game/app.py`
**Tests:** `pytest tests/unit/ui/screens/test_battle_setup_spec_flow.py --tb=short`

- [ ] Import `build_manual_battle_spec` in [game/app.py](../../../game/app.py)
- [ ] Rewrite `start_battle(team0_ships, team1_ships, headless=False, end_condition=None)` at [game/app.py:543-572](../../../game/app.py#L543-L572):
  - Before constructing `BattleController`, compile a `BattleSpec`:
    ```python
    spec = build_manual_battle_spec(
        team_ships={0: team0_ships, 1: team1_ships},
        boundary=self.battle_setup.get_boundary(),
        modifier_sources=self.battle_setup.get_modifier_sources(),
        seed=self.battle_setup.get_seed(),
        end_condition=end_condition,
    )
    ```
  - Pass the spec to `BattleController.configure(config, spec=spec)` (signature change — coordinated with Phase 4 or done in a backwards-compat way here)
  - Remove inline `controller.add_ships(team0_ships, 0)` + `controller.add_ships(team1_ships, 1)` — the spec now carries the ships
- [ ] Update the inline docstring — remove the "Task 6.9 defers…" forward-reference (currently lines 546–551)
- [ ] Verify caller `FleetBattleSetupScreen._start_battle` still supplies the right inputs
- [ ] Run test from Task 3.1 — confirm it passes
- [ ] Run `pytest tests/unit/ui/ --testmon` — green
- [ ] Manual smoke (interactive): launch game, go to Battle Setup, start a 2v2 battle — no crash

**Notes:** [Filled during implementation]

---

### Task 3.3: Clean up `_sync_complex_toggles_to_state` indirection [Medium]
**File:** `game/ui/screens/battle_setup_screen.py`
**Tests:** `pytest tests/unit/ui/screens/` --tb=short`

- [ ] Currently `FleetBattleSetupScreen._sync_complex_toggles_to_state` (line 1121) projects UI toggles onto `BattleSetupSide.system_complexes` / `sector_complexes` lists, then `build_manual_battle_spec` reads those lists. This indirection exists because `build_manual_battle_spec` wasn't being called live (Phase 3.2 fixes that).
- [ ] Option A (simpler): delete `_sync_complex_toggles_to_state`; have `_start_battle` pass the toggle dict directly to `build_manual_battle_spec` as a kwarg
- [ ] Option B (more compatible): keep `_sync_complex_toggles_to_state` but ensure its call happens exactly once (currently at line 1033 inside `_start_battle`)
- [ ] Pick one — document in Notes. Default recommendation: Option A (simpler, no hidden state)
- [ ] Write failing test asserting toggled complexes end up as `ModifierEntry` in the resulting spec
- [ ] Implement
- [ ] Verify: 2v2 with toggled complex produces spec with right entries (test) + doesn't crash (manual smoke)

**Notes:** [Filled during implementation]

---

### Task 3.4: Audit `build_manual_battle_spec` signature + kwargs [Simple]
**File:** `game/ui/screens/battle_setup/spec_compiler.py`
**Tests:** `pytest tests/unit/ui/screens/battle_setup/test_spec_compiler.py --tb=short`

- [ ] Read [game/ui/screens/battle_setup/spec_compiler.py](../../../game/ui/screens/battle_setup/spec_compiler.py) — note current signature
- [ ] Confirm it accepts the kwargs Task 3.2 passes (team_ships, boundary, modifier_sources, seed, end_condition). If not, extend the compiler signature
- [ ] Write failing test asserting the new kwargs are honoured
- [ ] Implement kwargs if needed
- [ ] Run test — passes
- [ ] Run existing `test_spec_compiler.py` — still green

**Notes:** [Filled during implementation]

---

### Task 3.5: Phase 3 regression gate [Simple]
**Tests:** Full suites

- [ ] `pytest tests/ --tb=no -q` — ≥ baseline
- [ ] `python -m combat_lab.run_tests --fast --no-history` — 162/162 green
- [ ] `pytest tests/unit/ui/ --testmon` — green
- [ ] Grep audit: `build_manual_battle_spec` has at least one live production caller (via `app.py::start_battle`)
- [ ] Manual smoke (interactive): Battle Setup 2v2 with toggled complex — battle starts, complex modifier appears in the forensic trace via `engine.modifier_stack`

**Notes:** [Filled during implementation]

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Tests for Tasks 3.1, 3.3, 3.4 passing
- [ ] Regression gate (Task 3.5) passed
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next active phase
