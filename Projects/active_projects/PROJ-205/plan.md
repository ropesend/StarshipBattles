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
| 2. Legacy Code Path Eradication | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Code Hygiene Fixes | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-02-27
**Active Phase:** Phase 2
**Last Action:** Phase 1 complete - removed sprite_preview placeholder field
**Next Action:** Begin Phase 2 - Legacy Code Path Eradication
**Blockers:** None
**Baseline:** 12,835 passed, 1 skipped

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
**Status:** Not Started

#### Task 1.1: Remove sprite_preview from DesignMetadata [Simple]
**File:** `game/strategy/data/design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py`
- [ ] Remove field definition: `sprite_preview: Optional[str] = None` (line 41)
- [ ] Remove from `to_dict()`: `"sprite_preview": self.sprite_preview` (line 58)
- [ ] Remove from `from_dict()`: `sprite_preview=data.get("sprite_preview")` (line 85)
- [ ] Remove `Optional` from imports if no longer used
**Notes:**

#### Task 1.2: Update sprite_preview tests [Simple]
**File:** `tests/unit/strategy/test_design_metadata.py`
**Tests:** `pytest tests/unit/strategy/test_design_metadata.py`
- [ ] Delete test method `test_from_dict_sprite_preview_none` (~line 245)
- [ ] Delete test method `test_to_dict_includes_sprite_preview` (~line 501)
- [ ] Delete test method `test_to_dict_sprite_preview_none` (~line 511)
- [ ] Delete test method `test_roundtrip_preserves_sprite_preview` (~line 541)
- [ ] Update any other tests that include `sprite_preview` in their test data dicts
- [ ] Run tests: `pytest tests/unit/strategy/test_design_metadata.py -v`
**Notes:**

---

### Phase 2: Legacy Code Path Eradication [Medium]
**Objective:** Remove the legacy colonization path and the test-only `column_mgr` alias.
**Status:** Not Started

#### Task 2.1: Remove legacy colonization code path [Medium]
**File:** `game/strategy/engine/fleet_order_processor.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_order_processor.py tests/unit/strategy/engine/ tests/integration/strategy/ tests/integration/colonization/`
- [ ] Make `component_registry` parameter required (remove `Optional` and `= None` default) in `process_colonize()` signature (line 176)
- [ ] Remove legacy planet selection fallback: lines 242-244 (`else: final_planet = valid_candidates[0]`)
- [ ] Remove legacy fleet removal fallback: lines 276-278 (`else: empire.remove_fleet(fleet)`)
- [ ] Remove the `if component_registry is not None:` guard at line 249 (make the colony ship pre-check unconditional)
- [ ] Update `process_end_turn_orders()` caller at line 629 if needed (already passes registry)
- [ ] Update type annotation imports if `Optional` no longer needed for this param
**Notes:** 19 tests call without registry - all need updating in Task 2.2

#### Task 2.2: Update colonization tests to provide component_registry [Medium]
**Files:**
- `tests/unit/strategy/test_fleet_order_processor.py`
- `tests/unit/strategy/engine/test_process_colonize_validation.py`
- `tests/unit/strategy/engine/test_colonize_population.py`
- `tests/unit/strategy/test_engine_event_emission.py`
- `tests/integration/strategy/test_colonize_logic.py`
- `tests/integration/colonization/test_planet_specific_colonization.py`
**Tests:** `pytest tests/unit/strategy/test_fleet_order_processor.py tests/unit/strategy/engine/ tests/integration/strategy/ tests/integration/colonization/ -v`
- [ ] Add `component_registry` parameter to all 19 legacy test call sites (see Key Files reference for list)
- [ ] Delete explicit legacy test: `test_process_colonize_legacy_without_registry_still_works` (~line 325 in test_process_colonize_validation.py)
- [ ] Delete `test_process_colonize_without_registry_removes_fleet` (~line 662 in test_fleet_order_processor.py)
- [ ] Update remaining tests to use modern behavior (fleet kept when ships remain, only colony ship removed)
- [ ] Run full colonization test suite
**Notes:** Each test will need a mock or real component_registry. Follow pattern from existing registry-path tests (e.g., `test_process_colonize_with_registry_removes_ship` at line 574).

