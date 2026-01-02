# Legacy Code Removal Plan (Phase 7)

## Overview
This plan outlines the steps to remove all legacy code patterns identified during the Phase 6 Audit. The goal is to fully transition the codebase to the Component Ability System, removing backwards compatibility shims, legacy subclasses, and direct attribute access.

**Pre-requisites**: Phase 6 Data Migration must be confirmed complete (Verified).

---

## 1. Prioritization & Strategy
**Strategy**: "Migrate Usages First, Delete Definitions Last".
We must replace all `isinstance` checks and attribute access (`comp.damage`) with ability-based equivalents *before* we can safely remove the `Weapon`/`Engine` subclasses and `__getattr__` shims from `components.py`.

**Priority Levels**:
- **P0 (Critical)**: Bugs or logic that overwrites correct ability behavior (e.g., `ship_stats.py` shield bug).
- **P1 (Core Dependencies)**: Removal of `isinstance` checks in core logic (Combat, AI, Stats).
- **P2 (UI/Visualization)**: Removal of `isinstance` checks in UI, Rendering, and Builder.
- **P3 (Cleanup)**: Deletion of legacy subclasses, shims, and unused imports.

---

## 2. Detailed Task List

### Stage 1: Critical Fixes (P0)
These items are actively harmful or undermine the refactor.

- [ ] **Fix Shield Calculation Overwrite (`ship_stats.py`)**
    - *Issue*: Lines 325-330 overwrite the correct `ShieldProjection` aggregation with legacy dictionary lookups.
    - *Action*: Delete legacy lines 325-330.
- [ ] **Fix Legacy Armor Classification (`ship_stats.py`)**
    - *Issue*: Lines 72, 78, 182 check `comp.major_classification == "Armor"`.
    - *Action*: Replace with `comp.has_ability('ArmorAbility')` check.

### Stage 2: Migrate Core Logic (P1)
Refactor systems to stop using legacy patterns.

- [ ] **Combat System (`ship_combat.py`, `projectile_manager.py`)**
    - [ ] Replace `comp.damage`, `comp.range`, `comp.projectile_speed` access with `comp.get_ability('WeaponAbility').<attr>`.
    - [ ] Replace `comp.fire()` calls with `ability.fire()`.
    - [ ] Replace `beam_comp.calculate_hit_chance` logic in `collision_system.py`.
- [ ] **AI System (`ai.py`)**
    - [ ] Update `TargetEvaluator` to check `has_ability('WeaponAbility')` instead of `hasattr(c, 'damage')`.
    - [ ] Update PDC safety checks (`_stat_is_in_pdc_arc`) to use ability attributes for range/arc.
- [ ] **Ship Core (`ship.py`, `ship_stats.py`, `ship_physics.py`)**
    - [ ] Replace `isinstance(Sensor)`, `isinstance(Electronics)` checks with ability presense checks.
    - [ ] Remove `if hasattr(self, 'thrust_force')` style checks in `components.py` (if any logic depends on them internal to component).

### Stage 3: Migrate UI & Rendering (P2)
Refactor presentation layers.

- [ ] **Builder UI (`ui/builder/*.py`)**
    - [ ] Replace `isinstance(Weapon)` checks in `weapons_panel.py` and `schematic_view.py`.
    - [ ] Update `modifier_logic.py` to strictly read from ability dicts, removing any fallback to root data.
- [ ] **Battle UI & Rendering (`battle_ui.py`, `rendering.py`)**
    - [ ] Replace `isinstance` checks in debug overlays and status panels.
    - [ ] Update `rendering.py` color selection to use ability detection instead of `type_str`.

### Stage 4: Test Suite Updates (P1/P2)
Ensure tests pass without relying on legacy artifacts.

- [ ] **Component Tests (`test_components.py`)**
    - [ ] Remove `isinstance(Weapon)` assertions.
    - [ ] Update tests to check for ability presence.
- [ ] **Combat Tests (`test_combat.py`, `test_weapons.py`)**
    - [ ] Ensure mocks provide `WeaponAbility` instances, not just attributes on the component mock.

### Stage 5: The Big Delete (P3)
Once all usages are migrated, remove the definitions.

- [ ] **Clean `components.py`**
    - [ ] Remove `Weapon`, `Engine`, `Thruster`, `Shield`, `Bridge`, `Tank`, `Generator`, `Sensor`, `Electronics` subclasses.
    - [ ] Remove `_instantiate_abilities` legacy shim section (auto-creation from old keys).
    - [ ] Remove `__getattr__` shims (proxies for `damage`, `range`, `thrust_force`, etc.).
    - [ ] Remove `COMPONENT_TYPE_MAP`.
- [ ] **Clean Imports**
    - [ ] Remove unused imports of legacy subclasses across the entire codebase (`ship.py`, `ai.py`, etc.).
- [ ] **Remove Migration Scripts**
    - [ ] Delete `scripts/migrate_legacy_components.py` (optional, or archive it).

---

## 3. Verification Plan
1. **Regression Testing**: Run full test suite after each Stage.
2. **Visual Verification**: Check Ship Builder and Battle UI to ensure components appear and function correctly.
3. **Static Analysis**: Grep for `isinstance(`, `class Weapon`, `thrust_force` to ensure zero occurrences.

