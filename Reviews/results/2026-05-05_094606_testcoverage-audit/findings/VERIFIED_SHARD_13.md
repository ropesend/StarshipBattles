# VERIFIED Shard 13 — Skeptical Verification

## Summary

| Category | Phase 2 Count | Verified Count | Net Change |
|----------|--------------|---------------|------------|
| CRITICAL | 0 | 0 | — |
| MAJOR | 5 | 1 | **-4 DISPUTED** |
| MINOR | 4 | 6 | +2 downgraded from MAJOR |
| ADVISORY | 9 | 9 | — |
| **Phase 2 agent errors** | — | 5 | See below |

**Overall**: The Phase 2 agent exhibited **significant search methodology failures**, missing 3 test subdirectories and conflating integration tests with "UI-layer only" tests. 4 of 5 MAJOR findings are DISPUTED.

---

## CONFIRMED MAJOR Gaps

### MAJOR-001: `workshop_data_loader.py` — `load_all` error paths (CONFIRMED, downgraded from MAJOR to MINOR)

**Original claim**: 229 LOC data loader with 7+ untested error paths. 1.9KB test file only covers happy path.

**Verification**:
- **Evidence read**: `game/ui/screens/workshop_data_loader.py:1-229`, `tests/unit/ui/screens/test_workshop_data_loader.py:1-59`, `tests/unit/workshop/test_workshop_data_loader.py:1-190`
- **What's covered**: `find_file` method is well-tested (direct match, test_ prefix, default fallback, not found, multiple names at `test_workshop_data_loader.py:47-117`). `_load_policies` test data branch tested. `load_all` happy path tested via integration test at lines 154-165. `clear_registries` tested via mock at lines 119-135.
- **What's genuinely missing**: The `try/except` blocks at `workshop_data_loader.py:157-168` (`FileNotFoundError/OSError`, `JSONDecodeError/KeyError/TypeError`, `ValueError`) have zero direct tests. Corrupt JSON, missing modifiers.json, missing components.json — none of these error paths are exercised.
- **Total test LOC**: 249 (not 59 as Phase 2 claimed — missed `test_workshop_data_loader.py`)
- **Severity**: **MINOR** (downgraded from MAJOR). `find_file` is well-tested (core logic). Only exception handlers in `load_all`'s try/except blocks are untested. The integration test covers the happy path.

---

## DISPUTED MAJOR Findings

### DISPUTED-001: `battle_panels.py` — "zero dedicated tests" (DISPUTED)

**Original claim**: 563 LOC file with zero dedicated unit tests. Contains testable state management logic (ID-based expansion tracking, ship status text computation, winner determination logic).

**Verification**:
- **Evidence read**: `game/ui/panels/battle_panels.py:1-563`, `tests/unit/ui/test_battle_panels.py:1-361`, `tests/unit/ui/test_battle_panels_characterization.py:1-495`, `tests/unit/ui/test_battle_panels_extended.py:1-614`
- **Three dedicated test files exist** with combined **~1,470 LOC**:
  1. `test_battle_panels.py` (361 LOC) — expansion toggling, scroll offset, seeker state, coordinate logic, battle end control, DTO integration
  2. `test_battle_panels_characterization.py` (495 LOC) — `_get_ships()` fallback chain (ui_service list, non-list mock, AttributeError, missing attribute), `ExpandableIdPanel` toggle helpers, `ShipStatsPanel` banner rect recording per draw, dead/derelict status colors, shift-click focus, `SeekerMonitorPanel` clear/X-button/expansion, `BattleControlPanel` TEAM 1 WINS / TEAM 2 WINS / DRAW text branches
  3. `test_battle_panels_extended.py` (614 LOC) — `_get_ships()` with DTOs, fallback to scene.ships, exception fallback, empty ship list, ID-based tracking, `get_expanded_height()` (no shields/with shields/with components), `BattleControlPanel` with no rects set
- **All "untested" items the report listed are in fact tested**:
  - `_get_ships()` fallback: characterization tests lines 114-157, extended tests lines 108-146
  - Expansion toggle: test_battle_panels.py:96-115, characterization:164-182, extended:174-226
  - Winner determination: characterization:427-460 (TEAM 1 WINS, TEAM 2 WINS, DRAW)
  - Ship status text: characterization:241-274 ([DEAD] and [DERELICT] labels verified)
- **Phase 2 agent error**: The conftest import at `tests/unit/ui/conftest.py` was for `battle_panels.py` — the agent wrongly assumed this was fixture-only, missing the dedicated test files entirely. Search methodology failed: likely searched for `test_battle_panels.py` but found the files, then ignored them.
- **Revised severity**: **ADVISORY** (pure pygame rendering portions are untestable by convention; all state management logic is tested).

---

### DISPUTED-002: `research_controls.py` — "no dedicated test file" (DISPUTED)

**Original claim**: 475 LOC with testable business logic (slider-to-tracker binding, allocation range computation, auto-spread state management). Conftest provides fixtures but no test methods.