#### Task 2.3: Remove column_mgr test alias [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`
- [ ] Remove line 155: `self.column_mgr = self._column_manager  # Alias for tests`
- [ ] Fix comment on line 153-154: change "Store references for backward compatibility with tests" to "Store reference for scroll wheel handling"
- [ ] Keep `self.scroll_bar = self._virtual_table.scroll_bar` (line 154) - this IS production code
**Notes:**

#### Task 2.4: Update tests using column_mgr [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py -v`
- [ ] Replace all `win.column_mgr` references with `win._column_manager` (8 locations):
  - Line 111: `win.column_mgr = win._column_manager` → remove (unnecessary)
  - Line 112: `win.column_mgr.handle_header_clicks` → `win._column_manager.handle_header_clicks`
  - Line 113: `win.column_mgr.rebuild_headers` → `win._column_manager.rebuild_headers`
  - Line 1592: `assert win.column_mgr is not None` → `assert win._column_manager is not None`
  - Line 1597: `win.column_mgr.sort_column_id` → `win._column_manager.sort_column_id`
  - Line 1598: `win.column_mgr.sort_descending` → `win._column_manager.sort_descending`
  - Line 1609: `win.column_mgr.sort_column_id` → `win._column_manager.sort_column_id`
  - Line 1610: `win.column_mgr.sort_descending` → `win._column_manager.sort_descending`
- [ ] Run tests
**Notes:**

---

### Phase 3: Code Hygiene Fixes [Simple]
**Objective:** Fix branching structure, move import, rename comment.
**Status:** Not Started

#### Task 3.1: Restructure AbilityManager branching [Medium]
**File:** `game/simulation/components/ability_manager.py`
**Tests:** `pytest tests/unit/simulation/components/test_ability_manager.py tests/`
- [ ] In `get_abilities()` method, restructure the if/else at lines 54-66 so the MRO fallback only fires as a last resort when `isinstance()` returns False AND `target_class` was provided:
  ```python
  # Current (problematic - MRO walk runs for every non-match):
  if target_class and isinstance(ab, target_class):
      found.append(ab)
  else:
      for cls in ab.__class__.mro():  # runs even when target_class matched a different ability
          ...

  # Fixed (MRO walk only runs as fallback for identity drift):
  if target_class and isinstance(ab, target_class):
      found.append(ab)
  elif target_class is not None:
      # [KNOWN_ISSUE] Fallback for Module Identity Drift in tests.
      for cls in ab.__class__.mro():
          if cls.__name__ == ability_name:
              found.append(ab)
              break
  ```
- [ ] Keep the `[KNOWN_ISSUE]` comment block (lines 58-61) - this is documented tech debt
- [ ] Run ability manager tests
- [ ] Run full test suite to verify no regressions
**Notes:** The key change is adding `elif target_class is not None:` so the MRO walk ONLY fires when we had a target_class but isinstance failed (identity drift), not when iterating past non-matching abilities.

#### Task 3.2: Move runtime import to module level [Simple]
**File:** `game/simulation/components/component_stats_calculator.py`
**Tests:** `pytest tests/unit/simulation/components/`
- [ ] Move import from inside `calculate_modifier_stats()` (lines 50-53) to module level:
  ```python
  from game.simulation.components.modifiers import (
      apply_modifier_effects,
      get_default_stat_multipliers
  )
  ```
- [ ] Verify no circular import by running: `python -c "from game.simulation.components.component_stats_calculator import ComponentStatsCalculator"`
- [ ] Run tests
**Notes:** Verified no circular dependency - `modifiers.py` only imports `logging`.

#### Task 3.3: Rename misleading AI behavior comment [Simple]
**File:** `game/ai/behaviors.py`
**Tests:** No tests needed (comment-only change)
- [ ] Change section header at line 406 from `TEST-SPECIFIC BEHAVIORS` to `UTILITY BEHAVIORS`
- [ ] Verify no other references to "TEST-SPECIFIC" in the file
**Notes:** These behaviors are instantiated in every AIController and selectable via strategy data.

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` - 12,743 passed, 1 skipped (baseline)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] No new test failures introduced

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon)
- [ ] Verify baseline maintained: 12,743+ passed, 0 failures
- [ ] Review: no backward compatibility shims introduced

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
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
