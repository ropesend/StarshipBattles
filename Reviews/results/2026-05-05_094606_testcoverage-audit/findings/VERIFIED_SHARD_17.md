# Shard 17 — Skeptical Verification Report

**Phase**: 3 (Skeptical Verifier)
**Scope**: 1 CRITICAL + 4 of 7 MAJOR findings verified (4 MAJOR explicitly labeled in Phase 2 report; 3 MAJOR in the summary header appear to be Phase 1 reclassifications that were not restated as MAJOR in the body text)
**Methodology**: Read each cited production file in full + 10 lines surrounding context. Read all actual test files. Grep for indirect/transitive coverage. Cross-reference import chains.

---

## CRITICAL Finding Verification

### F01: `game/simulation/combat/families/seeker.py` — SeekerHandler.fire() has zero tests

**Phase 2 Claim**: Tier 0, CRITICAL. No unit test imports this module. No test file exists. SeekerHandler.fire() has 4 untested code paths.

**Evidence Reviewed**:
- Production file: `game/simulation/combat/families/seeker.py` (73 lines) — read in full
- Searched for test file: `tests/unit/simulation/combat/families/test_seeker.py` — **DOES NOT EXIST** ✓
- Searched for direct imports: `grep "from game.simulation.combat.families.seeker" tests/unit/` — **0 matches** ✓
- Searched for indirect SeekerHandler references: Found **1 match** in `tests/unit/simulation/combat/test_weapon_dispatch_golden.py:346-368`
- Read test context: `TestSeekerGolden.test_seeker_attack_creates_missile_with_pinned_fields`

**What IS tested** (via `test_weapon_dispatch_golden.py`):
1. SeekerHandler.fire() IS called — the test patches `game.simulation.combat.families.seeker.Projectile` which forces the seeker module import
2. All 13 Projectile construction kwargs verified: owner, damage, proj_type, turn_rate, target, hp, to_hit_defense, endurance, source_weapon, range_val, max_speed
3. The "target in arc" code path (lines 49-50 in seeker.py) IS exercised: target at (100, 0), ship at (0, 0), firing_arc=90 from the test setup

**What is NOT tested**:
1. **Target outside firing arc** (line 42 fallback): No test verifies launch_vec when target beyond arc
2. **target=None path** (line 45 gate): No test calls fire with target=None
3. **aim_vec zero-length fallback** (line 50 guard): No test verifies `aim_vec.length() == 0 → launch_vec`
4. **Ship velocity incorporation** (line 53): `p_vel = launch_vec * speed + ship.velocity` — ship.velocity is always (0,0) in test setup, so additive component never verified
5. **Registry registration** (line 73): No test verifies `WEAPON_REGISTRY` contains SeekerHandler for WeaponFamily.SEEKER
6. **facing_angle and comp_facing computation** (lines 40-42): The math for radian conversion and launch_vec from component orientation

**Verdict**: **CONFIRMED (with nuance)**

The claim "No unit test file imports this module" is true — no test file directly imports `game.simulation.combat.families.seeker`. The claim that SeekerHandler.fire() is completely untested is **FALSE**. The fire method IS exercised through the weapon dispatch golden test, which validates the happy path (target in arc). However, 6 distinct code paths remain untested, including critical ones (target=None, target outside arc, aim_vec zero-length fallback).

Severity assessment: The CRITICAL classification is **partially justified**. The golden test provides baseline coverage for the main integration path, but the absence of dedicated edge-case tests means seeker/missile behavior for non-standard firing scenarios (no target, extreme angles, zero-length aim vectors) is unverified.

**Recommendation**: Write a dedicated `test_seeker.py` covering the 6 untested paths listed above. The existing golden test provides a good template for test setup.

---

## MAJOR Finding Verification

### F02: `game/ui/screens/strategy_screen_order_editing.py` — No unit tests

**Phase 2 Claim**: Tier 0, MAJOR. "No unit test file imports this module." 10 suggested test cases for testable business logic.

**Evidence Reviewed**:
- Production file: `game/ui/screens/strategy_screen_order_editing.py` (91 lines) — read in full
- **Test file EXISTS**: `tests/unit/ui/screens/test_strategy_screen_order_editing.py` (183 lines) — read in full
- Import statement: `from game.ui.screens import strategy_screen_order_editing as order_edit` (line 10)

