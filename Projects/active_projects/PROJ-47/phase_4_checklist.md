# Phase 4: External Documentation Updates

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-47 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Fix broken links and add missing sections to docs/*.md files

---

## Tasks

### Task 4.1: Fix PROJ-11 Links (DOC-001) [Simple]
**File:** `docs/ARCHITECTURE.md`
**Tests:** Verify links work

- [ ] Line 151: Change `active_projects/PROJ-11` -> `archived_projects/PROJ-11`
- [ ] Line 152: Change `active_projects/PROJ-11` -> `archived_projects/PROJ-11`
- [ ] Verify: Open links and confirm they resolve

**Notes:**

---

### Task 4.2: Add API Reference to modifier_system.md (DOC-004) [Medium]
**File:** `docs/modifier_system.md`
**Tests:** N/A (markdown)

- [ ] Add new section `## API Reference` after existing content with:
  - **ModifierEffectEvaluator** class methods:
    - `evaluate_modifier(mod_def, param_value) -> List[ModifierEffect]`
    - `validate_formula(formula) -> List[str]`
  - **ModifierEffect** dataclass fields:
    - stat_key, value, operation, target_ability, source_modifier_id, formula_str, param_value
  - **ModifierIntrospection** class methods:
    - `get_modifier_affects(mod_def, component, param_value) -> dict`
    - `get_component_modifier_summary(component) -> dict`
    - `generate_ability_stats_display(ability) -> List[dict]`
    - `generate_modifier_tooltip(mod_def, param_value, component) -> str`
  - **apply_modifier_effects** function signature
- [ ] Verify: File renders correctly

**Notes:**

---

### Task 4.3: Add Error Handling Section to adding_abilities.md (DOC-008) [Medium]
**File:** `docs/adding_abilities.md`
**Tests:** N/A (markdown)

- [ ] Add new section `## Common Errors and Solutions` after Checklist with:
  - **Missing STAT_BINDINGS**: Error - modifiers have no effect. Solution - define STAT_BINDINGS list
  - **Invalid StatKey**: Error - KeyError. Solution - use StatKey enum, not strings
  - **Missing Base Attribute**: Error - AttributeError: '_base_damage'. Solution - store base values in __init__
  - **Ability Not Found**: Error - KeyError on component load. Solution - register in ABILITY_REGISTRY
  - **recalculate() Not Called**: Error - stats not updating. Solution - call apply_stat_bindings()
- [ ] Verify: File renders correctly

**Notes:**

---

### Task 4.4: Add MVVM Pattern Section (DOC-009) [Simple]
**File:** `docs/NAMING_CONVENTIONS.md`
**Tests:** N/A (markdown)

- [ ] Add new section `## MVVM Pattern - ViewModel Naming` with:
  - Convention: ViewModel classes use `*_viewmodel.py` suffix
  - Example: `workshop_viewmodel.py` contains `WorkshopViewModel`
  - ViewModel responsibilities: holds screen state, emits events, no pygame code
  - Related files: `*_context.py`, `*_event_router.py`, `*_data_loader.py`
  - When to create: complex screens with multiple panels sharing state
- [ ] Verify: File renders correctly

**Notes:**

---

### Task 4.5: Document Stat Resolution Order (DOC-010) [Simple]
**File:** `docs/adding_abilities.md`
**Tests:** N/A (markdown)

- [ ] Add subsection `### Stat Resolution Order` to Step 5 section with:
  - Resolution priority:
    1. `ability_stats[ClassName][stat_key]` (targeted modifier effects)
    2. `component.stats[stat_key]` (global component stats)
    3. Default value (*_mult -> 1.0, *_add -> 0.0, other -> None)
  - Code example showing usage with defaults
  - Targeted vs Global effects explanation
- [ ] Verify: File renders correctly

**Notes:**

---

### Task 4.6: Add Layer Iteration Documentation (DOC-011) [Medium]
**File:** `docs/adding_abilities.md`
**Tests:** N/A (markdown)

- [ ] Add new section `## Working with Ship Layers` before Step 7 with:
  - Layer structure: `ship.layers = {LayerType: {'components': [Component, ...]}}`
  - Common iteration patterns with code examples
  - `ship.get_components_by_ability('WeaponAbility', operational_only=True)`
  - LayerType reference (HULL, INTERNAL, EXTERNAL, WEAPONS)
  - Ability access: `comp.has_ability()`, `comp.get_ability()`
- [ ] Verify: File renders correctly

**Notes:**

---

### Task 4.7: Add FleetMovementSimulator Migration Guide (DOC-07) [Medium]
**File:** `game/strategy/engine/fleet_movement.py`
**Tests:** `python -m py_compile game/strategy/engine/fleet_movement.py`

- [ ] Expand module docstring with migration guide:
  - Before/After code examples
  - API mapping table:
    | Old Method | New Method | Notes |
    |------------|------------|-------|
    | FleetMovementSimulator.project_path() | FleetNavigationService.project_path() | Same signature |
    | FleetMovementSimulator.calculate_path() | FleetNavigationService.compute_path() | Uses NavigationState |
    | FleetState | NavigationState | Immutable (frozen) |
  - Key differences: NavigationState is immutable, includes can_warp field
  - Removal timeline: Deprecated in PROJ-35, removal in future release
- [ ] Verify: Run py_compile

**Notes:**

---

### Task 4.8: UI Method Docstrings (DOC-12) [Medium]
**Files:** Multiple UI files
**Tests:** `python -m py_compile <file>`

- [ ] Add docstring to `draw_debug_overlay()` in `game/ui/screens/battle_screen.py` (line 142)
  - Document: target lines, weapon ranges, aim points, firing arcs
- [ ] Add docstring to `draw_debug_overlay()` in `game/ui/hud/battle.py` (line 118)
- [ ] Add docstring to `_create_ui()` in `game/ui/screens/new_game_setup_screen.py` (line 72)
- [ ] Add docstring to `_create_ui()` in `game/ui/screens/builder/main.py` (line 135)
- [ ] Add docstring to `_create_ui()` in `game/ui/screens/workshop_screen.py` (line 161)
- [ ] Add docstring to `handle_event()` in `game/ui/screens/strategy_input_handler.py` (line 28)
- [ ] Verify: Run py_compile on all modified files

**Notes:**

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Run `pytest tests/` (full suite) - all tests pass
- [ ] Verify PROJ-11 links work in ARCHITECTURE.md
- [ ] Verify docs/component_system.md exists and renders
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to `Project Complete`
