# Simulation Engine Scout Report

## Summary
- Files Reviewed: 55
- Issues Found: 12
- Critical: 1, Major: 5, Minor: 5, Info: 1

---

## Findings

### CRITICAL: Duplicate Attribute Initialization
**ID:** NEW-SIM-001
**Location:** `game/simulation/entities/ship.py:92, 135`
**Issue:** `self.total_defense_score` is initialized twice with different values (0.0 then 1.0). Line 92 sets it to 0.0, but line 135 overwrites it with 1.0. This creates confusion about the true initial value and can cause subtle bugs.
**Impact:** Inconsistent initialization state; any code relying on the first assignment will be overridden; maintenance burden due to unclear intent.
**Recommendation:** Remove one of the duplicate assignments. Determine which is the intended initial value and keep only that one. Consider adding a comment explaining why 1.0 is the correct default.
**Effort:** Simple

---

### MAJOR: Duplicate Import Statement
**ID:** NEW-SIM-002
**Location:** `game/simulation/entities/ship.py:16, 85`
**Issue:** `ResourceRegistry` is imported at the module level (line 16) but then imported again inside `__init__` (line 85). The local import is redundant and violates DRY principle.
**Impact:** Code maintainability; confusing to readers; module-level import is sufficient and should be used consistently.
**Recommendation:** Remove the local import on line 85. Use the module-level import directly: `self.resources = ResourceRegistry()`
**Effort:** Simple

---

### MAJOR: Duplicate Statement (Assignment)
**ID:** NEW-SIM-003
**Location:** `game/simulation/systems/stats.py:42-43`
**Issue:** `ship.shield_regen_cost = 0` is assigned twice in succession (lines 42 and 43). This is a clear copy-paste error.
**Impact:** Code clarity; suggests incomplete refactoring or careless editing; wastes CPU cycles (though minimal).
**Recommendation:** Remove the duplicate line 43. Keep only one assignment.
**Effort:** Simple

---

### MAJOR: Incomplete Code Block (Dead Pass Statement)
**ID:** NEW-SIM-004
**Location:** `game/simulation/systems/stats.py:319-322`
**Issue:** A large deprecated section is replaced with just `pass`. Lines 319-321 are a comment block explaining that resource aggregation was removed, followed by a `pass` statement. This indicates incomplete refactoring or dead code path.
**Impact:** Technical debt; unclear intent; suggests Phase 6 resource aggregation was removed but not properly cleaned up.
**Recommendation:** Either implement the missing resource aggregation logic or add a clear deprecation comment explaining why this phase was removed. Consider removing the entire block if truly obsolete.
**Effort:** Medium

---

### MAJOR: Layer Violation - Components Importing Systems
**ID:** NEW-SIM-005
**Location:** `game/simulation/components/component.py:253, 297, 309`
**Issue:** The `Component` class (domain entity layer) imports from `game.simulation.systems.resource_manager` (system layer). This violates clean architecture: entities should not depend on systems. The imports are done at runtime inside methods (`_instantiate_abilities`, `update`) rather than at module level, suggesting circular dependency concerns.
**Impact:** Tight coupling between layers; difficult to test components in isolation; creates circular dependency risk; violates dependency inversion principle.
**Recommendation:** Move `ResourceConsumption` class and ability instantiation logic to a separate factory function or service. Pass necessary objects as constructor parameters rather than importing at runtime.
**Effort:** Complex

---

### MAJOR: Incomplete TODO (Missing Implementation)
**ID:** NEW-SIM-006
**Location:** `game/simulation/systems/validator.py:70`
**Issue:** The `MountDependencyRule.validate()` method has a TODO comment: "Implement full ship scan for missing mounts". This rule only validates mounts at the component addition level, not for the entire ship state.
**Impact:** Incomplete validation; ships can end up in invalid states where mount dependencies are broken; potential gameplay bugs where weapons appear to be valid but lack required mounts.
**Recommendation:** Implement the full ship scan logic in the conditional branch. Check all mounts against mount users across the entire ship. Add unit tests to verify mount dependency validation.
**Effort:** Medium

