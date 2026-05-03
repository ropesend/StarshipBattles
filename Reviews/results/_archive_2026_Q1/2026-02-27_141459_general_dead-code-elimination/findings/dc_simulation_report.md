# Dead Code Hunter Report: Simulation Module (`game/simulation/`)

### Summary
- Total dead code items found: 9
- Estimated removable lines: 45-60
- Critical: 0, Major: 3, Minor: 6, Info: 0

### Findings

#### Major: Empty recalculate() methods in Defense Abilities
**ID:** DC-SIM-01
**Location:** `game/simulation/components/abilities/defense.py:63-67, 88-89, 110-111`
**Issue:** Three ability classes (ToHitAttackModifier, ToHitDefenseModifier, EmissiveArmor) define `recalculate()` methods that contain only `pass` statements. Called by Component stats recalculation but do nothing. Abilities are stateless with `STAT_BINDINGS = []`.
**Evidence:** Comment indicates "for now" placeholder code.
**Removable Lines:** 9
**Effort:** Simple

#### Major: Documentation Gap in Marker Abilities
**ID:** DC-SIM-02
**Location:** `game/simulation/components/abilities/markers.py:24, 49-92`
**Issue:** Multiple marker ability classes (CommandAndControl, RequiresCommandAndControl, RequiresCombatMovement, StructuralIntegrity) don't define `recalculate()` but inherit stub from base. Intentional design but incomplete documentation.
**Removable Lines:** 0 (design choice, needs documentation)
**Effort:** Simple

#### Major: Dead Code Pattern in ship_physics.py rotate()
**ID:** DC-SIM-03
**Location:** `game/simulation/entities/ship_physics.py:76-86`
**Issue:** The `rotate()` method has trailing whitespace/blank lines after angle increment. Method ends abruptly without typical closure structure.
**Removable Lines:** 1-2
**Effort:** Simple

#### Minor: Unused Parameters in Component.update()
**ID:** DC-SIM-04
**Location:** `game/simulation/components/component.py:289-320`
**Issue:** `update(self, dt: float = 0.01, context: Optional[dict] = None)` has `dt` and `context` parameters never referenced in method body.
**Evidence:** Method body only calls `self.resources.update()` without using dt or context.
**Removable Lines:** 2 parameters
**Effort:** Simple

#### Minor: Hardcoded ModifierService get_initial_value()
**ID:** DC-SIM-05
**Location:** `game/simulation/services/modifier_service.py:141-185`
**Issue:** `get_initial_value()` contains hardcoded if/elif checks for specific modifier IDs instead of using modifier registry. Tight coupling requiring manual updates for new modifiers.
**Evidence:** Lines 158-183 show manual checks for 7 modifier types.
**Removable Lines:** ~20 lines of unnecessary branching (requires refactor)
**Effort:** Medium

#### Minor: Single-use get_ship_by_id() in BattleController
**ID:** DC-SIM-06
**Location:** `game/simulation/battle_controller.py:401-406`
**Issue:** Internal nested function defined and used only once. Could be inlined.
**Evidence:** Function defined then immediately passed to `retreat_manager.update()`.
**Removable Lines:** 6
**Effort:** Simple

#### Minor: Partially Dead Error Code Constants
**ID:** DC-SIM-07
**Location:** `game/simulation/formula_system.py:32-36`
**Issue:** Error codes FORMULA_ERROR_SYNTAX, FORMULA_ERROR_UNDEFINED, FORMULA_ERROR_RUNTIME defined but broad exception at line 144 catches all with FORMULA_ERROR_SECURITY code.
**Removable Lines:** ~5
**Effort:** Simple

#### Minor: Empty Context in Formula Evaluation
**ID:** DC-SIM-08
**Location:** `game/simulation/components/abilities/weapons.py:95-97`
**Issue:** Reload and range formula evaluation passes empty dict `{}` for context while damage formula passes `{'range_to_target': 0}`. Inconsistent pattern.
**Removable Lines:** 0 (incomplete feature, not dead code)
**Effort:** Medium

#### Minor: Inefficient hit flag pattern
**ID:** DC-SIM-09
**Location:** `game/simulation/projectile_manager.py:104-108`
**Issue:** `hit = False` followed by branches setting `hit = True` then `if hit:` check. Could use direct returns.
**Removable Lines:** 4-6
**Effort:** Simple

### Top 5 Priority Items
1. **DC-SIM-01**: Remove empty recalculate() methods (9 lines)
2. **DC-SIM-04**: Remove unused parameters from Component.update()
3. **DC-SIM-06**: Inline get_ship_by_id() (6 lines)
4. **DC-SIM-07**: Consolidate formula error codes (5 lines)
5. **DC-SIM-05**: Refactor ModifierService.get_initial_value() (20 lines)
