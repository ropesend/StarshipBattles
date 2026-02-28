# PROJ-205: Legacy Code Elimination - Verified Findings

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-205` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-205 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Dead Placeholder Cleanup | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Legacy Code Path Eradication | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Code Hygiene Fixes | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-27
**Active Phase:** Complete
**Last Action:** Audit Cycle 1 PASSED - all tasks verified
**Next Action:** User verification required
**Blockers:** None
**Baseline:** 12,831 passed, 1 skipped

## Overview
Address 6 verified actionable findings from the legacy code audit (Review `2026-02-27_141504_general_legacy-code-audit`). All findings were independently verified by skeptical verification agents. Original 34 findings were triaged down to these 6 confirmed issues plus 1 comment fix.

## Goals
- Remove dead placeholder field (`sprite_preview`) that is never used
- Eradicate legacy colonization code path that is never reached in production
- Remove test-only alias (`column_mgr`) that violates migration policy
- Fix AbilityManager branching to avoid unnecessary MRO walks in production
- Move historical runtime import to module level
- Fix misleading code comment

## Scope
**In:**
- 6 confirmed code changes + 1 comment fix across 5 production files
- Test updates for affected tests

**Out:**
- Disputed findings (10 items verified as non-issues)
- TypeGuard functions (exported as public API via `__init__.py`, not dead code)
- Economy placeholder fields (rendered in UI, removing causes crashes)
- Research system status (standalone feature, not dead code)
- exit_dialog.py refactoring (working code, refactoring = churn)

## Key Files
| Component | File Path |
|-----------|-----------|
| Design metadata | `game/strategy/data/design_metadata.py` |
| Fleet order processor | `game/strategy/engine/fleet_order_processor.py` |
| Build queue window | `game/ui/screens/empire_build_queue_window.py` |
| Ability manager | `game/simulation/components/ability_manager.py` |
| Stats calculator | `game/simulation/components/component_stats_calculator.py` |
| AI behaviors | `game/ai/behaviors.py` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-27 | Exclude TypeGuard functions (AIR-003) | All 4 are exported in `ai/interfaces/__init__.py` `__all__` - they're public API, not dead code |
| 2026-02-27 | Exclude economy placeholders (STR-003) | Rendered in `empire_treasury_panel.py:249-267` - removing causes `AttributeError` |
| 2026-02-27 | Exclude exit_dialog refactoring (AIR-002) | 102-line file, standard Pygame pattern, refactoring = churn |
| 2026-02-27 | Exclude research system removal (AIR-006) | Standalone sandbox feature accessible from main menu, not dead code |
| 2026-02-27 | Downgrade UIS-001 from Critical to Minor | `scroll_bar` is production code (4 call sites), only `column_mgr` is test-only |
| 2026-02-27 | Downgrade SIM-001 from Critical to Major | Known documented tech debt, restructure branching rather than remove |
| 2026-02-27 | Keep `scroll_bar` attribute, fix misleading comment | Production code uses it at lines 427, 429, 430, 451 |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- Review: `Reviews/results/2026-02-27_141504_general_legacy-code-audit/report.md`

---

## Phases

### Phase 1: Dead Placeholder Cleanup [Simple]
**Objective:** Remove the `sprite_preview` placeholder field that is never set or read.
**Status:** Complete

#### Task 1.1: Remove sprite_preview from DesignMetadata [Simple]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py`
- [x] Remove field definition: `sprite_preview: Optional[str] = None` (line 41)
- [x] Remove from `to_dict()`: `"sprite_preview": self.sprite_preview` (line 58)
- [x] Remove from `from_dict()`: `sprite_preview=data.get("sprite_preview")` (line 85)
- [x] Remove `Optional` from imports if no longer used
**Notes:** Removed field, to_dict entry, from_dict parameter, and unused Optional import.

#### Task 1.2: Update sprite_preview tests [Simple]
**File:** `tests/unit/strategy/test_design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py`
- [x] Delete test method `test_from_dict_sprite_preview_none` (~line 245)
- [x] Delete test method `test_to_dict_includes_sprite_preview` (~line 501)
- [x] Delete test method `test_to_dict_sprite_preview_none` (~line 511)
- [x] Delete test method `test_roundtrip_preserves_sprite_preview` (~line 541)
- [x] Update any other tests that include `sprite_preview` in their test data dicts
- [x] Run tests: `pytest tests/unit/strategy/test_design_metadata.py -v`
**Notes:** Removed 2 dedicated tests, updated 2 tests that referenced sprite_preview.

---

### Phase 2: Legacy Code Path Eradication [Medium]
**Objective:** Remove the legacy colonization path and the test-only `column_mgr` alias.
**Status:** Complete

