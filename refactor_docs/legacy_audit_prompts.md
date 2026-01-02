# Legacy Code Audit - Agent Prompts

> **Goal**: Independent review to identify and remove ALL legacy code patterns from the inheritance-based component system.
> **Output**: Each agent produces a report in `refactor_docs/audit_[area].md`

---

## Agent 1: Core Components & Abilities

**Focus Area**: `components.py`, `abilities.py`, `resources.py`, `component_modifiers.py`, `formula_system.py`

**Prompt**:
```
Review the following files for legacy code that should be removed after the Component Ability System refactor:
- c:\Dev\Starship Battles\components.py
- c:\Dev\Starship Battles\abilities.py  
- c:\Dev\Starship Battles\resources.py
- c:\Dev\Starship Battles\component_modifiers.py
- c:\Dev\Starship Battles\formula_system.py

LEGACY PATTERNS TO FIND:
1. `isinstance(comp, Engine)`, `isinstance(comp, Weapon)`, `isinstance(comp, Shield)`, `isinstance(comp, Thruster)` - should use `has_ability()` or `get_abilities()`
2. Direct attribute access like `comp.thrust_force`, `comp.damage`, `comp.range` - should use ability values
3. Type checks using `type_str == "Engine"` or similar string comparisons
4. Legacy subclass methods that duplicate ability functionality
5. Comments mentioning "legacy", "shim", "deprecated", "Phase X" that indicate temporary code
6. Imports of subclasses that are no longer needed
7. Legacy property shims that delegate to abilities but are marked for removal

FOR EACH FINDING:
- File and line number
- The problematic code snippet
- Why it's legacy
- Recommended fix (remove, refactor, or keep with justification)

Write a detailed report to: c:\Dev\Starship Battles\refactor_docs\audit_core_components.md
```

---

## Agent 2: Combat System

**Focus Area**: `ship_combat.py`, `battle_engine.py`, `battle.py`, `collision_system.py`, `projectiles.py`, `projectile_manager.py`

**Prompt**:
```
Review the combat system files for legacy code patterns:
- c:\Dev\Starship Battles\ship_combat.py
- c:\Dev\Starship Battles\battle_engine.py
- c:\Dev\Starship Battles\battle.py
- c:\Dev\Starship Battles\collision_system.py
- c:\Dev\Starship Battles\projectiles.py
- c:\Dev\Starship Battles\projectile_manager.py

LEGACY PATTERNS TO FIND:
1. `isinstance(comp, Weapon)`, `isinstance(comp, SeekerWeapon)`, `isinstance(comp, BeamWeapon)`, `isinstance(comp, ProjectileWeapon)` - should use `has_ability('WeaponAbility')` or specific ability checks
2. Direct weapon attribute access: `comp.damage`, `comp.range`, `comp.reload_time`, `comp.firing_arc` - if not coming from ability instances
3. `isinstance(comp, Shield)`, `isinstance(comp, Engine)` checks in damage or propulsion logic
4. Legacy weapon firing logic that bypasses ability cooldowns
5. Direct `comp.fire()` calls that should use ability-based firing
6. Any `PointDefense` legacy flag checks vs `has_pdc_ability()` or tag checks
7. Legacy projectile creation that reads weapon stats from non-ability sources

FOR EACH FINDING:
- File and line number  
- The problematic code
- Classification: MUST_FIX / SHOULD_FIX / ACCEPTABLE_SHIM
- Recommended action

Write report to: c:\Dev\Starship Battles\refactor_docs\audit_combat_system.md
```

---

## Agent 3: Ship Core System

**Focus Area**: `ship.py`, `ship_stats.py`, `ship_physics.py`