**Coverage confirmed**:
| Function | Tests | What's verified |
|---|---|---|
| `on_edit_order` | 3 tests | MOVE→start_edit_move dispatch, TRANSFER/LOAD_POPULATION/UNLOAD_POPULATION→start_edit_transfer dispatch, unhandled OrderType is noop |
| `start_edit_move` | 4 tests | non-HexCoord target short-circuit, opponent fleet owner_id gate, state recording + camera pan, active_empire=None allows edit |
| `complete_edit_move` | 3 tests | target mutation + path invalidation (idx=0), non-zero index preserves path, out-of-range index skips target update but clears state |
| `start_edit_transfer` | 3 tests | fleet location fallback with no prior moves, walks prior MOVE destinations, walks WARP destinations, order popped + dialog opened |

_Total: 13 test methods covering all 4 public functions with edge cases._

**Verdict**: **DISPUTED**

The Phase 2 report's claim is factually incorrect. A 183-line test file exists with comprehensive coverage of all 4 public functions and their edge cases. This is NOT Tier 0. The module is Tier 2 (partial coverage, well-tested). The Phase 1 import-matching presumably missed the import because it uses module-level import syntax (`from game.ui.screens import strategy_screen_order_editing`) rather than a direct from-import.

**Correct severity**: NO_ISSUE (false positive) — the module is adequately tested.

---

### F03: `game/ui/screens/strategy_windows/fleet_report_ctrl.py` — No unit tests

**Phase 2 Claim**: Tier 0, MAJOR. "No unit test file imports this module." Testable business logic: SplitFleetCommand dispatch, dimension math, `_on_closed` callback.

**Evidence Reviewed**:
- Production file: `game/ui/screens/strategy_windows/fleet_report_ctrl.py` (63 lines) — read in full
- No dedicated test file at `tests/unit/ui/screens/strategy_windows/test_fleet_report_ctrl.py` — **CONFIRMED** ✓
- No test file directly imports `fleet_report_ctrl` — **CONFIRMED** ✓
- Indirect coverage found in `tests/unit/ui/screens/test_strategy_window_manager.py`:
  - 3 tests patch `FleetReportWindow` from `fleet_report_ctrl` (lines 444, 454, 722)
  - 1 test verifies `_on_fleet_report_closed` (line 465-469) — but this is StrategyWindowManager's method, NOT FleetReportRegistrar._on_closed

**What IS tested indirectly**:
1. `FleetReportRegistrar.open()` IS called through `StrategyWindowManager.open_fleet_report_window()` — WindowManager delegates to FleetReportRegistrar
2. Existing window kill logic: `test_open_fleet_report_kills_existing` verifies the prior window is killed before new creation
3. Window reference set: `test_open_fleet_report_creates_window` verifies `window_manager.fleet_report_window is not None`

