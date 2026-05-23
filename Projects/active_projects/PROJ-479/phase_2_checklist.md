# Phase 2: CAT-5 Fixture Bloat

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-479 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Rescope or restructure the 18 verified CAT-5 fixture-bloat findings from review `2026-05-20_210550_test-review`. Each finding is a function-scoped fixture that rebuilds expensive state per test (pygame display, full Ship objects, registry hydration). The key skeptical check applied during verification: **mutable shared state can't be rescoped** — fixtures that mutate must stay function-scoped, only confirmed-immutable fixtures get rescoped to module/class/session. Reclaim ~400-600 LOC of redundant setup + significant per-test wall-clock savings.

---

## Tasks

### Task 2.1: test_theme_discovery.py — 9 autouse pygame inits
**File:** `tests/unit/ui/test_theme_discovery.py`
**Tests:** `pytest tests/unit/ui/test_theme_discovery.py`

- [ ] Rescope the 9 autouse function-scoped fixtures (across TestNewThemes / TestImageSizeValidationWarning / TestShipThemeManagerSingletonLifecycle / TestShipThemeManagerErrorPaths / TestShipThemeManagerCaching / TestShipThemeManagerMetrics / TestShipThemeManagerThreadSafety / TestShipThemeManagerManualScale / TestThemeContractAgainstRealAssets) to class scope. Share the initialized ShipThemeManager across the ~30 tests in each class.
- [ ] Verify: `pytest tests/unit/ui/test_theme_discovery.py` passes; per-class pygame init drops from ~30 to 9.

### Task 2.2: test_ai.py — Ship + AIController rebuild per test
**File:** `tests/unit/ai/test_ai.py`
**Tests:** `pytest tests/unit/ai/test_ai.py`

- [ ] Rescope `ai_setup` fixture (lines 17-70) to class scope. Use `copy.deepcopy()` per test on the mutable Ship objects, or re-initialize only the mutable state.
- [ ] Verify: `pytest tests/unit/ai/test_ai.py` passes; LOC delta minimal but per-test build cost drops from full Ship+5-component+AI build → deep copy.

### Task 2.3: test_combat.py — 3 autouse setup fixtures
**File:** `tests/unit/strategy/test_combat.py`
**Tests:** `pytest tests/unit/strategy/test_combat.py`

- [ ] Rescope the 3 autouse setup fixtures (lines 14-49, 104-115, 149-160) to class scope. Each builds Ship + 4 components + recalculate_stats per test.
- [ ] Verify: `pytest tests/unit/strategy/test_combat.py` passes; per-class Ship builds drop.

### Task 2.4: test_weapons_report_layout.py — missing teardown
**File:** `tests/unit/ui/test_weapons_report_layout.py`
**Tests:** `pytest tests/unit/ui/test_weapons_report_layout.py`

- [ ] Add teardown to the function-scoped fixture (lines 16-36) — call `pygame.quit()` and `manager.clear_and_reset()`. _(verification note: the original CAT-5 claim was about scope, but the single-test class makes scope change cosmetic; real issue is missing teardown.)_
- [ ] Verify: `pytest tests/unit/ui/test_weapons_report_layout.py` passes; no leaked pygame state.

### Task 2.5: density/conftest.py — split mutable vs immutable
**File:** `tests/unit/strategy/generation/density/conftest.py`
**Tests:** `pytest tests/unit/strategy/generation/density/`

- [ ] Keep `seeded_rng` and `simple_density_map` (lines 62-79) as function-scoped — they're mutable. Only rescope the confirmed-immutable primitive fixtures. _(verification adjusted from review's blanket session-scope — `seeded_rng` is stateful PRNG, `simple_density_map` is mutable DensityMap; blanket session-scope unsafe. See verification_report.md.)_
- [ ] Verify: `pytest tests/unit/strategy/generation/density/` passes; LOC delta minimal.

### Task 2.6: test_event_log_replay_e2e.py — pygame init per test
**File:** `tests/integration/ui/test_event_log_replay_e2e.py`
**Tests:** `pytest tests/integration/ui/test_event_log_replay_e2e.py`

- [ ] Rescope the `pygame_init` fixture (lines 21-25) to module scope. pygame.display.set_mode HIDDEN is reusable across tests.
- [ ] Verify: `pytest tests/integration/ui/test_event_log_replay_e2e.py` passes; pygame initialized once per module.

### Task 2.7: test_build_queue_enhanced_planet_report.py — UIPanel rebuilds
**File:** `tests/integration/ui/test_build_queue_enhanced_planet_report.py`
**Tests:** `pytest tests/integration/ui/test_build_queue_enhanced_planet_report.py`

- [ ] Rescope `planet_report_panel` fixture (lines 92-112) to module or class scope. Real pygame_gui.elements.UIPanel + PlanetReportPanel + UIImage per-test is unnecessary if tests read state only.
- [ ] Verify: `pytest tests/integration/ui/test_build_queue_enhanced_planet_report.py` passes.

### Task 2.8: test_quickstart_flow.py — full filesystem I/O per test
**File:** `tests/integration/quickstart/test_quickstart_flow.py`
**Tests:** `pytest tests/integration/quickstart/test_quickstart_flow.py`

- [ ] Rescope `full_quickstart_1p` and `full_quickstart_2p` fixtures (lines 19-63) to module scope. Each currently runs full GameSession construction, SaveGameService.save_game(), QuickstartBuilder.copy_quickstart_designs() (filesystem I/O), spawn_initial_complexes() per test.
- [ ] Verify: `pytest tests/integration/quickstart/test_quickstart_flow.py` passes; filesystem I/O drops dramatically.

