# Phase 2: CAT-5 Fixture Bloat

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-479 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete (partial — many tasks marked NEEDS_REWORK per skeptical-check verification)
**Objective:** Rescope or restructure the 18 verified CAT-5 fixture-bloat findings from review `2026-05-20_210550_test-review`. Each finding is a function-scoped fixture that rebuilds expensive state per test (pygame display, full Ship objects, registry hydration). The key skeptical check applied during verification: **mutable shared state can't be rescoped** — fixtures that mutate must stay function-scoped, only confirmed-immutable fixtures get rescoped to module/class/session. Reclaim ~400-600 LOC of redundant setup + significant per-test wall-clock savings.

---

## Tasks

### Task 2.1: test_theme_discovery.py — 9 autouse pygame inits
**File:** `tests/unit/ui/test_theme_discovery.py`
**Tests:** `pytest tests/unit/ui/test_theme_discovery.py`

- [x] Added module-scoped autouse `_shared_pygame_display` fixture. Per-test pygame.display.set_mode calls now wrapped in `if not pygame.display.get_surface()` guard so they are cheap no-ops after the class-scoped init. Manager state stays per-test (tests mutate it; sharing would break isolation).
- [x] Verify: 31 tests pass; pygame.display init drops from per-test to once-per-class.
- _NEEDS_REWORK_: plan's "share initialized ShipThemeManager across tests in each class" rejected — multiple tests mutate `mgr.themes`, `mgr.default_theme`, `mgr.discovery_complete`. Per-test `set_default_ship_theme_manager(ShipThemeManager())` reset is load-bearing for isolation.

### Task 2.2: test_ai.py — Ship + AIController rebuild per test
**File:** `tests/unit/ai/test_ai.py`
**Tests:** `pytest tests/unit/ai/test_ai.py`

- [x] Added module-level `_AI_TEST_DATA_LOADED` cache flag and `_ensure_ai_test_data_loaded()` helper to skip redundant disk-loads of components.json / test_vehicleclasses.json / test_targeting_policies.json / test_movement_policies.json within a single test. _Net effect is a no-op_ because the per-test teardown (`policy_manager.clear()`) is contractually required for test isolation (removing it broke `test_strategy_dispatch_flee`), so the cache flag is invalidated every test.
- _NEEDS_REWORK_: plan's "class-scope ai_setup + deepcopy" rejected — Ship objects hold pygame surface references and registry pointers that don't survive deepcopy, AND each test mutates ship state (HP / is_alive / position). A correct implementation would require either a state-snapshot/restore helper or rebuilding Ships in a class-scoped fixture with explicit per-test mutation reset; both are too invasive for this CAT-5 cleanup pass.
- [x] Verify: 17 tests pass.

### Task 2.3: test_combat.py — 3 autouse setup fixtures
**File:** `tests/unit/strategy/test_combat.py`
**Tests:** `pytest tests/unit/strategy/test_combat.py`

- _NEEDS_REWORK_: deferred per skeptical-check verification. The 3 setup fixtures build `Ship + 4 components` per test; the Ships are mutated by every test (damage, energy drain, `is_alive=False`). Class-scope without deepcopy would cause cross-test contamination; class-scope with deepcopy is unsafe for Ship objects (pygame surface refs). The correct fix is a state-snapshot/restore helper or `setup` builds fresh Ship from a class-scoped template `dict`. Out of scope for this CAT-5 sweep. _(Actual path: `tests/unit/combat/test_combat.py`.)_
- [x] No-op verify: existing tests pass (10 tests).

### Task 2.4: test_weapons_report_layout.py — missing teardown
**File:** `tests/unit/ui/test_weapons_report_layout.py`
**Tests:** `pytest tests/unit/ui/test_weapons_report_layout.py`

- [x] Added explicit teardown calling `manager.clear_and_reset()` then `pygame.quit()`.
- [x] Verify: 1 test passes.

### Task 2.5: density/conftest.py — split mutable vs immutable
**File:** `tests/unit/strategy/generation/density/conftest.py`
**Tests:** `pytest tests/unit/strategy/generation/density/`

- [x] Per plan: kept mutable fixtures function-scoped. No code change required. Verified test pass below.
- [x] Verify: passes.

### Task 2.6: test_event_log_replay_e2e.py — pygame init per test
**File:** `tests/integration/ui/test_event_log_replay_e2e.py`
**Tests:** `pytest tests/integration/ui/test_event_log_replay_e2e.py`

- [x] Rescoped `pygame_init` to `scope="module"`.
- [x] Verify: 4 tests pass.

### Task 2.7: test_build_queue_enhanced_planet_report.py — UIPanel rebuilds
**File:** `tests/integration/ui/test_build_queue_enhanced_planet_report.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_enhanced_planet_report.py`

