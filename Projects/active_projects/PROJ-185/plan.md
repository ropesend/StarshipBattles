# PROJ-185: Post-PROJ-174 Backward Compatibility Eradication

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-185` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-185 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Ghost Code & Comment Cleanup | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Remove Legacy Constant Aliases | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Remove Fleet Lookup Fallback | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Build Queue Single-Select Shim Removal | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-02-24
**Active Phase:** Phase 4 - Build Queue Single-Select Shim Removal
**Last Action:** Phase 3 Complete - Removed O(n) fallback in game_session.py, updated integration tests
**Next Action:** Execute Phase 4
**Blockers:** None
**Context for Next Agent:** Baseline is 12366 passed, 1 skipped. Pre-existing simulation_tests failures exist (unrelated to this project).

## Overview
Comprehensive cleanup of backward compatibility layers, ghost code, and misleading comments
discovered during independent audit of PROJ-174 (Registry Access Consolidation). While the
registry DI migration was verified clean, the audit uncovered broader backward compatibility
patterns across the codebase that violate the System Migration Policy.

## Goals
- Remove all backward compatibility code paths in production code
- Remove ghost code (stale comments, unused aliases, dead shims)
- Fix misleading comments that label proper patterns as "backward compatibility"
- Eliminate O(n) fallback lookup that undermines authoritative Galaxy registry
- Clean up ViewModel single-selection shim in build queue system

## Scope
**In:**
- Stale DeprecationWarning filter in test_protocols_boundary.py
- Legacy constant aliases in propulsion_scenarios.py
- Fleet lookup O(n) fallback in game_session.py
- Build queue ViewModel single-select shim removal
- Build queue Window test state exposure cleanup
- Misleading "backward compatibility" comments (6 locations)
- Production engine `turns_remaining` comment fix

**Out:**
- UI utils `__init__.py` re-exports (legitimate Python package API pattern)
- Test lab property delegates (dev tool, low priority)
- Build queue Window facade properties (proper encapsulation, not compat)
- Registry DI system changes (already clean)

## Key Files
| Component | File Path |
|-----------|-----------|
| DeprecationWarning filter | `tests/unit/core/test_protocols_boundary.py` |
| Propulsion legacy aliases | `simulation_tests/scenarios/propulsion_scenarios.py` |
| Fleet O(n) fallback | `game/strategy/engine/game_session.py` |
| Build queue ViewModel | `game/ui/screens/empire_build_queue_viewmodel.py` |
| Build queue Window | `game/ui/screens/empire_build_queue_window.py` |
| Build queue Window tests | `tests/unit/ui/screens/test_empire_build_queue_window.py` |
| Build queue ViewModel tests | `tests/unit/ui/screens/test_empire_build_queue_viewmodel.py` |
| Production engine | `game/strategy/engine/production_engine.py` |
| GameConfig | `game/strategy/engine/game_config.py` |
| UI utils init | `game/ui/utils/__init__.py` |
| Scenario base | `simulation_tests/scenarios/base.py` |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Keep UI utils __init__.py re-exports, fix comment only | Standard Python package API pattern, not backward compat |
| 2026-02-24 | Keep build queue Window facade properties, fix comments | Proper encapsulation (Law of Demeter) |
| 2026-02-24 | Remove ViewModel single-select shim, migrate callers | Clean-sheet: multi-select is authoritative |
| 2026-02-24 | Remove build queue test state exposure (lines 109-135) | Tests should use public API |
| 2026-02-24 | `turns_remaining` is NOT legacy - fix comment | Actively used by 6+ UI files |
| 2026-02-24 | GameConfig race fields are sparse serialization, not compat | Fix misleading comment |

---

## Phases

### Phase 1: Ghost Code & Comment Cleanup [Simple]
**Objective:** Remove stale code references and fix misleading comments
**Status:** Not Started

#### Task 1.1: Remove stale DeprecationWarning filter [Simple]
**File:** `tests/unit/core/test_protocols_boundary.py`
**Tests:** `pytest tests/unit/core/test_protocols_boundary.py`
- [ ] Remove stale docstring text at line 6: `PROJ-174: Uses deprecated get_default_registries() in fixture.`
- [ ] Remove stale pytestmark at lines 11-12:
  ```python
  # PROJ-174: Suppress deprecation warnings - fixture uses deprecated API
  pytestmark = pytest.mark.filterwarnings("ignore::DeprecationWarning")
  ```
- [ ] Remove stale comment at line 33: `# PROJ-181: Use IRegistryProvider instead of deprecated get_default_registries()`
- [ ] Verify tests still pass

