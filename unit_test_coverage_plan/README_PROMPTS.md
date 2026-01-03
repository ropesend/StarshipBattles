# Unit Test Coverage Audit Prompts

Use the following prompts to instantiate independent agents for the code coverage review.

## Agent 1: Core Architecture Auditor

**Role:** Core Architecture QA Specialist
**Goal:** Achieve 100% Test Coverage for the Core Component System.
**Scope:**
- `components.py`
- `abilities.py`
- `ship.py`
- `component_modifiers.py`

**Instructions:**
1.  **Analyze Source:** Read the files in Scope to understand every class, method, and branch.
2.  **Map Tests:** Search `unit_tests/` (specifically `test_components.py`, `test_abilities.py`, `test_ship.py`, `test_ship_stats.py`) to map existing tests to source code.
3.  **Identify Gaps:** Find every line of code that is NOT covered by a test. Look for edge cases, error handling, and `if/else` branches.
4.  **Report:** Create a detailed report at `unit_test_coverage_plan/coverage_report_core.md`.
    -   **Section 1: Coverage Summary** (e.g., "abilities.py is 85% covered").
    -   **Section 2: Missing Tests** (List specific methods/branches).
    -   **Section 3: Plan** (Specific test cases needed to reach 100%).

---

## Agent 2: Simulation Engine Auditor

**Role:** Physics & Combat QA Specialist
**Goal:** Achieve 100% Test Coverage for the Physics and Combat Engine.
**Scope:**
- `ship_physics.py`
- `ship_combat.py`
- `projectiles.py`
- `collision_system.py`
- `battle_engine.py`

**Instructions:**
1.  **Analyze Source:** Read the files in Scope. Pay close attention to the "Shooting Loop", "Movement Physics", and "Collision Resolution".
2.  **Map Tests:** Search `unit_tests/` (`test_physics.py`, `test_combat.py`, `test_projectiles.py`, `test_collision_system.py`, `test_battle_engine_core.py`) to map coverage.
3.  **Identify Gaps:** Look for uncovered logic in thrust calculation, damage application, projectile lifecycle, and collision detection edge cases.
4.  **Report:** Create a detailed report at `unit_test_coverage_plan/coverage_report_simulation.md`.
    -   **Section 1: Coverage Summary**.
    -   **Section 2: Missing Tests**.
    -   **Section 3: Plan** (Specific test cases needed to reach 100%).

---

## Agent 3: AI & Behaviors Auditor

**Role:** AI Systems QA Specialist
**Goal:** Achieve 100% Test Coverage for AI Logic and Behaviors.
**Scope:**
- `ai.py`
- `ai_behaviors.py`
- `strategies/*.json` (Review logic implied by data)

**Instructions:**
1.  **Analyze Source:** Read `ai.py` and `ai_behaviors.py`. Understand the State Machine, Targeting Logic, and Maneuver execution (Kite, Ram, Orbit).
2.  **Map Tests:** Search `unit_tests/` (`test_ai.py`, `test_ai_behaviors.py`, `test_strategy_system.py`).
3.  **Identify Gaps:** Are all behavior states tested? Are all targeting criteria tested? Are edge cases (no targets, zero speed) covered?
4.  **Report:** Create a detailed report at `unit_test_coverage_plan/coverage_report_ai.md`.
    -   **Section 1: Coverage Summary**.
    -   **Section 2: Missing Tests**.
    -   **Section 3: Plan** (Specific test cases needed to reach 100%).

---

## Agent 4: UI & Builder System Auditor

**Role:** UI/UX QA Specialist
**Goal:** Achieve 100% Test Coverage for the Ship Builder and UI Logic.
**Scope:**
- `builder_gui.py`
- `ui/builder/*.py` (Recursively)
- `rendering.py`

**Instructions:**
1.  **Analyze Source:** Read `builder_gui.py` and the `ui/builder/` module. Focus on logic (state changes, data updates, validation), NOT just drawing calls.
2.  **Map Tests:** Search `unit_tests/` (`test_builder_*.py`, `test_ui_*.py`).
3.  **Identify Gaps:** Check if `_load_ship`, `_save_ship`, drag-and-drop validation, and panel updates are covered.
4.  **Report:** Create a detailed report at `unit_test_coverage_plan/coverage_report_ui.md`.
    -   **Section 1: Coverage Summary**.
    -   **Section 2: Missing Tests**.
    -   **Section 3: Plan** (Specific test cases needed to reach 100%).

---

## Agent 5: Data & Infrastructure Auditor

**Role:** Data Integrity QA Specialist
**Goal:** Achieve 100% Test Coverage for Data Persistence and Validation.
**Scope:**
- `ship_io.py`
- `ship_validator.py`
- `resources.py`

**Instructions:**
1.  **Analyze Source:** Read the files. Focus on JSON serialization/deserialization, rule validation (ShipDesignValidator), and resource logic.
2.  **Map Tests:** Search `unit_tests/` (`test_ship_loading.py`, `test_builder_validation.py`, `test_resources.py`).
3.  **Identify Gaps:** Check for error handling (corrupt files), missing fields, version migration, and complex validation rules.
4.  **Report:** Create a detailed report at `unit_test_coverage_plan/coverage_report_data.md`.
    -   **Section 1: Coverage Summary**.
    -   **Section 2: Missing Tests**.
    -   **Section 3: Plan** (Specific test cases needed to reach 100%).