**Prompt**:
```
Review the ship core files for legacy component patterns:
- c:\Dev\Starship Battles\ship.py
- c:\Dev\Starship Battles\ship_stats.py
- c:\Dev\Starship Battles\ship_physics.py

LEGACY PATTERNS TO FIND:
1. `isinstance(c, Engine)` - should use `c.has_ability('CombatPropulsion')`
2. `isinstance(c, Thruster)` - should use `c.has_ability('ManeuveringThruster')`
3. `isinstance(c, Shield)` - should use `c.has_ability('ShieldProjection')`
4. `isinstance(c, Weapon)` - should use `c.has_ability('WeaponAbility')`
5. Direct attribute access: `c.thrust_force`, `c.turn_speed`, `c.shield_capacity`
6. Legacy stat calculation methods that duplicate ability aggregation
7. Any `get_total_ability_value()` calls that have fallback isinstance checks
8. Legacy imports: `from components import Engine, Weapon, Shield, Thruster`
9. Comments mentioning Phase 3/4 temporary code

FOR EACH FINDING:
- File, line, code snippet
- Is this blocking legacy removal? YES/NO
- Recommended fix

Write report to: c:\Dev\Starship Battles\refactor_docs\audit_ship_core.md
```

---

## Agent 4: AI & Behaviors System

**Focus Area**: `ai.py`, `ai_behaviors.py`

**Prompt**:
```
Review AI system for legacy component patterns:
- c:\Dev\Starship Battles\ai.py
- c:\Dev\Starship Battles\ai_behaviors.py

LEGACY PATTERNS TO FIND:
1. `isinstance(comp, Weapon)` - should use `has_ability('WeaponAbility')`
2. `isinstance(comp, Engine)` or `isinstance(comp, Thruster)` - should use ability checks
3. Direct `comp.range`, `comp.damage`, `comp.firing_arc` access vs ability values
4. Legacy `PointDefense` ability dict checks vs `has_pdc_ability()` or tag system
5. Weapon type checks like `isinstance(comp, SeekerWeapon)`
6. AI targeting that reads from component attributes instead of abilities
7. Formation integrity checks using legacy component types
8. Legacy imports from components module

FOR EACH FINDING:
- File, line, code 
- Impact on AI behavior if removed
- Fix priority: HIGH/MEDIUM/LOW

Write report to: c:\Dev\Starship Battles\refactor_docs\audit_ai_system.md
```

---

## Agent 5: Ship Builder UI (Part 1 - Core Panels)

**Focus Area**: `ui/builder/detail_panel.py`, `ui/builder/layer_panel.py`, `ui/builder/left_panel.py`, `ui/builder/right_panel.py`

**Prompt**:
```
Review Builder UI panels for legacy component patterns:
- c:\Dev\Starship Battles\ui\builder\detail_panel.py
- c:\Dev\Starship Battles\ui\builder\layer_panel.py  
- c:\Dev\Starship Battles\ui\builder\left_panel.py
- c:\Dev\Starship Battles\ui\builder\right_panel.py

LEGACY PATTERNS TO FIND:
1. `isinstance(comp, Engine)`, `isinstance(comp, Weapon)`, `isinstance(comp, Shield)` for display logic
2. Direct attribute access for UI display: `comp.damage`, `comp.thrust_force`, `comp.range`
3. `type_str` checks like `if comp.type_str == "Engine":`
4. Legacy hardcoded component type strings for colors/icons
5. UI that should use `get_ui_rows()` but reads attributes directly
6. Legacy imports: `from components import Engine, Weapon, ...`
7. Component categorization using type instead of abilities

FOR EACH FINDING:
- File, line, problematic code
- UI impact if changed
- Recommended fix

Write report to: c:\Dev\Starship Battles\refactor_docs\audit_builder_ui_panels.md
```

---

## Agent 6: Ship Builder UI (Part 2 - Weapons & Modifiers)

**Focus Area**: `ui/builder/weapons_panel.py`, `ui/builder/modifier_logic.py`, `ui/builder/modifier_row.py`, `ui/builder/schematic_view.py`