#### Task 1.2: Fix misleading comment in UI utils [Simple]
**File:** `game/ui/utils/__init__.py`
**Tests:** `pytest tests/unit/ui/test_utils.py`
- [ ] Change line 8 from `# Re-export pygame utilities for backward compatibility` to `# Public API - re-export pygame utilities from submodule`

#### Task 1.3: Fix misleading comment in GameConfig [Simple]
**File:** `game/strategy/engine/game_config.py`
**Tests:** `pytest tests/unit/strategy/`
- [ ] Change line 85 from `# Only include race fields if set (backwards compatibility)` to `# Only include optional race fields when set (sparse serialization)`

#### Task 1.4: Fix misleading comment in production engine [Simple]
**File:** `game/strategy/engine/production_engine.py`
**Tests:** `pytest tests/unit/strategy/`
- [ ] Change line 336 from `# Update legacy "turns_remaining" for UI display (approximate)` to `# Calculate turns_remaining for UI display (approximate)`

#### Task 1.5: Fix misleading comment in ability extraction map [Simple]
**File:** `simulation_tests/scenarios/base.py`
**Tests:** `pytest simulation_tests/`
- [ ] Change line 70 from `'key': 'weapon',  # backward compat: data['weapon'] for beam scenarios` to `'key': 'weapon',  # data['weapon'] for beam scenarios`

#### Task 1.6: Fix misleading comment in build queue window [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`
- [ ] Change line 196 section comment from `# Properties for backward compatibility` to `# Public API facade (delegates to ViewModel)`

---

### Phase 2: Remove Legacy Constant Aliases [Simple]
**Objective:** Remove unused backward compat aliases in propulsion scenarios
**Status:** Not Started

#### Task 2.1: Remove propulsion legacy aliases [Simple]
**File:** `simulation_tests/scenarios/propulsion_scenarios.py`
**Tests:** `pytest simulation_tests/ -n 12`
- [ ] Remove the entire legacy aliases block (lines 257-280), including section header comment
- [ ] Confirmed: zero external consumers (only defined within same file, never imported elsewhere)
- [ ] Run full simulation tests to verify

---

### Phase 3: Remove Fleet Lookup O(n) Fallback [Simple]
**Objective:** Make Galaxy registry the sole authoritative source for fleet lookups
**Status:** Not Started

#### Task 3.1: Remove O(n) fleet iteration fallback [Simple]
**File:** `game/strategy/engine/game_session.py`
**Tests:** `pytest tests/unit/strategy/ -n 12`
- [ ] Remove fallback code at lines 231-235:
  ```python
  # Fallback to O(n) iteration (for backward compatibility)
  for emp in self.empires:
      for f in emp.fleets:
          if f.id == fleet_id:
              return f
  ```
- [ ] Simplify method comment: remove "Try O(1) registry lookup first" (line 226) since it's now the only path. Change to `# O(1) Galaxy registry lookup`
- [ ] Keep the `return None` at the end
- [ ] Verify all strategy tests pass

---

### Phase 4: Build Queue Single-Select Shim Removal [Medium]
**Objective:** Remove the single-selection backward compatibility shim from ViewModel and clean up test state exposure in Window
**Status:** Not Started

#### Task 4.1: Remove test state exposure from Window [Simple]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`
- [ ] Remove comment + line 109-110:
  ```python
  # Expose state for backward compatibility with tests
  self.columns = self._filter_mgr.columns
  ```
- [ ] Check if `self.columns` is used within Window class itself; if yes, keep as `self._columns` (private)
- [ ] Remove lines 131-135:
  ```python
  # Expose sidebar button dicts for test compatibility
  self.column_toggle_buttons = self._sidebar.column_toggle_buttons
  self.filter_toggle_buttons = self._sidebar.filter_toggle_buttons
  self.search_entry = self._sidebar.search_entry
  self.btn_apply_filters = self._sidebar.btn_apply_filters
  ```
