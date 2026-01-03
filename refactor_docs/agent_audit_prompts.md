# Deep Dive Audit Prompts

Use the following prompts to instantiate independent agents for a final, comprehensive code review.

## Agent 1: Core Infrastructure Audit
**Role:** Senior Core Architect
**Task:** Audit the core component and ability definitions to ensure strict adherence to the Composition pattern.
**Context:** We have refactored from Inheritance (`Weapon` class) to Composition (`Component` + `WeaponAbility`).
**Focus Areas:** `components.py`, `abilities.py`, `component_modifiers.py`, `ship.py`, `resources.py`.
**Instructions:**
1.  **Scan `components.py`**:
    *   Confirm `Weapon`, `Engine`, `Shield` are strictly Aliases (or removed).
    *   Verify `Component.__init__` has NO "Legacy Shim" logic (e.g., `if 'damage' in data`).
    *   Check `has_pdc_ability` for fallback `abilities.get(...)` logic.
2.  **Scan `ship.py`**:
    *   Look for `SHIP_CLASSES` dictionary (Deprecated).
    *   Check `recalculate_stats` logic for any direct attribute setting.
3.  **Scan `abilities.py`**:
    *   Ensure ALL abilities use `recalculate()` to read from `component.stats`.
**Output:** Create `refactor_docs/audit_report_core_deep_dive.md`. List every file/line violation or "NO FINDINGS".

---

## Agent 2: Combat & Collision Audit
**Role:** Combat Systems Engineer
**Task:** Audit the combat loop to ensure it is 100% Ability-Driven.
**Focus Areas:** `ship_combat.py`, `projectile_manager.py`, `projectiles.py`, `collision_system.py`, `battle_engine.py`.
**Instructions:**
1.  **Check `fire_weapons` in `ship_combat.py`**:
    *   MUST use `comp.get_ability('WeaponAbility')`.
    *   MUST NOT read `comp.damage`, `comp.range`, `comp.reload_time`.
2.  **Check `Collision Logic`**:
    *   Damage application must come from the Projectile or Ability, never the Component instance directly.
3.  **Check `Projectile` instantiation**:
    *   Ensure it doesn't store the `source_component` and then read legacy attributes from it later.
**Output:** Create `refactor_docs/audit_report_combat_deep_dive.md`.

---

## Agent 3: Physics & Stats Audit
**Role:** Physics Engineer
**Task:** Audit movement and stat aggregation logic.
**Focus Areas:** `ship_physics.py`, `ship_stats.py`, `spatial.py`, `physics.py`.
**Instructions:**
1.  **Check `ShipPhysicsMixin`**:
    *   Verify thrust calculation iterates `CombatPropulsion` abilities, NOT `isinstance(c, Engine)`.
    *   Verify turn speed comes from `ManeuveringThruster` abilities.
2.  **Check `ShipStatsCalculator`**:
    *   Ensure aggregation loops use `comp.get_abilities(...)` or `comp.has_ability(...)`.
    *   Flag any use of `c.type` or `c.classification` for logic (OK for display).
**Output:** Create `refactor_docs/audit_report_physics_deep_dive.md`.

---

## Agent 4: AI & Behavior Audit
**Role:** AI Specialist
**Task:** Audit AI decision making for legacy assumptions.
**Focus Areas:** `ai.py`, `ai_behaviors.py`, `formation_editor.py`.
**Instructions:**
1.  **Check `determine_best_target`**:
    *   Range checks must use `WeaponAbility.range`.
    *   DPS calculations must sum ability logic.
2.  **Check Behaviors (Kite, Ram)**:
    *   Ensure they read `ship.max_weapon_range` (which should be ability-derived) and not `ship.components[0].range`.
3.  **Check `formation_editor.py`**:
    *   Ensure visualization logic doesn't crash on Components without legacy attributes.
**Output:** Create `refactor_docs/audit_report_ai_deep_dive.md`.

---

## Agent 5: UI & Builder Audit
**Role:** UI/UX Developer
**Task:** Audit the Ship Builder and Rendering systems.
**Focus Areas:** `builder_gui.py`, `ui/builder/*.py`, `rendering.py`.
**Instructions:**
1.  **Check `detail_panel.py`**:
    *   MUST iterate `comp.get_ui_rows()`.
    *   MUST NOT have huge `if isinstance(c, Weapon): show_damage()` blocks.
2.  **Check `rendering.py`**:
    *   Drawing turrets/engines should check `has_ability('WeaponAbility')`/`CombatPropulsion`.
    *   Avoid `isinstance` checks that rely on aliases.
3.  **Check `builder_gui.py`**:
    *   Flag imports of `Weapon`, `Engine` (should be `Component`).
**Output:** Create `refactor_docs/audit_report_ui_deep_dive.md`.

---

## Agent 6: Data Persistence Audit
**Role:** Data Engineer
**Task:** Audit JSON data and Save/Load logic.
**Focus Areas:** `data/components.json`, `ship_io.py`, `ship_validator.py`.
**Instructions:**
1.  **Scan `components.json`**:
    *   FAIL if any component has root-level `damage`, `range`, `thrust_force`.
    *   All functional stats must be inside `abilities: { ... }`.
2.  **Check `ship_io.py`**:
    *   Ensure `save_ship` does not "re-hydrate" legacy attributes into the JSON.
3.  **Check `ship_validator.py`**:
    *   Verify `LayerRestriction` uses `allow_abilities` NOT `allow_types`.
**Output:** Create `refactor_docs/audit_report_data_deep_dive.md`.

---

## Agent 7: Unit Test Integrity Audit
**Role:** QA Engineer
**Task:** Identify "False Positive" tests that work by accident or cheat.
**Focus Areas:** `unit_tests/*.py`.
**Instructions:**
1.  **Search for Mock Abuse**:
    *   `c = Mock(); c.damage = 10` -> **FAIL** (Components don't have .damage).
    *   `c.range = 500` -> **FAIL**.
2.  **Search for Legacy Constructors**:
    *   `Weapon(name="...")` -> **FAIL** (Should be `Component(data={...})`).
3.  **Search for Legacy Assertions**:
    *   `assertIsInstance(c, Weapon)` -> **FAIL**.
**Output:** Create `refactor_docs/audit_report_tests_deep_dive.md`.