**Prompt**:
```
Review Builder weapons and modifier UI for legacy patterns:
- c:\Dev\Starship Battles\ui\builder\weapons_panel.py
- c:\Dev\Starship Battles\ui\builder\modifier_logic.py
- c:\Dev\Starship Battles\ui\builder\modifier_row.py
- c:\Dev\Starship Battles\ui\builder\schematic_view.py

LEGACY PATTERNS TO FIND:
1. `isinstance(comp, Weapon)` or subclass checks for weapon filtering
2. Direct weapon attribute access: `comp.damage`, `comp.range`, `comp.firing_arc`, `comp.reload_time`
3. `isinstance(comp, ProjectileWeapon)`, `isinstance(comp, BeamWeapon)`, `isinstance(comp, SeekerWeapon)`
4. Modifier logic reading from legacy attributes instead of ability values
5. Schematic view using type checks for rendering
6. Weapon stats that should read from ability dicts post-migration
7. Arc visualization using legacy `firing_arc` attribute

FOR EACH FINDING:
- File, line, code
- Is this read-only display or mutable logic?
- Fix approach

Write report to: c:\Dev\Starship Battles\refactor_docs\audit_builder_weapons.md
```

---

## Agent 7: Battle UI & Rendering

**Focus Area**: `battle_ui.py`, `battle_panels.py`, `rendering.py`, `battle_setup.py`

**Prompt**:
```
Review battle UI for legacy component patterns:
- c:\Dev\Starship Battles\battle_ui.py
- c:\Dev\Starship Battles\battle_panels.py
- c:\Dev\Starship Battles\rendering.py
- c:\Dev\Starship Battles\battle_setup.py

LEGACY PATTERNS TO FIND:
1. `isinstance(comp, Weapon)` for weapon status display
2. `isinstance(comp, Engine)`, `isinstance(comp, Shield)` for status panels
3. Direct attribute access for UI values
4. Color/visual selection based on component type instead of abilities
5. Weapon tooltips reading legacy attributes
6. Debug overlays using isinstance checks
7. Battle setup using legacy component types

FOR EACH FINDING:
- File, line, code
- Visual impact
- Fix recommendation

Write report to: c:\Dev\Starship Battles\refactor_docs\audit_battle_ui.md
```

---

## Agent 8: Data & Validation

**Focus Area**: `ship_validator.py`, `ship_io.py`, `data/components.json`, `data/vehicleclasses.json`, `data/modifiers.json`

**Prompt**:
```
Review data validation and I/O for legacy patterns:
- c:\Dev\Starship Battles\ship_validator.py
- c:\Dev\Starship Battles\ship_io.py
- c:\Dev\Starship Battles\data\components.json
- c:\Dev\Starship Battles\data\vehicleclasses.json
- c:\Dev\Starship Battles\data\modifiers.json

LEGACY PATTERNS TO FIND:
1. Validation rules using `isinstance` checks
2. Type-based validation that should use abilities
3. components.json entries with legacy root-level attributes that should be in ability dicts
4. vehicleclasses.json requirements referencing legacy component types
5. Modifier restrictions using component type instead of ability presence
6. Save/load serialization assuming legacy attribute locations
7. Any vestiges of Phase 6 migration incomplete

FOR EACH FINDING:
- File, line/entry, issue
- Data integrity impact
- Fix required

Write report to: c:\Dev\Starship Battles\refactor_docs\audit_data_validation.md
```

---

## Agent 9: Unit Tests - Components & Abilities

**Focus Area**: `unit_tests/test_components.py`, `unit_tests/test_abilities.py`, `unit_tests/test_component_composition.py`, `unit_tests/test_legacy_shim.py`, `unit_tests/test_component_modifiers_extended.py`, `unit_tests/test_component_resources.py`, `unit_tests/test_component_formulas.py`

**Prompt**:
```
Review component-related unit tests for legacy patterns:
- c:\Dev\Starship Battles\unit_tests\test_components.py
- c:\Dev\Starship Battles\unit_tests\test_abilities.py
- c:\Dev\Starship Battles\unit_tests\test_component_composition.py
- c:\Dev\Starship Battles\unit_tests\test_legacy_shim.py
- c:\Dev\Starship Battles\unit_tests\test_component_modifiers_extended.py
- c:\Dev\Starship Battles\unit_tests\test_component_resources.py
- c:\Dev\Starship Battles\unit_tests\test_component_formulas.py

LEGACY PATTERNS TO FIND:
1. Tests that explicitly test legacy shim behavior - should these be removed?
2. `isinstance` assertions for component types
3. Tests reading from `comp.data.get('range')` vs `comp.range` after migration
4. MockComponents that don't have ability instances
5. Tests that would break if legacy subclasses were removed
6. Assertions on legacy attribute paths

FOR EACH FINDING:
- File, test name, line
- Is test still valid? YES/NO/NEEDS_UPDATE
- Recommended action

Write report to: c:\Dev\Starship Battles\refactor_docs\audit_tests_components.md
```

