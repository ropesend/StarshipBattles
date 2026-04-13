# Phase 11: Test + Doc Hardening

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-270 11`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Risk:** LOW (tests + docs; no production behavior changes)
**Depends On:** Phases 9 + 10 (the contract has to be real before hardening the guards)
**Objective:** Convert the paraphrase-gameable regex regression guards into AST/behavioral tests, widen scope to all of `game/`, add real content assertions, write end-to-end integration tests for all 3 spec compilers, and fix the documentation drift that still teaches the deleted `setup(battle_engine)` API.

## Context (from skeptic audit)

- `TestNoLegacyCompatibleComments` regex is `Legacy-compatible|retained for` — trivially defeated by paraphrase. Scope missing `game/strategy`, `game/ai`, `game/core`.
- `TestNoLegacyScenarioSetup` regex requires literal param name `battle_engine` — a rename to `engine` bypasses the guard.
- Acceptance criterion (e) guard missing `deprecated` — 17 live files have DEPRECATED markers; `battle_screen.py:116-118` has "Legacy state — kept for backward compat" that the guard misses.
- `test_outcome_emission.py` asserts `controller.get_outcome() is mock_outcome` — never checks `.teams`, `.end_reason`, `.duration_ticks`. A `BattleOutcome(teams=())` regression would pass every test.
- `TestNoPlaceholderStatKeyInStrategyCompiler` is a source-text regex scan, not a behavioral test of the compiler function.
- **Doc drift Critical:** `docs/guides/simulation_testing.md:167-174` shows `def setup(self, battle_engine):` as canonical — the exact API Phase 1.3 deleted. No historical banner.
- **Doc drift High:** `combat_lab/COMBAT_LAB_DOCUMENTATION.md:283-289` base-class section still lists `def setup(self, battle_engine): raise NotImplementedError`.
- **Doc drift Medium:** `docs/01_ARCHITECTURE.md:375-378` and `docs/systems/combat_simulation.md:319` describe the old `controller.set_spec(spec)` two-step flow instead of `configure(config, spec=spec)`.
- `tests/integration/simulation/test_simulation_adapter_storms.py` — referenced in plan but does not exist.
- CircleBoundary "pick +x direction at origin" convention documented in code but not tested.
- `build_manual_battle_spec` and `build_test_battle_spec` have no end-to-end integration tests (only `build_strategy_battle_spec` does).

---

## Tasks

### Task 11.1: Strengthen assertions in `test_outcome_emission.py` [Medium]
**File:** `tests/unit/simulation/battle_controller/test_outcome_emission.py`

- [ ] Add real-content assertion test: use a minimal real spec (1 ship per team), drive `BattleController` through a short battle, assert:
  - `outcome.teams` is non-empty
  - Each `ShipOutcome.status` is a valid `ShipStatus` enum value (not None)
  - `outcome.duration_ticks > 0`
  - `outcome.end_reason` is a real `EndReason`
- [ ] Keep the existing mock-based tests (they still have plumbing value) but add the real-content test alongside
- [ ] Verify: a synthesized `BattleOutcome(teams=())` would now fail the new test

---

### Task 11.2: AST-based rewrite of `TestNoLegacyScenarioSetup` [Medium]
**File:** `tests/unit/simulation/test_unified_entry_guard.py`

- [ ] Replace regex `^\s*def\s+setup\s*\(\s*self\s*,\s*battle_engine\b` with AST walker that finds ANY `def setup(self, *)` on classes under `combat_lab/scenarios/`
- [ ] Run — should still be green (no `setup` methods exist)
- [ ] Verify: renaming `battle_engine` to `engine` in a test shim would now trip the guard (it wouldn't before)

Alternative: delete the redundant guard entirely and rely on `test_template_no_legacy_setup.py::*::test_*_has_no_setup` which uses `hasattr(Class, 'setup')` — that's already robust.

---

### Task 11.3: Expand `TestNoLegacyCompatibleComments` scope + pattern [Medium]
**File:** `tests/unit/simulation/test_unified_entry_guard.py:119-133`

- [ ] Broaden regex to `(?i)(legacy[-\s]?(compat|shim|state)|retained (for|while)|backward[-\s]?compat(ibility)?|deprecated[-\s]?but|kept for (transition|backward|legacy))`
- [ ] Expand scope to all of `game/` + `combat_lab/` (currently only `game/simulation`, `game/ui`, `combat_lab`)
- [ ] Run guard — identify hit list
- [ ] Triage each hit: either delete the compat marker (preferred) OR add explicit inline allow-marker (e.g. `# NOQA: legacy-retained — intentional for PROJ-X`) with a filed ticket
- [ ] Known hits from skeptic: `game/ui/screens/battle_screen.py:116-118` "Legacy state — kept as instance vars for backward compatibility", `game/simulation/components/ability_manager.py:286` "DEPRECATED static methods (kept for transition)", `game/simulation/components/modifier_manager.py:221`, and others

---

### Task 11.4: Behavioral test for strategy compiler stat_keys [Simple]
**File:** `tests/unit/simulation/test_unified_entry_guard.py::TestNoPlaceholderStatKeyInStrategyCompiler`

- [ ] Replace text-regex scan of `spec_compiler.py` with a behavioral test: call `_entries_from_fleet_combat_modifiers(FleetCombatModifiers(shield_mult=0.5, damage_mult=0.5, ...))` and assert `entry.effect.stat_key` equals the expected real enum value (`StatKey.SHIELD_CAPACITY_MULT`, etc.)
- [ ] Similarly for `_entries_from_environmental_effects`
- [ ] Behavioral test survives reformatting / renaming that a regex wouldn't

---

### Task 11.5: End-to-end compiler integration tests [Medium]
**File:** `tests/integration/simulation/test_entry_points_emit_outcome.py` (new)

- [ ] Write integration test: for each of the 3 production compilers (`build_test_battle_spec`, `build_manual_battle_spec`, `build_strategy_battle_spec`), build a minimal real spec, call `run_battle(spec)`, assert the resulting `BattleOutcome` has populated teams, non-zero duration, and a real end_reason
- [ ] Currently only `build_strategy_battle_spec` has this coverage (via `test_damage_persistence.py`)

---

### Task 11.6: Visual-mode end-to-end integration test (Task 4.1 re-opened) [Medium]
**File:** `tests/integration/ui/test_visual_battle_outcome.py` (new)

- [ ] Write integration test that drives a real `BattleController` through a real `BattleEngine` via `configure(config, spec=spec)` + per-frame `update()` loop until `is_battle_over()`
- [ ] Assert `controller.get_outcome()` returns a real (non-mocked, non-synthesized) `BattleOutcome`
- [ ] If `BattleScreen._build_fallback_outcome` survives Phase 10 deletion, assert this test's outcome is NOT a fallback (check a distinguishing field like `seed != 0` if production tests always set seed)

---

### Task 11.7: Boundary origin-ambiguity tests [Simple]
**File:** `tests/unit/simulation/combat/test_boundary.py`

- [ ] Add `test_circle_boundary_closest_edge_point_at_origin_returns_plus_x` locking the documented "+x convention"
- [ ] Add `test_rect_boundary_closest_edge_point_at_origin_deterministic` locking the chosen direction when all 4 edges are equidistant (document + test the chosen convention)

---

### Task 11.8: Fix critical doc drift — `simulation_testing.md` [Medium]
**File:** `docs/guides/simulation_testing.md:167-174`

- [ ] Delete the `def setup(self, battle_engine):` + `def update(self, battle_engine):` canonical-pattern section
- [ ] Replace with current `TestScenario` API: `to_spec(registries)` → `wire_ships(ships_by_role, engine, initial_state)` → `custom_setup(...)` (if applicable) → `validate(outcome, telemetry)`
- [ ] Cross-link to an authoritative example scenario file
- [ ] Check: any other spots in the file that teach deleted APIs? Fix them.

---

### Task 11.9: Fix `combat_lab/COMBAT_LAB_DOCUMENTATION.md` base-class drift [Simple]
**File:** `combat_lab/COMBAT_LAB_DOCUMENTATION.md:283-289`

- [ ] Update the base-class snippet to match current `TestScenario` (no `setup(battle_engine)`)
- [ ] OR delete the snippet and reference `docs/systems/combat_simulation.md`

---

### Task 11.10: Fix `docs/01_ARCHITECTURE.md` + `docs/systems/combat_simulation.md` API drift [Simple]
**File:** `docs/01_ARCHITECTURE.md:375-378`, `docs/systems/combat_simulation.md:319`

- [ ] Update both sections to describe `controller.configure(config, spec=spec)` as the primary visual-mode entry
- [ ] Note `set_spec(spec)` as internal-only (or remove if Phase 10 deleted it)

---

### Task 11.11: Misc doc cleanup [Low]

- [ ] Remove the reference to nonexistent `tests/integration/simulation/test_simulation_adapter_storms.py` from any plan/doc that mentions it
- [ ] `docs/README.md` "23 design patterns" — either make dynamic or remove the count

---

### Task 11.12: Phase 11 regression gate
**Tests:** Full suites

- [ ] `pytest tests/ --tb=no -q` — ≥ baseline + new Phase 11 tests
- [ ] Combat Lab fast + full green
- [ ] All new regression guards + AST-based guards green
- [ ] Manual doc review: no live `def setup(self, battle_engine)` in user-facing docs

---

## Phase Completion Checklist

- [ ] All task checkboxes above are checked
- [ ] Regression guards are AST-based / behavioral where feasible (not just regex)
- [ ] `test_outcome_emission.py` has real-content assertions
- [ ] 3 spec compilers have end-to-end integration tests
- [ ] User-facing docs describe current APIs, not deleted ones
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