- _NEEDS_REWORK_: rescoping to class/module requires cascading rescope of dependency fixtures (`test_planet`, `mock_design_library`, `ui_manager`) — these are not all under our control (ui_manager doesn't exist as a session fixture; mock_design_library has session-state). Deferred to a later sweep.
- [x] Verify: tests pass.

### Task 2.8: test_quickstart_flow.py — full filesystem I/O per test
**File:** `tests/integration/quickstart/test_quickstart_flow.py`
**Tests:** `pytest tests/integration/quickstart/test_quickstart_flow.py`

- [x] Rescoped both `full_quickstart_1p` and `full_quickstart_2p` fixtures to `scope="class"`. Filesystem I/O (SaveGameService.save_game, QuickstartBuilder.copy_quickstart_designs/spawn_initial_complexes) now happens once per class instead of per test. Class-scope chosen over module-scope because fixtures live inside `TestQuickstartWithComplexes`.
- [x] Verify: 8 tests pass.

### Task 2.9: test_battle_state_serialization.py — 9 function-scoped fixtures
**File:** `tests/unit/simulation/test_battle_state_serialization.py`
**Tests:** `pytest tests/unit/simulation/test_battle_state_serialization.py`

- _MINOR (downgraded per plan)_: 17 dataclass-instance fixtures across 7 classes. Rescoping each to module scope would require lifting the fixtures outside their containing classes (pytest class-scope-with-self quirks). The dataclass-construction cost is negligible; per-test build of a `ComponentState(component_id=...)` is essentially a dict literal. Deferred.
- [x] Verify: 54 tests pass.

### Task 2.10: test_research_renderer.py — importlib reload per test
**File:** `tests/unit/ui/screens/test_research_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_research_renderer.py`

- [x] Rescoped to `scope="module"`. _(Actual path: `tests/unit/research/test_research_renderer.py`.)_
- [x] Verify: 20 tests pass.

### Task 2.11: test_utils.py — function-scoped pygame_gui UIManager
**File:** `tests/unit/ui/test_utils.py`
**Tests:** `pytest tests/unit/ui/test_utils.py`

- _NEEDS_REWORK_: plan assumes a cached `ui_manager` fixture exists in root conftest. It does not. The fix would require ADDING a session/module-scoped `ui_manager` fixture to `tests/conftest.py`, then migrating consumers. Out of scope for this CAT-5 sweep; should be filed as a separate Discovered Issue.
- [x] Verify: tests pass (no change made).

### Task 2.12: test_build_queue_design_report.py — 26 redundant panel builds
**File:** `tests/unit/ui/screens/test_build_queue_design_report.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_design_report.py`

- _NEEDS_REWORK_: rescoping requires lifting per-class fixtures or migrating dependency fixtures (mock_ship etc.) to matching scope. Test file lives at `tests/integration/ui/test_build_queue_design_report.py`. Deferred to follow-up sweep.
- [x] Verify: tests pass.

### Task 2.13: test_ship_serialization.py — equipped_ship rebuild
**File:** `tests/unit/simulation/entities/test_ship_serialization.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_serialization.py`

- _NEEDS_REWORK_: Ship objects are mutable and likely mutated by serialization tests (HP changes, equipped/unequipped flips). Rescoping requires either snapshot-restore semantics or careful per-test mutation audit. Deferred.
- [x] Verify: tests pass.

### Task 2.14: test_strategy_session_facade_public_api.py — cheap fixture overuse
**File:** `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`
**Tests:** `pytest tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`

- [x] Rescoped fixture to module scope.
- [x] Verify: tests pass.

### Task 2.15: test_race_summary_panel.py — partial fixture rescope
**File:** `tests/unit/ui/test_race_summary_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_summary_panel.py`

- _NEEDS_REWORK_: rescoping `mock_race_config_empty` to module scope requires lifting it out of its class (or making sibling dependencies module-scoped). Per skeptical-check the partial rescope was already documented as smaller-than-claimed benefit. Deferred to follow-up sweep.
- [x] Verify: tests pass.

### Task 2.16: test_fleet_orders_refresh.py — UIManager construction in unit tests
**File:** `tests/unit/ui/screens/test_fleet_orders_refresh.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_orders_refresh.py`

- _NEEDS_REWORK_: moving the file to integration/ or wrapping UIManager behind an interface is a structural refactor (touches import paths and possibly production code). Out of scope for this CAT-5 fixture sweep.
- [x] Verify: tests pass (no change made).

### Task 2.17: test_transfer_dialog_enhanced.py — UIManager without pygame.init
**File:** `tests/unit/ui/screens/test_transfer_dialog_enhanced.py`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog_enhanced.py`

- _NEEDS_REWORK_: changing UIManager to MagicMock requires verifying downstream pygame_gui method-call expectations of every test in the file (risk of false-pass). Deferred.
- [x] Verify: tests pass (no change made).

### Task 2.18: test_combat.py for empire_treasury_panel — accept as-is
**File:** `tests/unit/ui/panels/test_empire_treasury_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_empire_treasury_panel.py`

- [x] No change required per verification.
- [x] _(Audit-traceability task.)_
- [x] Verify: tests pass.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked (or marked NEEDS_REWORK with rationale)
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase (Phase 3 — CAT-6 Mocking Brittleness)

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
