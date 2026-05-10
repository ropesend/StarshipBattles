# Legacy System Holdovers Sweep: Simulation

## Summary
- **Shard:** Simulation
- **Files Scanned:** 72
- **Total Issues Found:** 7
- **Critical:** 1 | **Major:** 3 | **Minor:** 2 | **Info:** 1

## Findings

#### CRITICAL: Bootstrap Registry Fallback in load_components_data()
**ID:** LEG-SIM-001
**Location:** `game/simulation/components/component.py:498-507`
**Issue:** load_components_data() still contains "bootstrap registries fallback" using get_default_registry_provider() when registries are not provided. This violates PROJ-50 "strict DI required" mandate. Pattern also in load_components() (line 557) and load_modifiers() (line 650).
**Impact:** Maintains dual loading paths (bootstrap vs strict DI), creating confusion about which pattern is authoritative. Could mask bugs in tests vs production.
**Recommendation:** Complete PROJ-50 by requiring registries at all call sites. Delete bootstrap fallback entirely.
**Effort:** Complex

#### MAJOR: Dead Delegation Methods in BattleController
**ID:** LEG-SIM-002
**Location:** `game/simulation/battle_controller.py:401-407`
**Issue:** Two private methods _find_nearest_edge() and _is_at_map_edge() exist purely to delegate to RetreatManager but are never called anywhere. Grep confirms only definitions exist, no callers.
**Impact:** Dead code adds maintenance burden, creates false impression of API surface.
**Recommendation:** Delete both methods entirely.
**Effort:** Simple

#### MAJOR: Backward Compatibility Wrapper Functions
**ID:** LEG-SIM-003
**Location:** `game/simulation/components/component.py:545-577` (load_components) AND `game/simulation/components/component.py:638-668` (load_modifiers) AND `game/simulation/entities/ship_loader.py:100-130` (load_vehicle_classes)
**Issue:** Three wrapper functions explicitly marked for transition but still actively used during initialization. They maintain dual code paths with comments stating they're temporary.
**Impact:** Two loading paths for same operation. Comments suggest temporary but no timeline exists.
**Recommendation:** Replace all callers with direct load_components_data() calls and delete wrapper functions.
**Effort:** Medium

#### MAJOR: Deprecated AI Controller Initialization Paths
**ID:** LEG-SIM-004
**Location:** `game/simulation/systems/battle_engine.py:273-279, 343-352`
**Issue:** Two deprecated initialization paths in BattleEngine directly instantiate AIController from game.ai module, bypassing AIControllerFactory DI pattern. DeprecationWarning exists but code still active.
**Impact:** Creates tight coupling between BattleEngine and game.ai.controller. Tests using these paths bypass factory pattern.
**Recommendation:** Require ai_controllers or ai_factory parameters; remove fallback imports.
**Effort:** Medium

#### MINOR: Commented Legacy Code - Removed Component Attribute
**ID:** LEG-SIM-005
**Location:** `game/simulation/components/component.py:116-117`
**Issue:** Commented line: "# allowed_layers removed in refactor" with old code still present as comment.
**Impact:** Minimal - just dead comment creating uncertainty.
**Recommendation:** Delete commented line entirely.
**Effort:** Simple

#### MINOR: Safe Evaluation Wrapper - Redundant Indirection
**ID:** LEG-SIM-006
**Location:** `game/simulation/formula_system.py:148-171`
**Issue:** safe_evaluate_math_formula() documented as "backwards-compatible wrapper around evaluate_math_formula". Catches FormulaException and returns default value.
**Impact:** Extra indirection layer for error handling. "Backward-compatible" framing suggests removable.
**Recommendation:** Clarify intent: either commit to error handling pattern or consolidate into primary function.
**Effort:** Simple

#### INFO: Legacy Fallback Pattern Comment in Result Application
**ID:** LEG-SIM-007
**Location:** `game/simulation/battle_controller.py:620`
**Issue:** Comment "Legacy fallback (should not normally reach here)" guards a defensive code path for fleet mutation.
**Impact:** Code path exists for defensive purposes but marked as legacy.
**Recommendation:** Monitor usage. If never exercised, remove. If needed, remove "legacy" framing.
**Effort:** Simple

## Top 5 Priority Issues
1. **LEG-SIM-001** (CRITICAL): Bootstrap registry fallback - dual loading paths confuse DI enforcement
2. **LEG-SIM-003** (MAJOR): Wrapper functions - temporary compatibility never removed
3. **LEG-SIM-004** (MAJOR): Deprecated AI init paths - bypasses factory pattern
4. **LEG-SIM-002** (MAJOR): Dead delegation methods - never called, safe to delete
5. **LEG-SIM-005** (MINOR): Commented legacy code - quick cleanup