- [ ] If tests reference these attributes, add proper read-only properties with docstrings
- [ ] Verify tests pass (may need updates - see Task 4.5)

#### Task 4.2: Remove single-select shim from ViewModel [Medium]
**File:** `game/ui/screens/empire_build_queue_viewmodel.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_viewmodel.py`
- [ ] Remove `self._selected_index: int = -1` (line 81)
- [ ] Remove `self._selected_source: Optional[BuildQueueSource] = None` (line 82)
- [ ] Remove `selected_index` property (lines 114-117)
- [ ] Remove `selected_source` property (lines 119-122)
- [ ] Remove single-select sync block in `select_row()` (lines 215-222)
- [ ] Update event emission at line 224-227: remove `selected_source` from payload, keep only `selected_indices`
- [ ] Remove single-select reset in `_refresh()` (lines 260-261)
- [ ] `get_selected_sources()` method stays (already uses `selected_indices`)
- [ ] Clean up any unused imports (Optional may become unused)

#### Task 4.3: Update Window facade properties [Medium]
**File:** `game/ui/screens/empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`
- [ ] Rewrite `selected_source` property (line 210-212) as derived:
  ```python
  @property
  def selected_source(self) -> Optional[BuildQueueSource]:
      """Single selected source, or None if zero/multiple selected."""
      sources = self._viewmodel.get_selected_sources()
      return sources[0] if len(sources) == 1 else None
  ```
- [ ] Rewrite `selected_index` property (lines 214-217) as derived:
  ```python
  @property
  def selected_index(self) -> int:
      """Single selected index, or -1 if zero/multiple selected."""
      indices = self._viewmodel.selected_indices
      return next(iter(indices)) if len(indices) == 1 else -1
  ```
- [ ] These convenience properties remain on Window (proper facade) but no longer depend on ViewModel shim fields
- [ ] Update internal usage at line 433 if needed

#### Task 4.4: Update ViewModel test assertions [Medium]
**File:** `tests/unit/ui/screens/test_empire_build_queue_viewmodel.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_viewmodel.py`
- [ ] Migrate `vm.selected_index == N` assertions → `vm.selected_indices == {N}` or `N in vm.selected_indices`
- [ ] Migrate `vm.selected_index == -1` assertions → `vm.selected_indices == set()`
- [ ] Migrate `vm.selected_source is X` assertions → `vm.get_selected_sources() == [X]`
- [ ] Migrate `vm.selected_source is None` assertions → `vm.get_selected_sources() == []`
- [ ] Run tests to verify all pass

#### Task 4.5: Update Window test assertions [Simple]
**File:** `tests/unit/ui/screens/test_empire_build_queue_window.py`
**Tests:** `pytest tests/unit/ui/screens/test_empire_build_queue_window.py`
- [ ] Window keeps `selected_source` and `selected_index` as derived properties, so most assertions stay
- [ ] Update any tests referencing `win.column_toggle_buttons`, `win.filter_toggle_buttons`, `win.search_entry`, `win.btn_apply_filters` to use proper accessors (from Task 4.1)
- [ ] Run tests to verify all pass

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/ -n 12` - 12366 passed, 1 skipped (baseline established)

### After Each Phase
- [ ] Run `pytest tests/ --testmon` - all affected tests pass
- [ ] No new DeprecationWarnings introduced
- [ ] No misleading backward compatibility comments remain in modified files

### Final Verification
- [ ] Run full test suite: `pytest tests/ -n 12` (NOT --testmon, full verification)
- [ ] Run simulation tests: `pytest simulation_tests/ -n 12`
- [ ] Grep for "backward compat" / "backwards compat" in production code - only legitimate uses remain
- [ ] No stale PROJ-174 references remain

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [ ] All Phase 1 tasks checked off
- [ ] All Phase 2 tasks checked off
- [ ] All Phase 3 tasks checked off
- [ ] All Phase 4 tasks checked off
- [ ] All tests passing
- [ ] Regression tests passing
- [ ] Audit passed (no significant issues)
- [ ] User verified
