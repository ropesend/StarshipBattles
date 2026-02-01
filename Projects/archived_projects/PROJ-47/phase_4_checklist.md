# Phase 4: External Documentation Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-47 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Fix broken links and add missing sections to docs/*.md files

---

## Tasks

### Task 4.1: Fix PROJ-11 Links (DOC-001) [Simple]
**File:** `docs/ARCHITECTURE.md`
**Tests:** Verify links work

- [x] Line 238-239: Changed `active_projects/PROJ-11` -> `archived_projects/PROJ-11`
- [x] Verify: Links resolve to archived project files

**Notes:** Links now point to Projects/archived_projects/PROJ-11/ which contains plan.md and design.md

---

### Task 4.2: Add API Reference to modifier_system.md (DOC-004) [Medium]
**File:** `docs/modifier_system.md`
**Tests:** N/A (markdown)

- [x] Add new section `## API Reference` after existing content with:
  - **ModifierEffectEvaluator** class methods
  - **ModifierEffect** dataclass fields
  - **ModifierIntrospection** class methods
  - **apply_modifier_effects** function signature
- [x] Verify: File renders correctly

**Notes:** Added comprehensive API reference with signatures and docstrings

---

### Task 4.3: Add Error Handling Section to adding_abilities.md (DOC-008) [Medium]
**File:** `docs/adding_abilities.md`
**Tests:** N/A (markdown)

- [x] Add new section `## Common Errors and Solutions` after Checklist with:
  - **Missing STAT_BINDINGS**: Error - modifiers have no effect. Solution - define STAT_BINDINGS list
  - **Invalid StatKey**: Error - KeyError. Solution - use StatKey enum, not strings
  - **Missing Base Attribute**: Error - AttributeError: '_base_damage'. Solution - store base values in __init__
  - **Ability Not Found**: Error - KeyError on component load. Solution - register in ABILITY_REGISTRY
  - **recalculate() Not Called**: Error - stats not updating. Solution - call apply_stat_bindings()
- [x] Verify: File renders correctly

**Notes:** Added error solutions section with code examples

---

### Task 4.4: Add MVVM Pattern Section (DOC-009) [Simple]
**File:** `docs/NAMING_CONVENTIONS.md`
**Tests:** N/A (markdown)

- [x] Add new section `## MVVM Pattern - ViewModel Naming` with:
  - Convention: ViewModel classes use `*_viewmodel.py` suffix
  - Example: `workshop_viewmodel.py` contains `WorkshopViewModel`
  - ViewModel responsibilities: holds screen state, emits events, no pygame code
  - Related files: `*_context.py`, `*_event_router.py`, `*_data_loader.py`
  - When to create: complex screens with multiple panels sharing state
- [x] Verify: File renders correctly

**Notes:** Added complete MVVM naming conventions section

---

### Task 4.5: Document Stat Resolution Order (DOC-010) [Simple]
**File:** `docs/adding_abilities.md`
**Tests:** N/A (markdown)

- [x] Add subsection `### Stat Resolution Order` to Step 5 section with:
  - Resolution priority documented
  - Code example showing usage with defaults
  - Targeted vs Global effects explanation
- [x] Verify: File renders correctly

**Notes:** Added stat resolution order after Step 5 with priority list and examples

---

### Task 4.6: Add Layer Iteration Documentation (DOC-011) [Medium]
**File:** `docs/adding_abilities.md`
**Tests:** N/A (markdown)

- [x] Add new section `## Working with Ship Layers` before Step 7 with:
  - Layer structure documentation
  - Common iteration patterns with code examples
  - `ship.get_components_by_ability()` usage
  - LayerType reference (HULL, INTERNAL, EXTERNAL, WEAPONS)
  - Ability access: `comp.has_ability()`, `comp.get_ability()`
- [x] Verify: File renders correctly

**Notes:** Added comprehensive Working with Ship Layers section

---

### Task 4.7: Add FleetMovementSimulator Migration Guide (DOC-07) [Medium]
**File:** `game/strategy/services/fleet_navigation_service.py` (original file deleted in PROJ-42)
**Tests:** `python -m py_compile game/strategy/services/fleet_navigation_service.py`

- [x] Expand module docstring with migration guide:
  - Before/After code examples
  - API mapping table
  - Key differences: NavigationState is immutable, includes can_warp field
  - Removal timeline: Deprecated in PROJ-35, removed in PROJ-42
- [x] Verify: py_compile passed

**Notes:** Added migration guide to fleet_navigation_service.py since fleet_movement.py was removed

---

### Task 4.8: UI Method Docstrings (DOC-12) [Medium]
**Files:** Multiple UI files
**Tests:** `python -m py_compile <file>`

- [x] Enhanced docstring for `draw_debug_overlay()` in `game/ui/screens/battle_screen.py`
  - Documented: target lines, weapon ranges, aim points, firing arcs
- [x] Enhanced docstring for `draw_debug_overlay()` in `game/ui/hud/battle.py`
- [x] `_create_ui()` in `game/ui/screens/new_game_setup_screen.py` - already had docstring
- [x] Added docstring to `_create_ui()` in `game/ui/screens/builder/main.py`
- [x] Added docstring to `_create_ui()` in `game/ui/screens/workshop_screen.py`
- [x] `handle_event()` in `game/ui/screens/strategy_input_handler.py` - already had docstring
- [x] Verify: py_compile passed on all modified files

**Notes:** Some methods already had basic docstrings, enhanced draw_debug_overlay with element details

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Run `pytest tests/` (full suite) - 5499 passed (pre-existing UI failures in PROJ-48 scope)
- [x] Verify PROJ-11 links work in ARCHITECTURE.md - points to archived_projects
- [x] Verify docs/component_system.md exists and renders - created in Phase 3
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to `Project Complete`
