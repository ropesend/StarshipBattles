# Unit Test Creation Master Plan

**Status:** Draft
**Goal:** Achieve 100% Code Coverage and Verify System Stability.
**Based on:** Independent Code Reviews (Jan 2026).

## Executive Summary

This plan consolidates the findings from 5 independent audit agents. We have identified specific gaps in Data Persistence, Core Simulation Logic, AI Behaviors, and UI Integration. The work is prioritized to address **Stability & Data Integrity** first, followed by **Gameplay Logic**, and finally **UI/Visuals**.

---

## Phase 1: High-Risk Stability & Data Integrity (Immediate)

**Focus:** Prevention of crashes, data corruption, and invalid states.
**Target Modules:** `ship_io.py`, `ship_validator.py`, `builder_gui.py` (IO flows).

### 1.1. Data Persistence (`unit_tests/test_io_interactive.py`)
*   **New File**: Create `unit_tests/test_io_interactive.py`.
*   [ ] `test_save_ship_success`: Mock `filedialog` and `open`. Verify JSON structure.
*   [ ] `test_save_ship_failure`: Mock permission errors. Verify error handling return values.
*   [ ] `test_load_ship_corrupt`: Mock invalid JSON. Verify graceful failure.
*   [ ] `test_load_ship_GUI_flow`: In `test_builder_io_integration.py`, verify GUI allows user to see error messages.

### 1.2. Complex Validation Rules (`unit_tests/test_builder_validation.py`)
*   **Extension**: Add `TestComplexRules` class.
*   [ ] `test_class_requirements`: Ship with insufficient Crew/LifeSupport triggers `ClassRequirementsRule` error.
*   [ ] `test_resource_dependency`: Ship with Ammo consumer but no Ammo storage triggers warning.
*   [ ] `test_layer_restrictions`: Verify "Block" logic for specific component types in layers.

### 1.3. Ship Class Mutation (`unit_tests/test_ship.py`)
*   **Extension**: Add `TestShipClassMutation`.
*   [ ] `test_change_class_migration`: Verify components migrate to valid layers or are removed when reference hull changes from "Frigate" to "Destroyer".
*   [ ] `test_derelict_status_logic`: Verify `is_derelict` update logic when key components are destroyed.

---

## Phase 2: Core Simulation & Physics Logic

**Focus:** Gameplay correctness, "Shooting Loop" integrity, and Physics accuracy.
**Target Modules:** `abilities.py`, `ship_combat.py`, `ship_physics.py`.

### 2.1. Abilities & Formulas (`unit_tests/test_abilities_advanced.py`)
*   **New File**: Create `unit_tests/test_abilities_advanced.py`.
*   [ ] `test_firing_solution_arcs`: Verify target acquisition at 0°, 359°, and boundary angles.
*   [ ] `test_beam_accuracy_sigmoid`: Verify hit chance formula `1 / (1 + exp(-x))` at various ranges.
*   [ ] `test_weapon_damage_formula`: Verify `damage="=10 + range"` dynamic parsing.

### 2.2. Combat Logic (`unit_tests/test_combat.py`)
*   **Extension**: Add `TestCombatFlow`.
*   [ ] `test_firing_solution_lead`: Test `solve_lead` with perpendicular target vectors.
*   [ ] `test_fire_weapons_creates_projectiles`: Verification that `fire_weapons` returns valid `Projectile` or `Beam` objects with correct stats.
*   [ ] `test_special_armor_interactions`: Test `EmissiveArmor` (flat reduction) vs `CrystallineArmor`.

### 2.3. Physics Integration (`unit_tests/test_physics.py`)
*   **Extension**: Add `TestPhysicsIntegration`.
*   [ ] `test_ability_driven_thrust`: Verify `update_physics_movement` increases speed based on `CombatPropulsion.thrust_force`.
*   [ ] `test_mass_dampening`: Verify heavier ships accelerate slower with same thrust (F=ma).

---

## Phase 3: AI Intelligence & Behaviors

**Focus:** Bot behavior correctness and edge-case handling.
**Target Modules:** `ai.py`, `ai_behaviors.py`.

### 3.1. Targeting Rules (`unit_tests/test_targeting_rules.py`)
*   **New File**: Create `unit_tests/test_targeting_rules.py`.
*   [ ] `test_target_evaluator_sorting`: Verify `fastest`, `slowest`, `largest`, `most_damaged`, `least_armor`.
*   [ ] `test_pdc_arc_logic`: Verify targets are ignored if outside PDC specific firing arcs.

### 3.2. Advanced Behaviors (`unit_tests/test_advanced_behaviors.py`)
*   **New File**: Create `unit_tests/test_advanced_behaviors.py`.
*   [ ] `test_orbit_behavior`: Verify vector points tangent to target circle.
*   [ ] `test_flee_behavior`: Verify vector points away from threat.
*   [ ] `test_multiplex_targeting_flow`: Verify `find_secondary_targets` logic in AI Controller.

---

## Phase 4: UI Polish & Visuals

**Focus:** User experience and visual feedback correctness.
**Target Modules:** `detail_panel.py`, `rendering.py`, `layer_panel.py`.

### 4.1. Visual Feedback (`unit_tests/test_rendering_logic.py`)
*   **Extension**: Add `TestVisualFeedback`.
*   [ ] `test_component_coloring`: Verify drawing color logic (Weapon=Red, Prop=Green) via mocked `draw.circle`.

### 4.2. Drag & Drop Realism (`unit_tests/test_builder_drag_drop_real.py`)
*   **New File**: Create `unit_tests/test_builder_drag_drop_real.py`.
*   [ ] `test_layer_drop_mapping`: Verify pixel coordinates map to correct `Layer` object.
*   [ ] `test_drop_rejection`: Verify invalid drops trigger UI feedback.

### 4.3. HTML Generation (`unit_tests/test_detail_panel_rendering.py`)
*   **New File**: Create `unit_tests/test_detail_panel_rendering.py`.
*   [ ] `test_html_stats_generation`: Verify generated HTML string contains correct data values and tags.

---

## QA & Verification Standard

For every Phase:
1.  **Implement Tests**: Create the specified test files.
2.  **Run Tests**: `python -m pytest unit_tests/test_name.py`.
3.  **Fix Bugs**: If tests fail (revealing actual bugs), fix the source code.
4.  **Regression**: Run full suite `python -m pytest unit_tests/`.
5.  **Coverage Check**: (Optional) Run coverage tool to confirm gap closure.