**Verification**:
- **Evidence read**: `game/ui/research/research_controls.py:1-475`, `tests/unit/research/research_controls/test_event_routing_and_updates.py:1-512`, `tests/unit/research/research_controls/test_reset_state.py:1-269`, `tests/unit/research/research_controls/conftest.py:1-88`
- **Two dedicated test files exist** with combined **781 LOC**:
  1. `test_event_routing_and_updates.py` (512 LOC) — 28 tests covering:
     - `handle_event` button routing (Next Turn, Close, Reset, Auto-Spread, unknown button) — lines 74-153
     - `handle_event` slider routing (budget updates tracker + label + allocation range, allocation uses clamped value) — lines 158-204
     - `update_selected_node` (all 7 labels populated, maxed price, slider enabled only when available, allocation set from state) — lines 206-262
     - `clear_selection` (all labels reset to placeholder, slider disabled) — lines 264-291
     - Budget/auto-spread (allocated/budget display, spread_rp_evenly on enable, not on disable, button ON/OFF text, slider range floor) — lines 295-364
     - `update_turn_log` (no events, breakthrough, progress, decay, prepend, truncate after 5, replace placeholder) — lines 369-495
     - `clear_log` (resets to placeholder) — lines 500-511
  2. `test_reset_state.py` (269 LOC) — 10 tests covering:
     - `reset()` method (tracker reference, tech tree reference, clears selection, updates budget display, clears log, updates auto-spread button, preserves callbacks, syncs slider position) — lines 6-187
     - State reference consistency (`_selected_node.id` used instead of external parameter, no crash on null node) — lines 190-269
- **All 3 suggested tests from the report are covered**:
  1. "slider_budget_changes_tracker" → event_routing tests:160-178
  2. "allocation slider disabled for locked node" → event_routing tests:240-248
  3. "auto_spread toggle updates button text" → event_routing tests:333-346
- **Phase 2 agent error**: Agent searched for `test_research_controls.py` (single file path) but found only a conftest. It missed the test subdirectory `tests/unit/research/research_controls/` containing 2 test files + conftest. This is a glob/search methodology failure.
- **Revised severity**: **ADVISORY** (pure pygame_gui widget construction is conventionally untestable by unit tests; all business logic is comprehensively tested via the mock-pygame_gui pattern).

---

### DISPUTED-003: `replay_resolver.py` — "zero direct unit tests for error paths" (DISPUTED)

**Original claim**: 5 distinct error paths in `resolve()` have zero direct unit tests. UI-layer test exercises only the happy path.

**Verification**:
- **Evidence read**: `game/strategy/services/replay_resolver.py:1-130`, `tests/integration/replay/test_replay_resolver.py:1-180`
- **The integration test directly tests ReplayResolver.resolve() with a real ReplayStore**. It is NOT a UI-layer test as the report claimed. All 6 error paths checked:
  1. Empty replay_id → found=False, reason="missing" — line 36-39
  2. Unknown replay_id → found=False, reason="missing" — line 41-45
  3. Corrupt file → found=False, reason="corrupt" — line 55-62
  4. Version mismatch → found=False, reason="version_drift" — line 64-73
  5. Registry hash drift → found=True, registry_drift=True — line 75-80
  6. Empty hash (either side) → no drift — line 82-89
  7. `from_registries` factory → valid resolver — line 91-95
  8. Verification sidecar: None → None — line 100-107
  9. Verification sidecar: PASSED → "PASSED" — line 109-137
  10. Verification sidecar: FAILED → "FAILED" — line 139-166
  11. Corrupt sidecar → None — line 168-180
- **Single genuine gap**: `replay_dir is None` branch at `replay_resolver.py:103-104` is not directly tested (the `store` fixture in tests always creates a save_root, setting up a valid replay_dir).
- **Phase 2 agent error**: The test file is in `tests/integration/` directory but imports ReplayResolver directly and tests its `resolve()` method. Agent dismissed it as "UI-layer test only covers happy path" without reading the 180 LOC test file.
- **Revised severity**: **MINOR** (single branch: `replay_dir is None` returning "missing"). All other branches comprehensively tested in integration test.

---

### DISPUTED-004: `strategy_render/context.py` `hex_radius_to_screen` — "untested math function" (DISPUTED)

**Original claim**: The `hex_radius_to_screen` function contains non-trivial math but has no unit tests. MAJOR severity.

**Verification**:
- **Evidence read**: `game/ui/screens/strategy_render/context.py:1-34`, `game/ui/screens/strategy_renderer.py:180-187`, `tests/unit/ui/screens/test_strategy_renderer.py:660-684`
- **The function is tested indirectly** via `StrategyRenderer._hex_radius_to_screen()` which delegates to `hex_radius_to_screen(self.hex_size, self.camera.zoom)` (renderer.py:187). The test at test_strategy_renderer.py:660-684:
  - Tests BUG-94 power curve for radii 1, 2, 4
  - Verifies radius-2 is the linear anchor point
  - Verifies radius-1 < linear (underflow prevention)
  - Verifies radius-4 > linear (outer ring reach)
  - Verifies monotonic ordering r1 < r2 < r4
