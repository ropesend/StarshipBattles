# Architecture Drift Sweep: UI-Framework

## Summary
- **Shard:** UI-Framework
- **Files Scanned:** 22
- **Total Issues Found:** 10
- **Critical:** 2 | **Major:** 3 | **Minor:** 3 | **Info:** 2

## Findings

#### CRITICAL: Private Attribute Access in BattleUIService
**ID:** ADR-UI2-001
**Location:** `game/ui/services/battle_ui_service.py:133-134`
**Issue:** Accessing private _resources attribute: `getattr(ship_resources, '_resources', {})`. Violates encapsulation by relying on private implementation details.
**Impact:** If resources object changes internal structure, this breaks silently.
**Recommendation:** Use public method like get_all_resources() or define explicit API.
**Effort:** Simple

#### CRITICAL: Excessive getattr() Chains Indicating Fragile Contract
**ID:** ADR-UI2-002
**Location:** `game/ui/services/battle_ui_service.py:132-195`
**Issue:** 20+ getattr() calls with fallback defaults suggest ship object has unstable interface. Each defensive check indicates missing protocol/interface contract.
**Impact:** Fragile data transformation layer. Silent failures in battle rendering.
**Recommendation:** Define explicit IShipDTO conversion protocol that Ship implements.
**Effort:** Medium

#### MAJOR: ShipThemeManager Singleton Thread Safety Gap
**ID:** ADR-UI2-003
**Location:** `game/ui/assets/ship_theme_manager.py:70-92`
**Issue:** reset() doesn't call clear() first. _load_single_image acquires _io_lock but concurrent clear() isn't fully protected. Race condition during re-initialization.
**Impact:** Thread safety issue in asset manager.
**Recommendation:** Ensure reset() calls clear(). Guarantee all locks consistent.
**Effort:** Simple

#### MAJOR: game_renderer.py Tight Coupling to Simulation Enums
**ID:** ADR-UI2-004
**Location:** `game/ui/renderer/game_renderer.py:9, 46, 91-98`
**Issue:** Hardcoded LayerType enum and direct component ability inspection. Magic radius percentages (0.1, 0.35) hardcoded instead of calculated values.
**Impact:** Rendering logic tightly coupled to simulation layer enums.
**Recommendation:** Create RenderableShip interface and pass pre-calculated radii.
**Effort:** Medium

#### MAJOR: DesignLoaderAdapter Lazy Import Pattern
**ID:** ADR-UI2-005
**Location:** `game/ui/services/design_loader_adapter.py:40-45`
**Issue:** Lazy imports inside __init__ create implicit dependency ordering on SimulationDesignLoader.
**Impact:** Obscures dependencies at module level.
**Recommendation:** Move imports to top-level; make registries explicit parameter.
**Effort:** Simple

#### MINOR: Inconsistent DI Patterns Across Services
**ID:** ADR-UI2-006
**Location:** Multiple service files (component_service, vehicle_class_service, ship_factory)
**Issue:** Different services use different DI conventions (strict required vs optional lazy).
**Impact:** Inconsistent but functional.
**Recommendation:** Standardize on one DI pattern.
**Effort:** Medium

#### MINOR: SpriteManager Singleton Without Validation
**ID:** ADR-UI2-007
**Location:** `game/ui/renderer/sprites.py:58-74`
**Issue:** No validation that sprite paths exist before loading.
**Impact:** Low - graceful fallback exists but could warn earlier.
**Recommendation:** Add path validation with logging.
**Effort:** Simple

#### MINOR: ShipThemeManager Inefficient Path Resolution
**ID:** ADR-UI2-008
**Location:** `game/ui/assets/ship_theme_manager.py:300-309`
**Issue:** Fragile path inference walking up directory structure from any ship path. Should cache theme directory directly.
**Impact:** Low-Medium - works but unreliable.
**Recommendation:** Cache theme directory on initialization.
**Effort:** Simple

#### INFO: TYPE_CHECKING Import Not Isolated in BattleUIService
**ID:** ADR-UI2-009
**Location:** `game/ui/services/battle_ui_service.py:21-23, 56, 60`
**Issue:** Accessing engine.ships and engine.recent_beams directly without protocol.
**Impact:** Runtime assumption about engine structure.
**Recommendation:** Define explicit interface for BattleEngine data access.
**Effort:** Medium

#### INFO: BattleOrchestrator Cross-Layer Imports (Intentional)
**ID:** ADR-UI2-010
**Location:** `game/ui/orchestration/battle_orchestrator.py`
**Issue:** Imports game.ai.controller and game.engine.spatial intentionally. Comments explain UI-layer orchestration role.
**Impact:** Acceptable per architecture design. Documented.
**Recommendation:** None - intentional design.
**Effort:** None

## Top 5 Priority Issues
1. **ADR-UI2-001**: Private _resources attribute access - violates encapsulation
2. **ADR-UI2-002**: Excessive getattr() indicating missing interface contract
3. **ADR-UI2-003**: ShipThemeManager thread safety gap
4. **ADR-UI2-004**: game_renderer tight coupling to simulation enums
5. **ADR-UI2-005**: Lazy import pattern obscuring dependencies