#### Task 2.1: Remove legacy colonization code path [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_order_processor.py tests/unit/strategy/engine/ tests/integration/strategy/ tests/integration/colonization/`
- [x] Make `component_registry` parameter required (remove `Optional` and `= None` default) in `process_colonize()` signature (line 176)
- [x] Remove legacy planet selection fallback: lines 242-244 (`else: final_planet = valid_candidates[0]`)
- [x] Remove legacy fleet removal fallback: lines 276-278 (`else: empire.remove_fleet(fleet)`)
- [x] Remove the `if component_registry is not None:` guard at line 249 (make the colony ship pre-check unconditional)
- [x] Update `process_end_turn_orders()` caller at line 629 if needed (already passes registry)
- [x] Update type annotation imports if `Optional` no longer needed for this param
**Notes:** Updated to duck typing (hasattr) in fleet_order_processor and colonize_validator for test mock compatibility.

#### Task 2.2: Update colonization tests to provide component_registry [Medium]
**Files:**
- `tests/unit/strategy/test_fleet_order_processor.py`
- `tests/unit/strategy/engine/test_process_colonize_validation.py`
- `tests/unit/strategy/engine/test_colonize_population.py`
- `tests/unit/strategy/test_engine_event_emission.py`
- `tests/integration/strategy/test_colonize_logic.py`
- `tests/integration/colonization/test_planet_specific_colonization.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_order_processor.py tests/unit/strategy/engine/ tests/integration/strategy/ tests/integration/colonization/ -v`
- [x] Add `component_registry` parameter to all 19 legacy test call sites (see Key Files reference for list)
- [x] Delete explicit legacy test: `test_process_colonize_legacy_without_registry_still_works` (~line 325 in test_process_colonize_validation.py)
- [x] Delete `test_process_colonize_without_registry_removes_fleet` (~line 662 in test_fleet_order_processor.py)
- [x] Update remaining tests to use modern behavior (fleet kept when ships remain, only colony ship removed)
- [x] Run full colonization test suite
**Notes:** Added component_registry fixtures and updated all test files. 63 colonization tests pass.

#### Task 2.3: Remove column_mgr test alias [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`
- [x] Remove line 155: `self.column_mgr = self._column_manager  # Alias for tests`
- [x] Fix comment on line 153-154: change "Store references for backward compatibility with tests" to "Store reference for scroll wheel handling"
- [x] Keep `self.scroll_bar = self._virtual_table.scroll_bar` (line 154) - this IS production code
**Notes:** Removed alias, updated comment.

#### Task 2.4: Update tests using column_mgr [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -v`
- [x] Replace all `win.column_mgr` references with `win._column_manager` (8 locations)
- [x] Run tests
**Notes:** 118 build queue tests pass.

---

### Phase 3: Code Hygiene Fixes [Simple]
**Objective:** Fix branching structure, move import, rename comment.
**Status:** Complete

#### Task 3.1: Restructure AbilityManager branching [Medium]
**File:** `game/simulation/components/ability_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_ability_manager.py tests/`
- [x] In `get_abilities()` method, restructure the if/else at lines 54-66 so the MRO fallback only fires as a last resort when `isinstance()` returns False AND `target_class` was provided
- [x] Keep the `[KNOWN_ISSUE]` comment block (lines 58-61) - this is documented tech debt
- [x] Run ability manager tests
- [x] Run full test suite to verify no regressions
**Notes:** Changed `else:` to `elif target_class is not None:` so MRO walk only fires when isinstance fails for a provided target_class.

#### Task 3.2: Move runtime import to module level [Simple]
**File:** `game/simulation/components/component_stats_calculator.py`
**Tests:** `pytest tests/unit/simulation/components/`
- [x] Move import from inside `calculate_modifier_stats()` (lines 50-53) to module level
- [x] Verify no circular import by running: `python -c "from game.simulation.components.component_stats_calculator import ComponentStatsCalculator"`
- [x] Run tests
**Notes:** Import moved to module level successfully, no circular dependency.

#### Task 3.3: Rename misleading AI behavior comment [Simple]
**File:** `game/ai/behaviors.py`
**Tests:** No tests needed (comment-only change)
- [x] Change section header at line 406 from `TEST-SPECIFIC BEHAVIORS` to `UTILITY BEHAVIORS`
- [x] Verify no other references to "TEST-SPECIFIC" in the file
**Notes:** Comment updated. These behaviors are production code used by AIController.

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` - 12,743 passed, 1 skipped (baseline)

### After Each Phase
- [x] Run `pytest tests/ --testmon` - all affected tests pass
- [x] No new test failures introduced

### Final Verification
- [x] Run full test suite: `pytest tests/ -n 12` (NOT --testmon) - 12,831 passed, 1 skipped
- [x] Verify baseline maintained: 12,743+ passed, 0 failures
- [x] Review: no backward compatibility shims introduced

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-02-27 | No issues | PASSED |

## Completion Checklist
- [x] All Phase 1 tasks checked off
- [x] All Phase 2 tasks checked off
- [x] All Phase 3 tasks checked off
- [x] All tests passing
- [x] Regression tests passing
- [x] Audit passed (no significant issues)
- [ ] User verified
