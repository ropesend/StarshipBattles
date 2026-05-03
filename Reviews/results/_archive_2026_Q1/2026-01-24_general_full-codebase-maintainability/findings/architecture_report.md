# Architecture Reviewer Report

## Summary
- **Total issues found:** 13
- **Critical:** 3, **Major:** 5, **Minor:** 4, **Info:** 1

---

## Findings

### CRITICAL: Simulation Layer Imports pygame (UI Framework Dependency)
**ID:** AR-001
**Location:** `game/simulation/entities/ship.py:1`, `game/simulation/battle_state.py`, `game/simulation/systems/battle_engine.py`
**Issue:** The simulation layer directly imports and uses `pygame` throughout. Usage includes `pygame.math.Vector2` for velocity, position, offsets.
**Impact:**
- Simulation layer cannot be reused in headless servers, web clients, or other non-Pygame applications
- Testing simulation logic requires pygame initialization
- Violates layered architecture: Presentation layer should not leak into Simulation layer
**Recommendation:** Create a `game.core.math` module with Vector2. Remove pygame imports from simulation layer entirely.
**Effort:** Complex

### CRITICAL: Strategy Data Layer Imports UI Components
**ID:** AR-002
**Location:** `game/strategy/data/fleet.py` (imports `has_warp_capability` from UI)
**Issue:** The strategy data layer imports UI-specific logic from `game.ui.screens.fleet_report_filters`.
**Impact:**
- Violates clean architecture: Data layer should not depend on UI layer
- Makes strategy simulation dependent on UI module initialization
- Circular dependency risk
**Recommendation:** Move `has_warp_capability()` to `game/strategy/services/fleet_stats_service.py`.
**Effort:** Medium

### CRITICAL: Inappropriate Intimacy - AIController Tight Coupling to Ship
**ID:** AR-003
**Location:** `game/ai/controller.py`, `game/simulation/systems/battle_engine.py`
**Issue:** AIController directly accesses and modifies ship private fields extensively.
**Impact:**
- Changes to ship properties break AI logic
- AI and Ship classes are hard to test independently
- Cannot swap AI implementations easily
**Recommendation:** Create `ShipAIInterface` with methods like `set_throttle()`, `set_target()`, `get_position()`, `query_enemies()`.
**Effort:** Medium

### MAJOR: Ship Class - God Object Anti-Pattern
**ID:** AR-004
**Location:** `game/simulation/entities/ship.py:762 lines, 45 methods`
**Issue:** Ship class handles physics, combat, components, formation, resources, serialization, and validation.
**Impact:** Difficult to test, changes risk breaking multiple concerns, mixed responsibilities.
**Recommendation:** Extract FormationManager, ShipSerializer, ShipValidator as separate services.
**Effort:** Complex

### MAJOR: Pygame Imports in Data/Entity Layer
**ID:** AR-005
**Location:** `game/simulation/systems/persistence.py`
**Issue:** Persistence layer uses pygame for coordinates including screen dimensions in save/load.
**Impact:** Saved battles cannot load on headless servers. Screen resolution leaks into data layer.
**Recommendation:** Remove screen dimensions from persistence. Store positions as tuples. Move centering to UI layer.
**Effort:** Medium

### MAJOR: Simulation Imports Strategy Data (Bidirectional Dependency)
**ID:** AR-006
**Location:** `game/simulation/entities/ship_stats.py:43`, `game/simulation/battle_controller.py:29`
**Issue:** Simulation layer imports from strategy layer creating bidirectional dependency.
**Impact:** Creates circular dependency risk. Violates layered architecture.
**Recommendation:** Move shared constants to `game/core/constants.py`. Use dependency injection.
**Effort:** Medium

### MAJOR: Scattered Circular Import Workarounds
**ID:** AR-007
**Location:** Multiple files with comments like "# Import here to avoid circular imports"
**Issue:** Circular imports worked around with late imports inside functions.
**Impact:** Masks real dependency problems. Performance cost from runtime imports.
**Recommendation:** Restructure modules to have clear dependency direction. Move shared code to core layer.
**Effort:** Complex

### MAJOR: Race Setup Screen - God Class
**ID:** AR-008
**Location:** `game/ui/screens/race_setup_screen.py:2,325 lines, 56 methods`
**Issue:** Handles UI rendering, event routing, race configuration, validation, asset preview.
**Impact:** Very difficult to modify or test individual aspects. Large file makes code review difficult.
**Recommendation:** Extract RacePreviewRenderer, RaceValidator, RaceBrowserDialog as separate classes.
**Effort:** Medium

### Minor: Large Strategy UI Files
**ID:** AR-009
**Location:** `game/ui/screens/strategy_screen.py:885 lines`, `game/ui/screens/strategy_renderer.py:598 lines`
**Issue:** Files at or exceeding reasonable size (400-500 lines).
**Impact:** Hard to navigate. Visual rendering logic tightly coupled to input logic.
**Recommendation:** Further decompose into FleetRenderer, PlanetRenderer, UIOverlayRenderer.
**Effort:** Medium

### Minor: Feature Envy in Strategy Services
**ID:** AR-010
**Location:** `game/strategy/data/fleet.py`
**Issue:** Fleet class accesses many properties of Planet and ShipInstance objects.
**Impact:** Tight coupling between Fleet and its member types.
**Recommendation:** Create Fleet-focused query methods on Planet. Move capability checking to services.
**Effort:** Medium

### Minor: Builder Screen Complexity
**ID:** AR-011
**Location:** `game/ui/screens/builder_screen.py:169 lines`
**Issue:** Coordination between BuilderViewmodel, workshop_event_router, and builder_data_loader is complex.
**Impact:** Hard to test in isolation. Difficult to understand data flow.
**Recommendation:** Create BuilderCoordinator. Document data flow.
**Effort:** Simple

### Info: Singleton Usage Pattern
**ID:** AR-012
**Location:** Multiple files (27 files use `.instance()` or `get_instance()`)
**Issue:** Heavy reliance on singleton pattern for registries and services.
**Impact:** Makes dependency injection difficult. Hard to test. Global state risks.
**Recommendation:** Acceptable for stateless registries. Gradually migrate stateful services to DI.
**Effort:** Info only

---

## Top 5 Priority Issues

1. **AR-001: Simulation Imports pygame** - Blocks headless/server deployment, creates hard UI dependency
2. **AR-002: Strategy Data Imports UI** - Violates layered architecture, creates circular dependency risk
3. **AR-006: Bidirectional Simulation ↔ Strategy Dependency** - Breaks layering
4. **AR-003: AIController Tight Coupling to Ship** - Makes AI untestable, hard to extend
5. **AR-004: Ship Class God Object** - Makes Ship untestable, hard to modify

---

## Recommended Refactoring Sequence

1. **Phase 0 (Quick wins):** AR-002, AR-006 - Move has_warp_capability and PLANET_RESOURCES to core
2. **Phase 1 (Core layers):** AR-001 - Replace pygame.Vector2 with custom Vector2
3. **Phase 2 (Entity improvements):** AR-003, AR-004 - Extract AIController interface, begin Ship decomposition
4. **Phase 3 (UI improvements):** AR-008, AR-009, AR-011 - Decompose large UI classes
