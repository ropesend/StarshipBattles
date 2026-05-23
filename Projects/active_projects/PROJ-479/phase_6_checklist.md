# Phase 6: HLP Helper Consolidation

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-479 6`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Consolidate the 6 cross-shard helper duplications (HLP-001 through HLP-006) verified in `Reviews/results/2026-05-20_210550_test-review/CROSS_SHARD.md`. All 6 cluster definitions were VERIFIED in third-pass verification; extraction targets are sensible. Reclaim ~530 LOC by replacing 60+ local copies with imports from canonical conftest / fixtures.

---

## Tasks

### Task 6.1: HLP-001 — `MockGameSession` 5 copies → save_game_service/conftest.py
**File:** `tests/unit/strategy/save_game_service/conftest.py` (canonical) + 4 consumers
**Tests:** `pytest tests/unit/strategy/save_game_service/ tests/unit/ui/test_save_selection.py tests/unit/strategy/test_auto_save.py`

- [ ] Confirm canonical `MockGameSession` in `tests/unit/strategy/save_game_service/conftest.py:12-39` is the source-of-truth. If `test_auto_save.py:14-41` uses a different signature (`save_path` param), extend the canonical with an optional kwarg.
- [ ] Delete 4 local copies (byte-identical or near-identical):
  - `tests/unit/strategy/save_game_service/test_save_load_ops.py:24-51` _(Phase 1 Task 1.20 handles this one)_
  - `tests/unit/strategy/save_game_service/test_error_handling.py:24-51`
  - `tests/unit/ui/test_save_selection.py:36-62`
  - `tests/unit/strategy/test_auto_save.py:14-41`
- [ ] Update each to import from conftest.
- [ ] Verify: affected tests pass; LOC delta ≈ -100.

### Task 6.2: HLP-002 — `MockPlanetType(Enum)` 10+ copies → fixtures/colonization_fixtures.py
**File:** `tests/fixtures/colonization_fixtures.py` (new or extend) + 10+ consumers
**Tests:** `pytest tests/unit/strategy/ tests/integration/strategy/`

- [ ] Create or extend `tests/fixtures/colonization_fixtures.py` with a single canonical `MockPlanetType` Enum covering all observed variants: `CONTINENTAL`, `ICE_DWARF`, `ARID`, `DYSON_SPHERE`.
- [ ] Replace inline definitions in 10+ files (`tests/unit/strategy/turn_engine/conftest.py:18`, `test_colonize_validator.py:21`, `test_planet_specific_colonization.py:33`, `test_engine_event_emission.py:440/540/938/999`, `test_strategy_colonization.py:21`, `test_fleet_order_processor.py:157/282/484`, `test_commands.py:18`, plus 4 more per cross-shard report).
- [ ] Verify: affected tests pass; LOC delta ≈ -80.

### Task 6.3: HLP-003 — `make_mock_ship_instance` 4 local copies → tests/conftest.py
**File:** `tests/conftest.py` (canonical, already exists at line 350) + 4 consumer files
**Tests:** `pytest tests/integration/ui/test_fleet_build_button.py tests/integration/ui/test_strategy_buttons.py tests/unit/strategy/test_advanced_fleet_orders.py tests/repro_issues/test_bug_27_ordertype.py`

- [ ] Extend canonical `make_mock_ship_instance` at `tests/conftest.py:350-384` to accept an optional `has_yard=False` kwarg (for `test_fleet_build_button.py`'s use case).
- [ ] Delete 4 local copies:
  - `tests/integration/ui/test_fleet_build_button.py:12-40` (has `has_yard` extension)
  - `tests/integration/ui/test_strategy_buttons.py:13`
  - `tests/unit/strategy/test_advanced_fleet_orders.py:20-39`
  - `tests/repro_issues/test_bug_27_ordertype.py:12-30`
- [ ] Verify: affected tests pass; LOC delta ≈ -60.

### Task 6.4: HLP-004 — `_make_fleet` 43+ definitions → tests/conftest.py
**File:** `tests/conftest.py` (extend with `_make_mock_fleet`) + 43+ consumer files
**Tests:** `pytest tests/`

- [ ] Add `_make_mock_fleet(fleet_id=1, owner_id=1, location=None, speed=5, **overrides)` to `tests/conftest.py`. _(Note: Phase 5 Task 5.1 starts this for the DUP-001 cluster; this task extends the work across all ~43 sites.)_
- [ ] Walk through the 43 files in batches (alphabetical or by package) replacing local `_make_fleet` with the canonical helper. ~70% of copies share 6 core fields; the rest pass overrides for `task_forces` / `orders` / etc.
- [ ] Verify: full suite passes; LOC delta ≈ -200.

### Task 6.5: HLP-005 — `setup_tmpdir` Paths.SAVES_DIR fixture (4 copies)
**File:** `tests/unit/strategy/save_game_service/conftest.py` (canonical, already has at line 42) + consumers
**Tests:** `pytest tests/unit/strategy/save_game_service/ tests/unit/strategy/test_auto_save.py tests/unit/ui/test_save_selection.py`

- [ ] Promote the canonical `setup_tmpdir` fixture in `tests/unit/strategy/save_game_service/conftest.py:42` (it's already there, just not autouse / not class-scoped). Make it consumable from sibling test files.
- [ ] Reconcile the `test_auto_save.py:47-55` variant which uses `os.chdir(tmpdir)` + `os.chdir(original_cwd)` instead of patching `Paths.SAVES_DIR`. _(verification adjusted: the two mechanisms aren't a 1:1 swap — create a unified fixture supporting both modes via parameter, or pick one strategy team-wide. See verification_report.md.)_
- [ ] Delete the 4 local copies:
  - `tests/unit/strategy/save_game_service/test_save_load_ops.py:57-65` (and 4 more copies in same file at 150, 210, 286, 342 per S16-F005)
  - `tests/unit/strategy/save_game_service/test_error_handling.py:57-67`
  - `tests/unit/strategy/test_auto_save.py:47-55` (chdir variant)
  - `tests/unit/ui/test_save_selection.py:18-33` (`_patched_saves_tmpdir` variant)
- [ ] Verify: affected tests pass; LOC delta ≈ -50.

### Task 6.6: HLP-006 — `_make_empire(colonies=None)` 6 copies → engine/conftest.py
**File:** `tests/unit/strategy/engine/conftest.py` (extend) + 6 consumer files
**Tests:** `pytest tests/unit/strategy/engine/`

- [ ] _(Overlaps with Phase 5 Task 5.4 DUP-005; if Task 5.4 already extended `engine/conftest.py` with `mock_empire_factory`, this task ensures all 6 sites are covered.)_
- [ ] Handle the extended variant in `test_harvesting_engine.py:27` (adds `resource_pool` / `max_storage` / `empire_id`) via factory kwargs.
- [ ] Handle the `test_empire.py:17-20` variant which uses real Empire constructor (not MagicMock) — keep as-is if it's testing real Empire behavior, or extract a separate `real_empire_factory`.
- [ ] Verify: `pytest tests/unit/strategy/engine/` passes; LOC delta ≈ -50.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to indicate PROJ-479 complete

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