---

## Agent 10: Unit Tests - Weapons & Combat

**Focus Area**: `unit_tests/test_weapons.py`, `unit_tests/test_combat.py`, `unit_tests/test_combat_endurance.py`, `unit_tests/test_pdc.py`, `unit_tests/test_multitarget.py`, `unit_tests/test_projectiles.py`, `unit_tests/test_collision_system.py`, `unit_tests/test_shields.py`, `unit_tests/test_firing_arc_logic.py`

**Prompt**:
```
Review combat-related unit tests for legacy patterns:
- c:\Dev\Starship Battles\unit_tests\test_weapons.py
- c:\Dev\Starship Battles\unit_tests\test_combat.py
- c:\Dev\Starship Battles\unit_tests\test_combat_endurance.py
- c:\Dev\Starship Battles\unit_tests\test_pdc.py
- c:\Dev\Starship Battles\unit_tests\test_multitarget.py
- c:\Dev\Starship Battles\unit_tests\test_projectiles.py
- c:\Dev\Starship Battles\unit_tests\test_collision_system.py
- c:\Dev\Starship Battles\unit_tests\test_shields.py
- c:\Dev\Starship Battles\unit_tests\test_firing_arc_logic.py

LEGACY PATTERNS TO FIND:
1. Mock weapons without proper ability instances
2. Tests using `isinstance(comp, Weapon)` assertions
3. Reading `comp.data.get()` for migrated attributes
4. Tests that bypass ability system for weapon stats
5. PDC tests using legacy PointDefense flag vs has_pdc_ability()
6. Shield tests using legacy capacity attribute

FOR EACH FINDING:
- File, test, line
- Test validity status
- Fix needed

Write report to: c:\Dev\Starship Battles\refactor_docs\audit_tests_combat.md
```

---

## Agent 11: Unit Tests - Ship & Physics

**Focus Area**: `unit_tests/test_ship.py`, `unit_tests/test_ship_stats.py`, `unit_tests/test_ship_physics_mixin.py`, `unit_tests/test_ship_resources.py`, `unit_tests/test_physics.py`, `unit_tests/test_resources.py`

**Prompt**:
```
Review ship and physics unit tests for legacy patterns:
- c:\Dev\Starship Battles\unit_tests\test_ship.py
- c:\Dev\Starship Battles\unit_tests\test_ship_stats.py
- c:\Dev\Starship Battles\unit_tests\test_ship_physics_mixin.py
- c:\Dev\Starship Battles\unit_tests\test_ship_resources.py
- c:\Dev\Starship Battles\unit_tests\test_physics.py
- c:\Dev\Starship Battles\unit_tests\test_resources.py

LEGACY PATTERNS TO FIND:
1. Tests using `isinstance(c, Engine)` for engine detection
2. Tests checking `c.thrust_force` attribute directly vs ability value
3. Tests that would break if Engine/Thruster classes were just Component
4. Resource tests using legacy consumption patterns
5. Stats tests with isinstance-based component filtering

FOR EACH FINDING:
- File, test, line
- Blocks legacy removal? YES/NO
- Fix

Write report to: c:\Dev\Starship Battles\refactor_docs\audit_tests_ship_physics.md
```

---

## Agent 12: Unit Tests - AI & Battle

**Focus Area**: `unit_tests/test_ai.py`, `unit_tests/test_ai_behaviors.py`, `unit_tests/test_battle_engine_core.py`, `unit_tests/test_battle_scene.py`, `unit_tests/test_movement_and_ai.py`, `unit_tests/test_strategy_system.py`, `unit_tests/test_formation_editor_logic.py`

