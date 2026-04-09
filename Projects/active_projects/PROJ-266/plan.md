# PROJ-266: Critical UI Screen Test Coverage

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-266` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-266 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. BattleResultsScreen (0% coverage) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. NewGameSetupScreen extended (30% coverage) | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Combat Lab pure function extraction | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-04-09
**Active Phase:** Planning Complete
**Last Action:** Plan written with source analysis
**Next Action:** Begin Phase 1 implementation
**Blockers:** None
**Context for Next Agent:** All three phases create new test files only -- no production code changes. Phase 1 and 2 require pygame mocking. Phase 3 tests pure functions that can be called directly without pygame. Existing test patterns in `tests/unit/ui/test_battle_results_data.py` and `tests/unit/ui/test_new_game_setup.py` provide reference for mock structure.

## Overview
Three critical UI screens have 0-30% test coverage despite being user-facing code paths exercised in every game session. This project adds targeted tests for testable logic and state management in these screens, focusing on behavior that can be verified without pixel-level rendering checks. The data extraction layer (`battle_results_data.py`) is already 100% covered; this project covers the display screen and two Combat Lab UI modules.

## Goals
- Bring `battle_results_screen.py` from 0% to meaningful coverage of its testable logic
- Extend `new_game_setup_screen.py` coverage beyond the static methods (currently 30.2%) to include UI state management
- Extract and test pure functions from Combat Lab `renderer.py` (6.8%) and `test_run_details.py` (5.2%)

## Scope
**In:**
- Testing `BattleResultsScreen` initialization, state management, event routing, scroll logic, return navigation
- Testing `NewGameSetupScreen` UI state: player count changes, empire visibility, race display updates, start button validation, error states
- Testing `TestLabRenderer._format_check_pair()` and `_is_condition_verified()` as pure functions
- Testing `TestRunDetailsPanel._draw_numeric_difference()` skip logic and phase grouping logic

**Out:**
- Pixel-level rendering verification (asserting exact pixel positions, colors on surfaces)
- Testing pygame internals (font rendering, surface blitting)
- Refactoring production code (this project is test-only)
- Testing `battle_results_data.py` (already 100% covered in `tests/unit/ui/test_battle_results_data.py`)
- Testing Combat Lab `formatting_utils.py` (separate, small module -- already has clear behavior)

## Key Files Reference
| Component | File Path | Coverage | Notes |
|-----------|-----------|----------|-------|
| Battle Results Screen | `game/ui/screens/battle_results_screen.py` | 0% (167 stmts) | 279 LOC, IScene protocol |
| Battle Results Data | `game/ui/screens/battle_results_data.py` | 100% | Already covered -- provides test fixtures |
| New Game Setup Screen | `game/ui/screens/new_game_setup_screen.py` | 30.2% (281 stmts) | 645 LOC, pygame_gui UIWindow |
| Existing Setup Tests | `tests/unit/ui/test_new_game_setup.py` | -- | Tests static methods only |
| Combat Lab Renderer | `game/ui/screens/test_lab/renderer.py` | 6.8% (1193 LOC) | `_format_check_pair`, `_is_condition_verified` |
| Combat Lab Run Details | `game/ui/screens/test_lab/test_run_details.py` | 5.2% (957 LOC) | `_draw_numeric_difference`, phase grouping |
| Formatting Utils | `game/ui/screens/test_lab/formatting_utils.py` | -- | Used by test_run_details, already clear |

## Test Files Created
| Test File | Phase | Tests |
|-----------|-------|-------|
| `tests/unit/ui/screens/test_battle_results_screen.py` | 1 | ~12-15 tests |
| `tests/unit/ui/screens/test_new_game_setup_extended.py` | 2 | ~12-15 tests |
| `tests/unit/test_lab/test_renderer_pure_functions.py` | 3 | ~15-20 tests |

## Testing Strategy

### Pygame Mocking Approach (Phases 1 and 2)
Both `BattleResultsScreen` and `NewGameSetupScreen` depend on pygame/pygame_gui. The test strategy is:

1. **Mock pygame.Surface** for draw calls -- we do not assert pixel content, only that methods are called without error
2. **Mock pygame events** for event handling tests -- construct event objects and verify state changes
3. **Mock pygame_gui elements** (Phase 2) -- verify element show/hide/kill calls on UI state changes
4. **Use real data objects** -- `BattleResults`, `ShipResult`, `TeamSummary` are frozen dataclasses that need no mocking
5. **Focus on state transitions** -- scroll offsets, button rect computation, callback invocation, visibility toggling

### Pure Function Approach (Phase 3)
The Combat Lab functions are either `@staticmethod` or have logic that can be tested by:
1. Calling `_format_check_pair()` directly as a static method (no instance state needed)
2. Calling `_is_condition_verified()` with constructed string/dict arguments (no pygame dependency in logic)
3. Testing `_draw_numeric_difference()` skip logic by checking return value (y_offset unchanged = skipped)

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- `Reviews/results/2026-04-08_test-review/final_report.md` - Source review that identified coverage gaps

---

## Detailed Phase Analysis

### Phase 1: BattleResultsScreen (0% -> meaningful coverage)
**File:** `game/ui/screens/battle_results_screen.py` (279 LOC, 167 stmts)

This is an IScene protocol implementation shown after every battle. The data extraction is 100% covered by `test_battle_results_data.py`, but the display screen has zero coverage.

**Testable logic (no rendering assertions needed):**
1. **`__init__`** -- stores screen dimensions, results, callback; initializes scroll offsets to 0
2. **`_hp_color()`** -- module-level pure function mapping HP percentage to color tuple
3. **`_handle_scroll()`** -- scroll offset management based on mouse x position (left vs right column)
4. **`_trigger_return()`** -- invokes scene_callback with correct destination from results
5. **`handle_event()`** -- routes mouse clicks to return button, scroll events to columns, keyboard escape/enter to return
6. **`handle_resize()`** -- updates stored dimensions
7. **`_draw_footer()`** -- return button text varies by `return_destination` ("test_lab", "battle_setup", "strategy", unknown)
8. **Ship sorting** -- ships filtered by team_id for column assignment (in `draw()`)

**Not worth testing (pure rendering):**
- `_draw_header()`, `_draw_team_column()`, `_draw_ship_card()` -- all surface.blit/draw.rect calls

### Phase 2: NewGameSetupScreen extended (30% -> broader coverage)
**File:** `game/ui/screens/new_game_setup_screen.py` (645 LOC, 281 stmts)

The existing tests in `tests/unit/ui/test_new_game_setup.py` cover only static/class methods: `validate_save_name`, `build_game_config`, `generate_default_save_name`, `get_player_count_options`. The actual screen UI behavior is untested.

**Testable logic (via mock pygame_gui):**
1. **`_update_empire_visibility()`** -- shows/hides UI elements based on player_count; clears race for hidden players
2. **`_update_race_display()`** -- updates preview label text, theme label, hides name input when race selected
3. **`process_event()` routing** -- dropdown change updates `player_count`/`galaxy_type`, slider updates `system_count`, button press routes correctly
4. **`_on_start_clicked()`** -- validates save name, collects empire names (race name vs manual input), builds config, calls callback or shows error
5. **`_on_race_selected()`** / `_on_race_created()`** -- sets player race, updates display, clears modal state
6. **`_on_race_dialog_cancelled()`** -- clears modal state without changing race
7. **`_on_cancel_clicked()`** -- calls cancel callback and kills window
8. **Galaxy type / system count state** -- dropdown and slider update internal state

### Phase 3: Combat Lab Pure Functions
Two files with extractable pure logic:

**`renderer.py` -- `_format_check_pair()` (lines 1094-1130):**
- `@staticmethod` -- no instance needed
- Handles: both None, booleans, both numeric (precision by magnitude), mixed/string types
- Precision tiers: >=10000 -> 1 decimal, >=1 -> 4 decimals, <1 -> 6 decimals

**`renderer.py` -- `_is_condition_verified()` (lines 783-864):**
- Takes condition_text string + validation_results list of dicts
- Direct mapping lookup (pattern -> validation_name, check status == 'PASS')
- Special case: Range Penalty regex parsing with float arithmetic verification
- Returns bool

**`test_run_details.py` -- `_draw_numeric_difference()` skip logic (line 487-530):**
- Non-numeric types return y_offset unchanged (skip)
- Boolean types return y_offset unchanged (skip -- bool is int subclass)
- Numeric difference computation: exact match, essentially exact, percentage, zero expected

**`test_run_details.py` -- Phase grouping logic (lines 354-391):**
- Groups validation results by 'phase' key ('data', 'precondition', 'outcome')
- Default phase is 'outcome' when key missing or unrecognized
- Skips empty phase groups

---

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-09 | Test-only project, no production code changes | Focus is test coverage, not refactoring |
| 2026-04-09 | Use frozen dataclasses as real fixtures (not mocked) | `BattleResults` etc. are simple value objects -- mocking them adds complexity without benefit |
| 2026-04-09 | Mock pygame.Surface and fonts, not rendering output | Pixel-level assertions are brittle and test pygame internals, not our logic |
| 2026-04-09 | Test `_draw_numeric_difference` via skip/no-skip behavior | The rendering half of the method is pygame-only; the decision logic (skip or compute) is testable |
| 2026-04-09 | Put Combat Lab tests in `tests/unit/test_lab/` | Matches existing test location pattern (`tests/unit/test_lab/test_viewmodel.py` etc.) |

---

## Verification Checklist

### Project Start (REQUIRED)
- [ ] Run full test suite: `pytest tests/ -n 12` -- all tests pass (baseline)
- [ ] Note test count for comparison

### After Each Phase
- [ ] Run new test file -- all pass
- [ ] Run `pytest tests/ --testmon` -- no regressions

### Final Verification
- [ ] Run full test suite: `python Tools/test_sharded/test_sharded.py`
- [ ] Verify test count increased by ~40-50 tests
- [ ] Verify no new test failures
- [ ] All three test files exist and pass independently

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All tests passing
- [ ] Test count increased
- [ ] User verified