---

### MAJOR: Incomplete TODO (Missing Restoration Logic)
**ID:** NEW-SIM-007
**Location:** `game/simulation/battle_controller.py:493`
**Issue:** The `load_battle_state()` method has a TODO comment: "Restore projectiles". When loading a saved battle state, projectiles in flight are not restored, losing mid-battle state information.
**Impact:** Battle state restoration is incomplete; projectiles are lost when reloading saved battles; affects campaign continuity and testing.
**Recommendation:** Implement projectile serialization in `BattleState` and deserialization in `load_battle_state()`. Restore projectile objects with their current position, velocity, and target data.
**Effort:** Complex

---

### MINOR: Incomplete TODO (Missing Fleet Integration)
**ID:** NEW-SIM-008
**Location:** `game/simulation/battle_controller.py:650`
**Issue:** The `apply_battle_results()` method has a TODO: "Implement when Fleet uses ShipInstance". The method body is just `pass`. This is placeholder code waiting for upstream changes.
**Impact:** Battle results cannot be applied back to fleets; affects campaign/strategy layer integration; method exists but doesn't work.
**Recommendation:** Implement fleet result application once `ShipInstance` integration is available. For now, document this as a blocking dependency or create an issue to track this work.
**Effort:** Complex

---

### MINOR: Multiple Inheritance (God Class Pattern)
**ID:** NEW-SIM-009
**Location:** `game/simulation/entities/ship.py:34`
**Issue:** The `Ship` class uses multiple inheritance: `class Ship(PhysicsBody, ShipPhysicsMixin, ShipCombatMixin)`. While mixins are extracted, Ship is still a "god class" with 793 lines spanning physics, combat, components, stats, formation, and serialization responsibilities.
**Impact:** High cyclomatic complexity; difficult to test; hard to extend; violates single responsibility principle; makes the class fragile to changes.
**Recommendation:** Continue decomposition started in PROJ-12. Move more responsibilities to separate classes: `ShipComponentManager`, `ShipStatsCalculator`, `ShipSerializer`. Use composition over inheritance where possible.
**Effort:** Complex

---

### MINOR: Unused Parameter (Dead Code Path)
**ID:** NEW-SIM-010
**Location:** `game/simulation/entities/ship.py:55`
**Issue:** Variable `hull_equipped` is assigned on line 55 but never used. It's set when a hull component is successfully added but never checked or returned.
**Impact:** Dead code; suggests incomplete refactoring; clutters the codebase; may indicate missing error handling.
**Recommendation:** Either use `hull_equipped` to validate the hull attachment, or remove it. If no hull can be equipped, should an exception be raised? Consider adding: `if not hull_equipped: raise ValueError(f"Failed to equip default hull for {self.ship_class}")`
**Effort:** Simple

---

### MINOR: Missing Type Hints on Public Interface
**ID:** NEW-SIM-011
**Location:** `game/simulation/systems/stats.py:452-460`
**Issue:** Several public helper methods lack type hints. The `_priority_sort_key` method parameter `c` has no type annotation; return type is missing. Methods like `_check_mass_limits`, `_get_ability_total` also lack full type hints.
**Impact:** Reduced code clarity; IDE autocomplete is limited; harder to understand method contracts; maintenance burden.
**Recommendation:** Add type hints to all method parameters and return types. Example: `def _priority_sort_key(self, c: Component) -> int:` and `def _get_ability_total(self, component_list: List[Component], ability_name: str) -> float:`
**Effort:** Simple

---

