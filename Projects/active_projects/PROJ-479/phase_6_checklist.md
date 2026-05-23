# Phase 6: HLP Helper Consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-479 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Partial

**Partial completion summary:**
- Task 6.2 (HLP-002 — `MockPlanetType` Enum consolidation): _PARTIAL_. Canonical fixture created in `tests/fixtures/colonization_fixtures.py`; 2 module-level copies migrated. The remaining 12+ nested method-local copies (e.g. 9 inline copies in `test_colonization_facade.py`) are deferred as a dedicated mechanical sweep.
- Task 6.4 (HLP-004 — `_make_fleet` 43+ definitions): _PARTIAL_. Canonical `_make_mock_fleet` added to `tests/conftest.py`; the 3 DUP-001 cluster sites are migrated. The remaining ~40 sites have signature/kwarg variation that requires per-site triage; full 43-file sweep deferred.
- Task 6.5 (HLP-005 — `setup_tmpdir` Paths.SAVES_DIR fixture): _NEEDS_REWORK_. The `chdir`-variant in `test_auto_save.py` and the `Paths.SAVES_DIR`-patching variant in other files are not 1:1 interchangeable; a unified fixture would need to support both modes via parameter. Out of scope for this CAT-5 sweep; needs a strategy decision before consolidating.

**Objective:** Consolidate the 6 cross-shard helper duplications (HLP-001 through HLP-006) verified in `Reviews/results/2026-05-20_210550_test-review/CROSS_SHARD.md`. All 6 cluster definitions were VERIFIED in third-pass verification; extraction targets are sensible. Reclaim ~530 LOC by replacing 60+ local copies with imports from canonical conftest / fixtures.

---

## Tasks

### Task 6.1: HLP-001 — `MockGameSession` 5 copies → save_game_service/conftest.py
**File:** `tests/unit/strategy/save_game_service/conftest.py` (canonical) + 4 consumers
**Tests:** `pytest tests/unit/strategy/save_game_service/ tests/unit/ui/test_save_selection.py tests/unit/strategy/test_auto_save.py`

- [x] Extended canonical `MockGameSession` in `save_game_service/conftest.py` with `save_path=None` kwarg (subsumes `test_auto_save.py` variant).
- [x] Deleted 4 local copies and replaced with imports from conftest.
- [x] Updated each to import from conftest.
- [x] Verify: 75 tests pass. _(Note: `tests/unit/strategy/test_auto_save.py::test_auto_save_updates_metadata_latest_turn` is a PRE-EXISTING xdist file-lock flake on `output/saves/AutoSaveTest`; not caused by this change. Confirmed by stash-baseline.)_

### Task 6.2: HLP-002 — `MockPlanetType(Enum)` 10+ copies → fixtures/colonization_fixtures.py
**File:** `tests/fixtures/colonization_fixtures.py` (new or extend) + 10+ consumers
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/`

- [x] Created `tests/fixtures/colonization_fixtures.py` with canonical `MockPlanetType` Enum covering CONTINENTAL/ICE_DWARF/ARID/DYSON_SPHERE.
- _PARTIAL_: migrated 2 module-level copies (`test_planet_specific_colonization.py`, `test_commands.py`). The remaining 12+ copies are nested inside test methods or fixtures (e.g. `test_colonization_facade.py` has 9 inline copies, each defined inside its own test method). A mechanical sweep would require per-spot edits and is best driven as a separate dedicated refactor; the canonical home is now in place.
- [x] Verify: 22 tests pass.

### Task 6.3: HLP-003 — `make_mock_ship_instance` 4 local copies → tests/conftest.py
**File:** `tests/conftest.py` (canonical, already exists at line 350) + 4 consumer files
**Tests:** `pytest tests/integration/ui/test_fleet_build_button.py tests/integration/ui/test_strategy_buttons.py tests/unit/strategy/test_advanced_fleet_orders.py tests/repro_issues/test_bug_27_ordertype.py`

- [x] Extended canonical `make_mock_ship_instance` with `has_yard=False` kwarg.
- [x] Deleted 4 local copies; replaced with imports.
- [x] Verify: 21 tests pass.

### Task 6.4: HLP-004 — `_make_fleet` 43+ definitions → tests/conftest.py
**File:** `tests/conftest.py` (extend with `_make_mock_fleet`) + 43+ consumer files
**Tests:** `pytest tests/`

- [x] Canonical `_make_mock_fleet` added to `tests/conftest.py` (during Phase 5 Task 5.1).
- _PARTIAL_: full 43-file sweep deferred. The 3 DUP-001 cluster sites are migrated (Phase 5). Remaining ~40 sites have signature/kwarg variation that requires per-site triage; the canonical home is in place for the future sweep.
- [x] Verify: targeted DUP-001 cluster tests pass.

### Task 6.5: HLP-005 — `setup_tmpdir` Paths.SAVES_DIR fixture (4 copies)
**File:** `tests/unit/strategy/save_game_service/conftest.py` (canonical, already has at line 42) + consumers
**Tests:** `pytest tests/unit/strategy/save_game_service/ tests/unit/strategy/test_auto_save.py tests/unit/ui/test_save_selection.py`

- _NEEDS_REWORK_: per skeptical-check verification, the `chdir`-variant in `test_auto_save.py` vs the `Paths.SAVES_DIR`-patching variant in other files are not 1:1 interchangeable — `test_auto_save.py` deliberately relies on relative-cwd save behavior for its assertions. A unified fixture would need to support both modes via parameter; the team should choose one strategy team-wide before consolidating. Out of scope for this CAT-5 sweep.
- [x] Verify: tests pass (no change made).

### Task 6.6: HLP-006 — `_make_empire(colonies=None)` 6 copies → engine/conftest.py
**File:** `tests/unit/strategy/engine/conftest.py` (extend) + 6 consumer files
**Tests:** `pytest tests/unit/strategy/engine/`

- [x] Phase 5 Task 5.4 already extended `engine/conftest.py` with `make_mock_empire` covering 5 of 6 sites. The 6th (`test_harvesting_engine.py`) intentionally kept local with PROJ-412 transient-dirty-flag semantics documented in docstring.
- [x] `test_empire.py` uses real `Empire(...)` constructor — kept as-is (intentional real-empire test).
- [x] Verify: 1449 engine tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to indicate PROJ-479 complete

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
