# PROJ-113: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Review
- **Review:** [2026-02-11_sweep_full-codebase-sweep](../../Reviews/results/2026-02-11_sweep_full-codebase-sweep/)
- **Type:** Sweep Review (automated parallel analysis)
- **Date:** 2026-02-11
- **Report:** [View Full Report](../../Reviews/results/2026-02-11_sweep_full-codebase-sweep/report.md)

## Initial Analysis
Findings from review - 396 total findings identified.
- **Critical:** 9
- **Major:** 14
- **Selected for remediation:** 52

## Selected Findings Summary

### ADR-FND-001: Pygame imported in game/core/input_mappe
- **Severity:** Critical
- **Location:** `game/core/input_mapper.py:26,3`
- **Effort:** Medium

### ADR-FND-002: Pygame imported in game/core/screenshot_
- **Severity:** Critical
- **Location:** `game/core/screenshot_manager.p`
- **Effort:** Simple

### ADR-FND-003: Research scene imports from game.ui (Lay
- **Severity:** Critical
- **Location:** `game/research/ui/research_scen`
- **Effort:** Medium

### ADR-SIM-001: AIControllerFactory runtime imports from
- **Severity:** Critical
- **Location:** `game/simulation/factories/ai_f`
- **Effort:** Medium

### ADR-SIM-002: persistence.py imports tkinter UI framew
- **Severity:** Critical
- **Location:** `game/simulation/systems/persis`
- **Effort:** Simple

### ADR-UI2-001: Pygame in Core Layer -- ScreenshotManage
- **Severity:** Critical
- **Location:** `game/core/screenshot_manager.p`
- **Effort:** Medium

### ADR-UI2-002: Pygame in Core Layer -- InputMapper
- **Severity:** Critical
- **Location:** `game/core/input_mapper.py:26`
- **Effort:** Complex

### ADR-UI1-001: Test Lab UI Imports From test_framework
- **Severity:** Critical
- **Location:** `game/ui/screens/test_lab/scree`
- **Effort:** Complex

### ADR-UI1-002: Simulation Layer Imports tkinter GUI Fra
- **Severity:** Critical
- **Location:** `game/simulation/systems/persis`
- **Effort:** Medium

### ADR-FND-004: Core protocols.py TYPE_CHECKING import f
- **Severity:** Major
- **Location:** `game/core/protocols.py:42`
- **Effort:** Simple

### ADR-FND-005: AI controllable.py TYPE_CHECKING import
- **Severity:** Major
- **Location:** `game/ai/interfaces/controllabl`
- **Effort:** Simple

### ADR-FND-006: Research UI files use pygame directly (M
- **Severity:** Major
- **Location:** `game/research/ui/research_cont`
- **Effort:** Medium

### ADR-FND-007: AIController deep attribute chain (Law o
- **Severity:** Major
- **Location:** `game/ai/controller.py:410`
- **Effort:** Simple

### ADR-SIM-003: battle_config.py TYPE_CHECKING import fr
- **Severity:** Major
- **Location:** `game/simulation/battle_config.`
- **Effort:** Simple

### ADR-SIM-004: battle_engine.py TYPE_CHECKING import fr
- **Severity:** Major
- **Location:** `game/simulation/systems/battle`
- **Effort:** Simple

### ADR-STR-008: ShipDisplayFormatter in Strategy Data La
- **Severity:** Major
- **Location:** `game/strategy/data/ship_displa`
- **Effort:** Medium

### ADR-STR-011: hex_to_pixel/pixel_to_hex Usage in Galax
- **Severity:** Major
- **Location:** `game/strategy/data/galaxy.py:5`
- **Effort:** Simple

### ADR-UI2-003: Renderer Directly Accesses Simulation Do
- **Severity:** Major
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Medium

### ADR-UI2-004: ShipFactory Uses pygame.math.Vector2 Ins
- **Severity:** Major
- **Location:** `game/ui/services/ship_factory.`
- **Effort:** Simple

### ADR-UI2-005: DesignLoaderAdapter Has Hard Runtime Imp
- **Severity:** Major
- **Location:** `game/ui/services/design_loader`
- **Effort:** Simple

### ADR-UI2-006: Pygame TYPE_CHECKING Import in AI Layer
- **Severity:** Major
- **Location:** `game/ai/interfaces/controllabl`
- **Effort:** Simple

### ADR-UI1-007: Extensive Private Attribute Access Acros
- **Severity:** Major
- **Location:** `game/ui/screens/strategy_event`
- **Effort:** Medium

### ADR-UI1-008: UI Layer Mutates Strategy Data Objects W
- **Severity:** Major
- **Location:** `game/ui/screens/planet_list_fi`
- **Effort:** Medium

### ADR-FND-008: UIConfig class in game/core/config.py co
- **Severity:** Minor
- **Location:** `game/core/config.py:132-198`
- **Effort:** Simple

### ADR-FND-009: ScreenshotManager.capture_strategy_layer
- **Severity:** Minor
- **Location:** `game/core/screenshot_manager.p`
- **Effort:** Simple

