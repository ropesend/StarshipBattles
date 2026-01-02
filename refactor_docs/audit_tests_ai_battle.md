# Audit Report: AI and Battle Unit Tests

## Overview
This audit reviews specific unit test files for legacy patterns related to the Component Ability System refactor. The focus is on identifying tests that rely on legacy attributes (`comp.damage`, legacy component types) or bypass the ability system via shallow mocking.

**Audit Target:**
- `unit_tests\test_ai.py`
- `unit_tests\test_ai_behaviors.py`
- `unit_tests\test_battle_engine_core.py`
- `unit_tests\test_battle_scene.py`
- `unit_tests\test_movement_and_ai.py`
- `unit_tests\test_strategy_system.py`
- `unit_tests\test_formation_editor_logic.py`

---

## Findings

### 1. Legacy Weapon Attributes in Strategy System
**Pattern:** Strategy tests assuming legacy weapon attributes.
- **File:** `unit_tests\test_strategy_system.py`
- **Test:** `TestStrategySystem.test_target_evaluator_complex`
- **Line:** 77
- **Code:** `c1.damage = 10`
- **Issue:** The test manually sets a `damage` attribute on a mock component to satisfy the "has_weapons" rule in `TargetEvaluator`. This suggests the `TargetEvaluator` (or the test's understanding of it) checks `comp.damage` directly, which is a legacy pattern. Code should check for weapon abilities and their computed damage.
- **Impact:** **High**. Validates legacy behavior. If `TargetEvaluator` is refactored to use abilities, this test will fail or (worse) pass falsely if the mock accidentally satisfies a legacy fallback check.
- **Fix:** Update the test to mock a component with an `abilities` dictionary containing a weapon ability, or use `create_component("railgun")` to get a real component with stats.

### 2. Shallow Mocking of Ship Attributes (AI Behaviors)
**Pattern:** AI tests mocking weapons without ability instances.
- **File:** `unit_tests\test_ai_behaviors.py`
- **Test:** `TestKiteBehavior`
- **Line:** 22
- **Code:** `self.ship.max_weapon_range = 1000`
- **Issue:** The test manually sets `max_weapon_range` on the ship mock. While `Ship.max_weapon_range` is a valid property (likely an aggregator), the test bypasses the ability system that populates this value.
- **Impact:** **Low/Medium**. The test verifies the behavior logic *given* a range, but fails to verify the integration with the ability system.
- **Fix:** Use `create_component` to populate the ship with real weapons, allowing `recalculate_stats()` to populate `max_weapon_range` naturally. This ensures the behavior works with the real data path.

### 3. Legacy Attack Data Structures in Battle Engine
**Pattern:** Battle engine tests with legacy component type assumptions.
- **File:** `unit_tests\test_battle_engine_core.py`
- **Test:** `TestBattleEngineCore.test_system_delegation`
- **Line:** 136-139
- **Code:** 
  ```python
  beam_attack = {'type': AttackType.BEAM, 'damage': 10}
  with patch.object(self.ship1, 'fire_weapons', return_value=[beam_attack]):
  ```
- **Issue:** The test mocks `fire_weapons` to return a dictionary. In the new system, `fire_weapons` typically returns `Projectile` objects or `Beam` effect objects, not raw dictionaries (unless `BattleEngine` has a legacy handler for dicts).
- **Impact:** **Medium**. If `BattleEngine` logic is refactored to expect objects, this test maintains a legacy contract.
- **Fix:** Update the mock to return a proper `Beam` object/effect consistent with the new combat system.

### 4. Dummy Components in Battle Engine Setup
**Pattern:** Battle engine tests with legacy component assumptions.
- **File:** `unit_tests\test_battle_engine_core.py`
- **Test:** `TestBattleEngineCore.setUp`
- **Line:** 50-56
- **Code:** `dummy_comp1 = MagicMock(); dummy_comp1.current_hp = 100`
- **Issue:** Tests use generic mocks for components, setting only HP. This bypasses any component type/tag validation the battle engine might perform (e.g., critical hit logic needing specific component tags).
- **Impact:** **Low**. The affected tests (`test_spatial_grid_integration`) are spatial and might not care about component types, but it's a weak test setup.
- **Fix:** Use `create_component("bridge")` etc. to ensure tests run against realistic data structures.

---

## Clean Files
The following files were reviewed and found **Clean** (no significant legacy patterns detected):
- `unit_tests\test_ai.py` (Uses `create_component` and real `Ship` validation)
- `unit_tests\test_battle_scene.py` (Uses `create_component`)
- `unit_tests\test_movement_and_ai.py` (Uses real components and full ship setup)
- `unit_tests\test_formation_editor_logic.py` (UI logic, independent of component system)

## Summary of Required Actions
1. **Refactor `test_strategy_system.py`**: Replace `c1.damage = 10` with proper ability setup.
2. **Refactor `test_battle_engine_core.py`**: Update `fire_weapons` mock return values to match new system types.
3. **Enhance `test_ai_behaviors.py`**: Consider using real ship/component setup instead of shallow mocks where feasible.