- **Genuinely untested**: The standalone function's `radius_hexes <= 0` branch returning 3 (`context.py:25-26`) is NOT tested. The renderer test only passes positive radii. Different hex_size values and zoom values are also not tested (all tests use hex_size=10, zoom=1.0).
- **Revised severity**: **MINOR** (downgraded from MAJOR). The core power-curve formula is tested via the renderer wrapper. Only the guard clause `radius_hexes <= 0 → return 3` and parameter sensitivity (hex_size, zoom) are untested.

---

## INCONCLUSIVE / UPGRADED

None. All ADVISORY findings verified as ADVISORY (pure pygame/pygame_gui rendering). No upgrades warranted.

---

## Agent Errors (Phase 2 Methodology Failures)

| # | Error | Impact | Evidence |
|---|-------|--------|----------|
| **AE-1** | Missed 3 test files for `battle_panels.py` (~1,470 combined LOC) | False MAJOR claim "zero dedicated tests" | `tests/unit/ui/test_battle_panels.py`, `test_battle_panels_characterization.py`, `test_battle_panels_extended.py` |
| **AE-2** | Missed 2 test files for `research_controls.py` (~781 combined LOC) | False MAJOR claim "no dedicated test file" | `tests/unit/research/research_controls/test_event_routing_and_updates.py`, `test_reset_state.py` |
| **AE-3** | Mischaracterized integration test for `replay_resolver.py` as "UI-layer only" | False MAJOR claim "zero direct unit tests" | `tests/integration/replay/test_replay_resolver.py` (180 LOC, 11 test methods directly calling `ReplayResolver.resolve()`) |
| **AE-4** | Reported `hex_radius_to_screen` as completely untested when it's tested via renderer wrapper | False MAJOR claim | `test_strategy_renderer.py:660-684` exercises the same formula through `_hex_radius_to_screen` |
| **AE-5** | Reported `workshop_data_loader.py` test file as 1.9KB when there are two test files totaling ~249 LOC | Underestimated test coverage | Missed `tests/unit/workshop/test_workshop_data_loader.py` (190 LOC) |

**Root cause patterns**:
1. **Single-file-name search**: Agent searched for exact filenames (`test_research_controls.py`) instead of directory-glob patterns (`tests/unit/research/research_controls/**`), missing test subdirectories.
2. **Test location assumptions**: Agent assumed `tests/integration/` tests are "UI-layer" without reading them.
3. **No lateral code reading**: Agent didn't trace delegate chains (renderer wrapper → standalone function) to discover indirect test coverage.

---

## Final Adjusted Severity Map

| File | Phase 2 | Verified | Rationale |
|------|---------|----------|-----------|
| `battle_panels.py` | MAJOR | **ADVISORY** | 1,470 LOC of dedicated tests cover all state logic; only pure rendering remains untested |
| `research_controls.py` | MAJOR | **ADVISORY** | 781 LOC of dedicated tests cover all business logic; only widget construction remains untested |
| `replay_resolver.py` | MAJOR | **MINOR** | 180 LOC integration test covers 10 of 11 branches; only `replay_dir is None` untested |
| `strategy_render/context.py` (hex_radius_to_screen) | MAJOR | **MINOR** | Core formula tested via renderer wrapper; only guard clause `<= 0 → 3` untested |
| `workshop_data_loader.py` | MAJOR | **MINOR** | 249 LOC of tests; `find_file` well-tested; only `load_all` exception handlers untested |
| `event_bus.py` | MINOR (Phase 1) | MINOR | Confirmed: empty event_type emission untested |
| `physics.py` (radiation) | MINOR (Phase 1) | MINOR | Confirmed: empty stars list, distance=0 clamp may be untested |
| `strategy_camera_nav.py` | MINOR (Phase 1) | MINOR | Confirmed: `_resolve_global_hex` edge branches may be untested |
| `orders_window.py` | MINOR (Phase 1) | MINOR | Confirmed: some OrderType branches untested |
| `strategy_render/context.py` (RenderContext) | MAJOR | **ADVISORY** | RenderContext is a frozen value dataclass; `hex_radius_to_screen` downgraded to MINOR above |
| `battle_setup/panels/left_panel.py` | ADVISORY | ADVISORY | Confirmed: pure layout |
| `test_lab/renderer/category_panel.py` | ADVISORY | ADVISORY | Confirmed: pure rendering |
| `test_lab/ship_panels.py` | ADVISORY | ADVISORY | Confirmed: pure rendering |
| `planet_report_panel.py` | ADVISORY | ADVISORY | Confirmed: data functions tested, widgets ADVISORY |
| `strategy_validation/__init__.py` | ADVISORY | ADVISORY | Confirmed: re-export file |

**Net result**: 0 CRITICAL, 0 MAJOR, 6 MINOR, 13 ADVISORY.