### ADR-FND-010: Engine collision.py TYPE_CHECKING import
- **Severity:** Minor
- **Location:** `game/engine/collision.py:55`
- **Effort:** Simple

### ADR-FND-011: Constants file mixes UI concerns (colors
- **Severity:** Minor
- **Location:** `game/core/constants.py:42-49`
- **Effort:** Simple

### ADR-SIM-008: UI data flow - screen dimensions in simu
- **Severity:** Minor
- **Location:** `game/simulation/services/desig`
- **Effort:** Simple

### ADR-SIM-009: Visual properties embedded in simulation
- **Severity:** Minor
- **Location:** `game/simulation/entities/proje`
- **Effort:** Medium

### ADR-SIM-010: Pervasive color_hint in ability display_
- **Severity:** Minor
- **Location:** `game/simulation/components/abi`
- **Effort:** Large

### ADR-SIM-011: Circular dependency workarounds via late
- **Severity:** Minor
- **Location:** `game/simulation/entities/ship.`
- **Effort:** Large

### ADR-SIM-012: modifier_introspection.py contains UI-sp
- **Severity:** Minor
- **Location:** `game/simulation/components/mod`
- **Effort:** Simple

### ADR-STR-001: Pervasive Lazy Imports to Avoid Circular
- **Severity:** Minor
- **Location:** `Unknown`
- **Effort:** Complex

### ADR-STR-002: Galaxy Circular Dependency with Placemen
- **Severity:** Minor
- **Location:** `game/strategy/data/galaxy.py:3`
- **Effort:** Medium

### ADR-STR-007: FleetBattleAdapter Accesses Private Meth
- **Severity:** Minor
- **Location:** `game/strategy/data/fleet_battl`
- **Effort:** Simple

### ADR-STR-009: Color Tuples Embedded in Strategy Game C
- **Severity:** Minor
- **Location:** `game/strategy/engine/game_conf`
- **Effort:** Medium

### ADR-STR-013: EmpireEconomyCalculator Provides "Displa
- **Severity:** Minor
- **Location:** `game/strategy/engine/empire_ec`
- **Effort:** Simple

### ADR-UI2-007: ScreenshotManager Accesses Private _rend
- **Severity:** Minor
- **Location:** `game/core/screenshot_manager.p`
- **Effort:** Medium

### ADR-UI2-008: ValidationService Has Eager Runtime Impo
- **Severity:** Minor
- **Location:** `game/ui/services/validation_se`
- **Effort:** Simple

### ADR-UI2-009: game_renderer.py Uses Lazy Import Inside
- **Severity:** Minor
- **Location:** `game/ui/renderer/game_renderer`
- **Effort:** Simple

### ADR-UI1-013: UIConfig and DisplayConfig in Core Layer
- **Severity:** Minor
- **Location:** `game/core/config.py:132-159`
- **Effort:** Simple

### ADR-UI1-014: UI Color Constants (WHITE, BLACK, BLUE,
- **Severity:** Minor
- **Location:** `game/core/constants.py:42-49`
- **Effort:** Simple

### ADR-UI1-015: Circular Import Avoidance via Late Impor
- **Severity:** Minor
- **Location:** `game/ui/screens/column_manager`
- **Effort:** Simple

### ADR-UI1-016: Module-Level tkinter Initialization Side
- **Severity:** Minor
- **Location:** `game/ui/screens/formation_edit`
- **Effort:** Simple

### ADR-UI1-017: Deep Attribute Chains Violating Law of D
- **Severity:** Minor
- **Location:** `game/ui/screens/test_lab/scree`
- **Effort:** Medium

### ADR-UI1-018: Circular Import Avoidance in new_game_se
- **Severity:** Minor
- **Location:** `game/ui/screens/new_game_setup`
- **Effort:** Simple

### ADR-UI1-019: TestLabScreen Directly Accesses battle_s
- **Severity:** Minor
- **Location:** `game/ui/screens/test_lab/scree`
- **Effort:** Simple

### ADR-FND-012: Research package has clean data/systems
- **Severity:** Info
- **Location:** `game/research/data/`
- **Effort:** N

### ADR-SIM-013: battle_state.py is a large data containe
- **Severity:** Info
- **Location:** `game/simulation/battle_state.p`
- **Effort:** N

### ADR-SIM-014: game.engine dependencies are architectur
- **Severity:** Info
- **Location:** `Unknown`
- **Effort:** N

### ADR-STR-012: DesignMetadata Contains sprite_preview F
- **Severity:** Info
- **Location:** `game/strategy/data/design_meta`
- **Effort:** Simple

### ADR-UI2-010: Consistent Use of Facade/Adapter Pattern
- **Severity:** Info
- **Location:** `game/ui/services/`
- **Effort:** N


## Architecture
[Key architecture points relevant to implementation - to be filled during planning]

## Key Patterns to Reuse
- **[Pattern Name]**: `file:lines` - description

## Dependencies & Risks
1. **[Risk/Dependency]** - mitigation approach

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
