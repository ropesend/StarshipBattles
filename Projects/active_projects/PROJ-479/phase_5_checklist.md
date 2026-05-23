# Phase 5: DUP Cluster Consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-479 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Extract the 5 cross-shard duplicate-test patterns (DUP-001, DUP-002, DUP-003, DUP-005, DUP-006) verified in `Reviews/results/2026-05-20_210550_test-review/CROSS_SHARD.md`. **DUP-004 was REJECTED during verification** — the three serializer files serve different contract layers (HP roundtrip vs dict schema vs adapter) and should not be consolidated. **DUP-003 and DUP-006 are NEEDS_REWORK** — verification narrowed their scope.

---

## Tasks

### Task 5.1: DUP-001 — `_make_fleet` + `_make_empire` 3-file cluster
**File:** `tests/conftest.py` (target) + 3 call sites
**Tests:** `pytest tests/integration/strategy/test_combat_round_budget.py tests/performance/test_contested_hex_round_budget.py tests/unit/strategy/engine/test_conflict_round_budget.py`

- [ ] Add a canonical `_make_mock_fleet(fleet_id, owner_id, location, speed, **overrides)` to `tests/conftest.py` (extends existing `make_mock_ship_instance` helper per PROJ-40). Accept 6 core MagicMock fields (id, owner_id, location, speed, ships, task_forces, orders) plus kwargs override.
- [ ] Delete the 3 byte-identical local `_make_fleet` definitions:
  - `tests/integration/strategy/test_combat_round_budget.py:75-91`
  - `tests/performance/test_contested_hex_round_budget.py:60-76`
  - `tests/unit/strategy/engine/test_conflict_round_budget.py:35-51`
- [ ] Update the 3 call sites to import from `tests/conftest.py`.
- [ ] Verify: all 3 test files pass; LOC delta ≈ -60.

### Task 5.2: DUP-002 — `_draw_setup` + `_stub_fonts` battle panel mocks
**File:** `tests/fixtures/battle_panels.py` (new) + 2 consumer files
**Tests:** `pytest tests/unit/ui/test_battle_panels_characterization.py tests/unit/ui/test_battle_panels_extended.py`

- [ ] Create `tests/fixtures/battle_panels.py` with a `battle_panels_mock` pytest fixture providing pre-mocked `pygame.Rect`, `K_LSHIFT`, `SRCALPHA`, and `pygame` module surface.
- [ ] Update `tests/unit/ui/test_battle_panels_characterization.py:419-433` to import the fixture instead of defining `_draw_setup` + `_stub_fonts` locally.
- [ ] Update `tests/unit/ui/test_battle_panels_extended.py:36-69` to use the same fixture instead of `_install_battle_panels_pygame_mock`.
- [ ] _(Note: `test_battle_panels_extended.py:474-520` also has an inline duplicate of its own helper — fix as part of the same task per S14-F010 finding.)_
- [ ] Verify: both test files pass; LOC delta ≈ -70.

### Task 5.3: DUP-003 — Ship serialization roundtrip overlap (NEEDS_REWORK)
**File:** `tests/conftest.py` (extend) + 2 test files (selective)
**Tests:** `pytest tests/unit/ui/services/test_ship_io.py tests/unit/simulation/entities/test_ship_serialization.py`

- [ ] Add `_assert_roundtrip_property(obj, expected_attr, expected_value)` helper to `tests/conftest.py`.
- [ ] Refactor the 4 overlapping property assertions in:
  - `tests/unit/ui/services/test_ship_io.py:395-430`
  - `tests/unit/simulation/entities/test_ship_serialization.py:328-369`
  Use the shared helper for the overlapping properties (name, class, team_id, color).
- [ ] **Keep both files** — they serve different layers (IO with tmp_path vs pure entity). Full consolidation would lose layer separation. _(verification adjusted from review's full-consolidation suggestion. See verification_report.md.)_
- [ ] Verify: both test files pass; LOC delta ≈ -20 (not 80 as originally claimed).

### Task 5.4: DUP-005 — `_make_empire` + `_make_colony` engine cluster
**File:** `tests/unit/strategy/engine/conftest.py` (extend) + 6 consumer files
**Tests:** `pytest tests/unit/strategy/engine/`

- [ ] Extend `tests/unit/strategy/engine/conftest.py` (currently has only `economy_calculator` at line 13) with `mock_empire_factory` and `mock_colony_factory` fixtures matching the 6 identical local definitions.
- [ ] Delete local `_make_empire(colonies=None)` from the 6 files:
  - `test_planet_action_engine.py:91`
  - `test_harvesting_engine.py:27` (extended variant — pass extra kwargs)
  - `test_planet_energy_engine.py:64`
  - `test_resupply_engine.py:95`
  - `test_component_activation_engine.py:41`
  - `test_environmental_hazard_engine.py:61`
- [ ] Update all 6 to use the fixture. The extended variant in `test_harvesting_engine.py` needs `resource_pool` / `max_storage` kwargs.
- [ ] Verify: `pytest tests/unit/strategy/engine/` passes; LOC delta ≈ -90.

### Task 5.5: DUP-006 — `_Modifier` / `_SpecialModifier` stubs (NEEDS_REWORK)
**File:** `tests/fixtures/modifier_stubs.py` (new) + builder UI test files
**Tests:** `pytest tests/unit/ui/screens/builder/test_modifier_utils.py`

- [ ] Create `tests/fixtures/modifier_stubs.py` with `_Modifier` and `_SpecialModifier` stub classes.
- [ ] Update `tests/unit/ui/screens/builder/test_modifier_utils.py:10-17` to import the stubs.
- [ ] **Narrow scope** to builder UI files only. _(verification adjusted from review's claim of "3+ files in Shard 07 alone + Shard 02" — `test_workshop_viewmodel_selection.py` uses `_Component` not Modifier stubs; `test_propulsion_ability_bindings.py` uses inline `MockComponent` for STAT_BINDINGS testing in a different domain. Don't force unrelated files into this consolidation. See verification_report.md.)_
- [ ] Verify: builder UI test files pass; LOC delta ≈ -15 (not 40 as originally claimed).

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 6 — HLP helper consolidation)

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