### INFO: Potential Code Smell - Excessive Use of getattr()
**ID:** NEW-SIM-012
**Location:** `game/simulation/systems/stats.py:376, 487-491`
**Issue:** Widespread use of `getattr(ship, '_prev_max_fuel', 0)` and similar patterns suggests the Ship class is missing proper attribute initialization. This defensive programming pattern indicates incomplete initialization or poor design.
**Impact:** Code smell; suggests incomplete initialization; makes it harder to track actual ship state; can hide bugs where attributes are unexpectedly missing.
**Recommendation:** Ensure all Ship attributes are initialized in `__init__`. Use type hints to document expected attributes. Consider using `@dataclass` or explicit initialization blocks rather than defensive getattr() calls.
**Effort:** Medium

---

## Files Reviewed

1. game/simulation/__init__.py
2. game/simulation/battle_controller.py
3. game/simulation/battle_state.py
4. game/simulation/components/__init__.py
5. game/simulation/components/abilities/__init__.py
6. game/simulation/components/abilities/base.py
7. game/simulation/components/abilities/crew.py
8. game/simulation/components/abilities/defense.py
9. game/simulation/components/abilities/harvester.py
10. game/simulation/components/abilities/markers.py
11. game/simulation/components/abilities/propulsion.py
12. game/simulation/components/abilities/resources.py
13. game/simulation/components/abilities/stat_keys.py
14. game/simulation/components/abilities/weapons.py
15. game/simulation/components/component.py
16. game/simulation/components/component_constants.py
17. game/simulation/components/modifier_effects.py
18. game/simulation/components/modifier_introspection.py
19. game/simulation/components/modifier_schema.py
20. game/simulation/components/modifiers.py
21. game/simulation/designs.py
22. game/simulation/entities/ability_aggregator.py
23. game/simulation/entities/combat_endurance.py
24. game/simulation/entities/projectile.py
25. game/simulation/entities/ship.py
26. game/simulation/entities/ship_combat.py
27. game/simulation/entities/ship_combat_engine.py
28. game/simulation/entities/ship_component_manager.py
29. game/simulation/entities/ship_formation.py
30. game/simulation/entities/ship_loader.py
31. game/simulation/entities/ship_physics.py
32. game/simulation/entities/ship_serialization.py
33. game/simulation/entities/ship_stats.py
34. game/simulation/formula_system.py
35. game/simulation/managers/__init__.py
36. game/simulation/managers/battle_state_manager.py
37. game/simulation/managers/retreat_manager.py
38. game/simulation/physics_constants.py
39. game/simulation/projectile_manager.py
40. game/simulation/services/__init__.py
41. game/simulation/services/battle_service.py
42. game/simulation/services/design_loader.py
43. game/simulation/services/modifier_service.py
44. game/simulation/services/vehicle_design_service.py
45. game/simulation/ship_validator.py
46. game/simulation/systems/battle_end_conditions.py
47. game/simulation/systems/battle_engine.py
48. game/simulation/systems/persistence.py
49. game/simulation/systems/projectile_manager.py
50. game/simulation/systems/resource_manager.py
51. game/simulation/systems/stats.py
52. game/simulation/systems/tech_preset_loader.py
53. game/simulation/systems/validator.py
54. game/simulation/validation/__init__.py
55. game/simulation/validation/base.py

---

## Key Observations

1. **Attribute Initialization Issues** (NEW-SIM-001, NEW-SIM-010, NEW-SIM-012): The Ship class has scattered initialization and defensive programming patterns suggesting incomplete refactoring.

2. **Dead Code & Incomplete TODOs** (NEW-SIM-006, NEW-SIM-007, NEW-SIM-008): Three significant TODOs indicate incomplete features blocking functionality.

3. **Layer Violations** (NEW-SIM-005): Components importing from systems layer violates clean architecture and suggests tight coupling.

4. **God Class** (NEW-SIM-009): While PROJ-12 has started decomposition, Ship remains large and complex at 793 lines.

5. **Clean Code Issues** (NEW-SIM-002, NEW-SIM-003, NEW-SIM-004): Multiple instances of duplicate code and incomplete refactoring suggest the codebase could use a consolidation pass.
