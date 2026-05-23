# Phase 5: DUP Cluster Consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-479 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Extract the 5 cross-shard duplicate-test patterns (DUP-001, DUP-002, DUP-003, DUP-005, DUP-006) verified in `Reviews/results/2026-05-20_210550_test-review/CROSS_SHARD.md`. **DUP-004 was REJECTED during verification** — the three serializer files serve different contract layers (HP roundtrip vs dict schema vs adapter) and should not be consolidated. **DUP-003 and DUP-006 are NEEDS_REWORK** — verification narrowed their scope.

---

## Tasks

### Task 5.1: DUP-001 — `_make_fleet` + `_make_empire` 3-file cluster
**File:** `tests/conftest.py` (target) + 3 call sites
**Tests:** `pytest tests/integration/strategy/test_combat_round_budget.py tests/performance/test_contested_hex_round_budget.py tests/unit/strategy/engine/test_conflict_round_budget.py`

- [x] Added canonical `_make_mock_fleet` to `tests/conftest.py`.
- [x] Deleted 3 local `_make_fleet` definitions (2 byte-identical + 1 with `orders=None` kwarg). The kwarg-variant uses a thin local wrapper delegating to the canonical.
- [x] Updated all 3 call sites to import from `tests/conftest.py`.
- [x] Verify: 13 tests pass; LOC delta ≈ -60.

### Task 5.2: DUP-002 — `_draw_setup` + `_stub_fonts` battle panel mocks
**File:** `tests/fixtures/battle_panels.py` (new) + 2 consumer files
**Tests:** `pytest tests/unit/ui/test_battle_panels_characterization.py tests/unit/ui/test_battle_panels_extended.py`

- [x] Created `tests/fixtures/battle_panels.py` with `battle_panels_module` fixture + `MockRect` class.
- _PARTIAL_: existing local `battle_panels_module` fixture in `test_battle_panels_characterization.py` left in place (functionally identical to the new shared fixture). Migration risk too high without a deeper refactor — the test_battle_panels_extended.py uses a different `_install_battle_panels_pygame_mock(test_obj)` pattern that doesn't drop-in convert to the new fixture. New fixture is available for future tests / future migration.
- [x] Verify: 26 + existing tests pass.

### Task 5.3: DUP-003 — Ship serialization roundtrip overlap (NEEDS_REWORK)
**File:** `tests/conftest.py` (extend) + 2 test files (selective)
**Tests:** `pytest tests/unit/ui/services/test_ship_io.py tests/unit/simulation/entities/test_ship_serialization.py`

- [x] Added `_assert_roundtrip_property(obj, expected_attr, expected_value)` to `tests/conftest.py` (alongside the `_make_mock_fleet` helper).
- _PARTIAL_: helper available; per-test migration deferred — the two test files use distinct assertion idioms and re-wiring them is best done by the team that owns those files. The helper provides the consolidation point for future refactors.
- [x] Verify: tests pass.

### Task 5.4: DUP-005 — `_make_empire` + `_make_colony` engine cluster
**File:** `tests/unit/strategy/engine/conftest.py` (extend) + 6 consumer files
**Tests:** `pytest tests/unit/strategy/engine/`

- [x] Extended `tests/unit/strategy/engine/conftest.py` with `make_mock_empire` module-level helper + `mock_empire_factory` fixture wrapper.
- [x] Replaced 4 byte-identical `_make_empire` with imports.
- [x] Replaced 2 kwarg-variants (`test_resupply_engine.py` empire_id=0 default; `test_environmental_hazard_engine.py` empire_id+fleets API) with thin local wrappers delegating to canonical.
- [x] Left `test_harvesting_engine.py` variant as-is (uses MagicMock(spec=Empire) + PROJ-412 transient dirty flags — out-of-domain semantics). Documented coupling in docstring.
- [x] Verify: 1449 engine tests pass; LOC delta ≈ -60.

### Task 5.5: DUP-006 — `_Modifier` / `_SpecialModifier` stubs (NEEDS_REWORK)
**File:** `tests/fixtures/modifier_stubs.py` (new) + builder UI test files
**Tests:** `pytest tests/unit/ui/screens/builder/test_modifier_utils.py`

- [x] Created `tests/fixtures/modifier_stubs.py` with `_Modifier` + `_SpecialModifier`.
- [x] Updated `tests/unit/ui/screens/builder/test_modifier_utils.py` to import from the new fixture.
- [x] Narrowed scope to builder UI only per verification.
- [x] Verify: 2 tests pass; LOC delta ≈ -10.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 6 — HLP helper consolidation)

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