**Prompt**:
```
Review AI and battle unit tests for legacy patterns:
- c:\Dev\Starship Battles\unit_tests\test_ai.py
- c:\Dev\Starship Battles\unit_tests\test_ai_behaviors.py
- c:\Dev\Starship Battles\unit_tests\test_battle_engine_core.py
- c:\Dev\Starship Battles\unit_tests\test_battle_scene.py
- c:\Dev\Starship Battles\unit_tests\test_movement_and_ai.py
- c:\Dev\Starship Battles\unit_tests\test_strategy_system.py
- c:\Dev\Starship Battles\unit_tests\test_formation_editor_logic.py

LEGACY PATTERNS TO FIND:
1. AI tests mocking weapons without ability instances
2. Tests using isinstance for targeting logic
3. Formation tests with legacy engine/thruster checks
4. Battle engine tests with legacy component type assumptions
5. Strategy tests assuming legacy weapon attributes

FOR EACH FINDING:
- File, test, line
- Impact on test validity
- Fix approach

Write report to: c:\Dev\Starship Battles\refactor_docs\audit_tests_ai_battle.md
```

---

## Agent 13: Unit Tests - Builder UI

**Focus Area**: `unit_tests/test_builder_*.py` (all builder tests), `unit_tests/test_modifier_*.py`

**Prompt**:
```
Review all builder UI unit tests for legacy patterns:
- c:\Dev\Starship Battles\unit_tests\test_builder_improvements.py
- c:\Dev\Starship Battles\unit_tests\test_builder_interaction.py
- c:\Dev\Starship Battles\unit_tests\test_builder_logic.py
- c:\Dev\Starship Battles\unit_tests\test_builder_refactor.py
- c:\Dev\Starship Battles\unit_tests\test_builder_structure_features.py
- c:\Dev\Starship Battles\unit_tests\test_builder_ui_sync.py
- c:\Dev\Starship Battles\unit_tests\test_builder_validation.py
- c:\Dev\Starship Battles\unit_tests\test_builder_warning_logic.py
- c:\Dev\Starship Battles\unit_tests\test_modifier_defaults_robustness.py
- c:\Dev\Starship Battles\unit_tests\test_modifier_logic.py
- c:\Dev\Starship Battles\unit_tests\test_modifier_propagation.py
- c:\Dev\Starship Battles\unit_tests\test_modifier_row.py
- c:\Dev\Starship Battles\unit_tests\test_modifiers.py
- c:\Dev\Starship Battles\unit_tests\test_new_modifiers.py

LEGACY PATTERNS TO FIND:
1. Tests using isinstance for component filtering in UI
2. Modifier tests reading legacy attribute paths
3. Builder tests with hardcoded component type assumptions
4. UI sync tests expecting legacy data structure
5. Validation tests using type-based rules

FOR EACH FINDING:
- File, test, line
- Test still needed? YES/NO
- Fix or remove

Write report to: c:\Dev\Starship Battles\refactor_docs\audit_tests_builder.md
```

---

## Agent 14: Main Entry Points & Integration

**Focus Area**: `main.py`, `builder.py`, `builder_gui.py`, `builder_components.py`, `formation_editor.py`

**Prompt**:
```
Review main entry points and integration for legacy patterns:
- c:\Dev\Starship Battles\main.py
- c:\Dev\Starship Battles\builder.py
- c:\Dev\Starship Battles\builder_gui.py
- c:\Dev\Starship Battles\builder_components.py
- c:\Dev\Starship Battles\formation_editor.py

LEGACY PATTERNS TO FIND:
1. Game initialization using legacy component types
2. Scene transitions with isinstance checks
3. Ship creation/loading using legacy patterns
4. Formation editor with legacy engine/thruster assumptions
5. Legacy imports at module level
6. Hardcoded component type strings

FOR EACH FINDING:
- File, line, code
- Runtime impact
- Fix priority: CRITICAL/HIGH/MEDIUM/LOW

Write report to: c:\Dev\Starship Battles\refactor_docs\audit_integration.md
```

---

## Summary Checklist

After all agents complete, assess reports and update:
- [ ] `refactor_docs/task.md` - Add Phase 7: Legacy Removal tasks
- [ ] `refactor_docs/refactor_handoff.md` - Update with consolidated findings
- [ ] Create `refactor_docs/legacy_removal_plan.md` - Prioritized fix list

**Expected Output**: 14 audit reports in `refactor_docs/` with actionable findings.