### Task 2.9: test_battle_state_serialization.py — 9 function-scoped fixtures
**File:** `tests/unit/simulation/test_battle_state_serialization.py`
**Tests:** `pytest tests/unit/simulation/test_battle_state_serialization.py`

- [ ] Downgrade severity to MINOR and rescope to module scope after re-confirming fixtures are read-only. _(verification adjusted from review's "rescope" — all 9 fixtures were verified read-only, so scope change is safe but priority is lower than originally tagged. See verification_report.md.)_
- [ ] Verify: `pytest tests/unit/simulation/test_battle_state_serialization.py` passes; LOC delta minimal.

### Task 2.10: test_research_renderer.py — importlib reload per test
**File:** `tests/unit/ui/screens/test_research_renderer.py`
**Tests:** `pytest tests/unit/ui/screens/test_research_renderer.py`

- [ ] Rescope the `autouse=True` fixture (lines 22-38) to `scope="module"`, not session. _(verification adjusted from review's "session" — module scope preserves the importlib bypass without redundant disk I/O while keeping isolation between unrelated test modules.)_
- [ ] Verify: `pytest tests/unit/ui/screens/test_research_renderer.py` passes; reloads drop from per-test to per-module.

### Task 2.11: test_utils.py — function-scoped pygame_gui UIManager
**File:** `tests/unit/ui/test_utils.py`
**Tests:** `pytest tests/unit/ui/test_utils.py`

- [ ] Delete the function-scoped UIManager fixture (lines 482-491) and use the cached `ui_manager` fixture from root conftest.
- [ ] Verify: `pytest tests/unit/ui/test_utils.py` passes; LOC delta ≈ -10 + per-test pygame_gui setup eliminated.

### Task 2.12: test_build_queue_design_report.py — 26 redundant panel builds
**File:** `tests/unit/ui/screens/test_build_queue_design_report.py`
**Tests:** `pytest tests/unit/ui/screens/test_build_queue_design_report.py`

- [ ] Rescope `design_report_panel` fixture (lines 160-184) to module scope. Mock_ship is identical across ~26 tests; no per-test mutation observed.
- [ ] Verify: `pytest tests/unit/ui/screens/test_build_queue_design_report.py` passes.

### Task 2.13: test_ship_serialization.py — equipped_ship rebuild
**File:** `tests/unit/simulation/entities/test_ship_serialization.py`
**Tests:** `pytest tests/unit/simulation/entities/test_ship_serialization.py`

- [ ] Rescope `equipped_ship` (lines 49-82) to class scope after confirming 20+ consumers are read-only.
- [ ] Verify: `pytest tests/unit/simulation/entities/test_ship_serialization.py` passes.

### Task 2.14: test_strategy_session_facade_public_api.py — cheap fixture overuse
**File:** `tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`
**Tests:** `pytest tests/unit/strategy/facade/test_strategy_session_facade_public_api.py`

- [ ] Rescope the fixture at line 209 (`@pytest.fixture()` default function scope) to module scope. Tests are read-only contract checks.
- [ ] Verify: `pytest tests/unit/strategy/facade/test_strategy_session_facade_public_api.py` passes.

### Task 2.15: test_race_summary_panel.py — partial fixture rescope
**File:** `tests/unit/ui/test_race_summary_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_summary_panel.py`

- [ ] Rescope **only** `mock_race_config_empty` (lines 43-96 fixture cluster) to module scope. Keep `mock_race_config` and `mock_race_config_full` function-scoped — verification found mutations at lines 583-584, 681. _(verification adjusted from review's all-read-only claim. See verification_report.md.)_
- [ ] Verify: `pytest tests/unit/ui/test_race_summary_panel.py` passes; LOC delta ≈ -30 effective benefit instead of -60.

### Task 2.16: test_fleet_orders_refresh.py — UIManager construction in unit tests
**File:** `tests/unit/ui/screens/test_fleet_orders_refresh.py`
**Tests:** `pytest tests/unit/ui/screens/test_fleet_orders_refresh.py`

- [ ] Move the fixture to `tests/integration/ui/` or wrap UIManager behind an interface. _(verification adjusted from review's MAJOR — headless conftest enforces SDL_VIDEODRIVER=dummy, so the test runs; coupling is the real concern.)_
- [ ] Verify: tests pass from new location (or with interface wrapper).

### Task 2.17: test_transfer_dialog_enhanced.py — UIManager without pygame.init
**File:** `tests/unit/ui/screens/test_transfer_dialog_enhanced.py`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog_enhanced.py`

- [ ] Patch UIManager with MagicMock for unit-level isolation, or move to integration tests (line 13).
- [ ] Verify: `pytest tests/unit/ui/screens/test_transfer_dialog_enhanced.py` passes.

### Task 2.18: test_combat.py for empire_treasury_panel — accept as-is
**File:** `tests/unit/ui/panels/test_empire_treasury_panel.py`
**Tests:** `pytest tests/unit/ui/panels/test_empire_treasury_panel.py`

- [ ] No change — function-scoping at lines 92-99 is correct and documented (4 tests in TestPopulationUpkeepRow mutate snapshot.total_population_upkeep). Verification confirmed mutation exists; scope is the right call.
- [ ] _(Task retained for audit traceability — verification flagged the finding but no remediation is appropriate.)_
- [ ] Verify: `pytest tests/unit/ui/panels/test_empire_treasury_panel.py` passes; LOC delta 0.

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 3 — CAT-6 Mocking Brittleness)

_Source review: `Reviews/results/2026-05-20_210550_test-review/`. See [findings/source_review.md](findings/source_review.md) for the link._