**What is NOT tested**:
1. **SplitFleetCommand closure dispatch** (lines 37-49): The closure construction, command field correctness, and `facade.handle_command()` routing are never verified
2. **Dimension computation** (lines 33-34): `w, h = c.width * 0.9, c.height * 0.9` — the 90% scale math is never tested
3. **`_on_closed` clears window reference** (lines 62-63): `self._composer.fleet_report_window = None` — never verified directly. The StrategyWindowManager test for `_on_fleet_report_closed` tests a different method
4. **facade.handle_command` routing** (line 49): The CQRS pipeline integration is never verified

**Verdict**: **CONFIRMED**

No dedicated unit test file imports `fleet_report_ctrl.py`. The indirect coverage via `test_strategy_window_manager.py` exercises the happy path of window creation through the WindowManager delegation, but does NOT test the internal logic of `FleetReportRegistrar.open()` (SplitFleetCommand closure, dimension math, `_on_closed`). The MAJOR classification is reasonable.

---

### F04: `game/ui/services/tkinter_utils.py` — False Tier 0

**Phase 2 Claim**: Tier 0, MAJOR. "No unit test file imports this module directly. ... The existing `tests/unit/ui/services/test_tkinter_utils.py` may already cover some of these functions. Phase 1 import-matching missed the direct import. This is a false Tier 0 — needs verification."

**Evidence Reviewed**:
- Production file: `game/ui/services/tkinter_utils.py` (231 lines) — read in full
- **Test file EXISTS**: `tests/unit/ui/services/test_tkinter_utils.py` (217 lines) — read in full
- Import statement: `from game.ui.services import tkinter_utils` (line 12)

**Coverage confirmed**:

| Class | Tests | What's verified |
|---|---|---|
| `TestGetTkRoot` | 4 | SDL_VIDEODRIVER=dummy→None, TclError handling, RuntimeError handling, lazy init caches result (single Tk() call) |
| `TestIsTkinterAvailable` | 3 | Returns True on success, False on failure, False on dummy |
| `TestResetTkRoot` | 1 | Resets state + destroys root, new root different after re-init |
| `TestOpenSaveDialog` | 2 | Returns None when unavailable, calls filedialog with params |
| `TestOpenLoadDialog` | 1 | Returns None when unavailable |
| `TestPromptString` | 1 | Returns initialvalue fallback when unavailable |
| `TestCopyToClipboard` | 2 | Returns False when unavailable, clipboard_clear/append/update called |

_Total: 14 tests across 7 test classes. All 7 public functions tested._

**Verdict**: **DISPUTED** (as the Phase 2 report itself suspected)

The test file exists and has comprehensive coverage. Every public function is tested with happy paths and error handling. The module is Tier 2, not Tier 0. The Phase 1 import-matching missed this because the test imports via `from game.ui.services import tkinter_utils` (module-level import) rather than `from game.ui.services.tkinter_utils import get_tk_root` (from-import).

**Correct severity**: NO_ISSUE (false positive) — adequately tested.

**Note on coverage gaps**: The report's suggested tests (lines 97-101) are partially redundant:
- `test_get_tk_root_returns_none_on_dummy_display` → Already covered by `test_returns_none_when_sdl_dummy`
- `test_get_tk_root_lazy_initializes_shared_instance` → Already covered by `test_lazy_initialization_caches_result`
- `test_reset_tk_root_clears_state_and_destroys_old_root` → Already covered by `test_resets_state_for_reinitialize`
- `test_is_tkinter_available_triggers_lazy_init` → Already covered by `test_returns_true_when_initialized`

---

### F05: `game/ui/utils/pygame_utils.py` — No unit tests for math functions

**Phase 2 Claim**: Tier 0, MAJOR. "No unit test file imports this module. ... Half the functions are testable math utilities." 5 suggested tests for `create_centered_rect` and `calculate_ship_image_scale`.

**Evidence Reviewed**:
- Production file: `game/ui/utils/pygame_utils.py` (260 lines) — read in full
- **No test file directly imports `game.ui.utils.pygame_utils`** — CONFIRMED ✓
- **BUT**: `game/ui/utils/__init__.py` (lines 9-17) re-exports ALL 6 public functions from `pygame_utils.py`
- Test file: `tests/unit/ui/test_utils.py` (565 lines) imports from `game.ui.utils` — read in full

**Coverage confirmed via package re-export**:

| Function | Tests | Edge cases tested |
|---|---|---|
| `create_centered_rect` | 6 | centered horizontally/vertically, dimensions preserved, window larger than screen (negative offsets), odd-dimension integer rounding |
| `calculate_ship_image_scale` | 8 | basic scaling, visible_size parameter, manual_scale multiplier, visible_size=None fallback to max dimensions, visible_size=0 guard, tall images, 1x1 images, combined visible + manual_scale |
| `scale_and_rotate_image` | 7 | scale up/down, zero scale returns original, negative scale returns original, with rotation (90° swaps dimensions), specific angles 90/180/270, very small scale (0.01), very large scale (10.0) |
| `get_visible_bounding_box` | 4 | fully transparent→None, fully opaque→full rect, single opaque pixel→1x1 bbox, small 2x2 region→correct rect |
| `scale_image_by_visible_portion` | 6 | basic scaling, empty surface→placeholder, max_width constrains wide image, max_width aspect ratio preserved, tall image fits by height, backward compatible without max_width |
| `scale_image_to_fit` | 3 | target smaller than image, target larger than image, non-square aspect ratio preserved |
| `create_section_header` | 9 | default parameters, x offset, height override, container parameter, long text, wide width, tall height |

_Total: 43 test cases covering ALL 7 public functions with edge cases and error paths._

**Additional corroboration**: 2 test files mock/assert `create_section_header`: `test_empire_treasury_panel.py` (25 tests mock it as dependency), `test_race_environment_panel.py` (2 tests mock it), `test_race_summary_panel.py` (2 tests mock it), etc.

**Phase 2 report error**: The report listed `draw_text_with_background`, `draw_progress_bar`, and `draw_tooltip` as functions in `pygame_utils.py`. These functions DO NOT EXIST in the file. Only `draw_tooltip` exists in `game/ui/screens/builder/weapons_renderer.py`. The report attributed functions to the wrong module.

**Verdict**: **DISPUTED**

While no test file directly imports `game.ui.utils.pygame_utils`, ALL 7 public functions are tested through the package-level re-export at `game/ui/utils/__init__.py`. The test file `tests/unit/ui/test_utils.py` has 565 lines with 43 test cases covering every function with edge cases, error paths, and boundary conditions. This is a Phase 1 false negative caused by indirection through the package `__init__.py`.

**Correct severity**: NO_ISSUE (false positive) — adequately tested.

The Phase 2 report's suggested tests (lines 115-119) for `create_centered_rect` and `calculate_ship_image_scale` are already covered by the existing test suite.

---

## Summary

| # | Finding | Severity | Phase 2 Status | Verdict | Correct Severity |
|---|---|---|---|---|---|
| F01 | `seeker.py` — No dedicated tests | CRITICAL | Tier 0 | **CONFIRMED (nuanced)** | CRITICAL — integrated tested via golden test, but 6 code paths untested |
| F02 | `strategy_screen_order_editing.py` — No tests | MAJOR | Tier 0 | **DISPUTED** | NO_ISSUE — 183-line test file with 13 tests exists |
| F03 | `fleet_report_ctrl.py` — No tests | MAJOR | Tier 0 | **CONFIRMED** | MAJOR — indirect coverage only, core logic untested |
| F04 | `tkinter_utils.py` — No tests | MAJOR | Tier 0 | **DISPUTED** | NO_ISSUE — 217-line test file with 14 tests exists |
| F05 | `pygame_utils.py` — No tests for math functions | MAJOR | Tier 0 | **DISPUTED** | NO_ISSUE — 565-line test file with 43 tests via re-export |

**Disputed rate**: 4/5 (80%) — 3 findings were Phase 1 false negatives that Phase 2 failed to correct. Only `seeker.py` (CRITICAL) and `fleet_report_ctrl.py` (MAJOR) have genuine coverage gaps.

**Note on Phase 2 summary discrepancy**: The Phase 2 report header says "Major: 7" but only 4 findings are explicitly tagged as MAJOR in the body text. The remaining 3 may be Phase 1 classifications that Phase 2 implicitly downgraded during inspection. This verification covers the 4 explicitly-labeled MAJOR findings.

**Phase 1 root cause**: Import-matching missed coverage when:
1. Tests import modules using namespace syntax (`from package.orig_module import module as alias`)
2. Tests import through package `__init__.py` re-exports rather than submodule direct paths

**Phase 2 quality**: Weak. The Phase 2 agent reported 3 files as Tier 0 (no tests) that have existing, thorough test suites. Only the `seeker.py` CRITICAL finding was substantive, and even that failed to note the existing integration test coverage via `test_weapon_dispatch_golden.py`.

## Appendix: Untested Code Paths — genuinly absent tests

### seeker.py (6 paths)
1. `fire()` with target outside firing_arc → launch_vec from comp_facing (line 42)
2. `fire()` with target=None → launch_vec only (line 45 gate)
3. `fire()` with aim_vec.length() == 0 → fallback to launch_vec (line 50)
4. `fire()` with non-zero ship.velocity → p_vel incorporates velocity (line 53)
5. `WEAPON_REGISTRY` registration for WeaponFamily.SEEKER (line 73)
6. `facing_angle` non-zero computation path (lines 40-42)

### fleet_report_ctrl.py (4 paths)
1. `SplitFleetCommand` closure dispatch correctness (lines 37-49)
2. Dimension computation at 90% of screen (lines 33-34)
3. `_on_closed` clears window reference (lines 62-63)
4. `facade.handle_command()` routing through CQRS pipeline (line 49)
