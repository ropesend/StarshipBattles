# Architecture Drift Sweep: Strategy

## Summary
- **Shard:** Strategy (game/strategy/)
- **Files Scanned:** 95
- **Total Issues Found:** 6
- **Critical:** 1 | **Major:** 2 | **Minor:** 2 | **Info:** 1

## Findings

#### CRITICAL: Strategy Layer Imports from AI Layer
**ID:** ADR-STR-001
**Location:** `game/strategy/adapters/simulation_adapter.py:29`
**Issue:** Strategy layer directly imports from the AI layer, violating the documented architecture where Strategy can only depend on Simulation and Core. The comment on line 28-29 incorrectly claims "strategy can depend on AI" but the architecture documentation (docs/architecture/ARCHITECTURE.md lines 35-40) explicitly states Strategy can only depend on "Simulation (via interfaces), Core".
**Code:**
```python
# PROJ-126: Import AI factory from AI layer (strategy can depend on AI)
from game.ai.ai_factory import AIControllerFactory
```
**Impact:** This creates an improper dependency direction. AI should depend on Strategy (not vice versa). This complicates testing, prevents headless strategy execution without AI code, and creates coupling between layers that should be independent.
**Recommendation:** Inject AIControllerFactory as a parameter to SimulationBattleResolver or via BattleController. The BattleController should accept an optional AI factory, allowing SimulationBattleResolver to remain AI-agnostic.
**Effort:** Medium

#### MAJOR: ShipDisplayFormatter in Strategy Layer (Presentation Leak)
**ID:** ADR-STR-002
**Location:** `game/strategy/data/ship_display_formatter.py:1-122`
**Issue:** ShipDisplayFormatter is a presentation/formatting class that lives in the strategy layer. While the class's docstring acknowledges this is unusual and defends the placement, having display formatting logic in the strategy layer is a data flow violation. The class formats status text, HP display strings, and resource percentages - these are all UI concerns.
**Code:**
```python
"""
ARCHITECTURE NOTE: This class provides presentation-layer formatting (status text,
HP display strings, resource percentages) but lives in the strategy layer because:
1. Moving to game.ui would create a circular dependency (ShipInstance imports this)
...
"""
```
**Impact:** The strategy layer now contains UI/presentation concerns. If ShipInstance imports this formatter, the circular dependency argument is valid but indicates a design issue - ShipInstance should not need to format its own display.
**Recommendation:** Consider using a protocol pattern: ShipInstance provides data via IShipStats protocol, and UI creates ShipDisplayFormatter with that protocol. Or, provide raw data methods on ShipInstance and let UI handle all formatting.
**Effort:** Medium

#### MAJOR: Circular Import Workaround in Galaxy
**ID:** ADR-STR-003
**Location:** `game/strategy/data/galaxy.py:468-470`
**Issue:** Late import inside method to avoid circular dependency: `from game.strategy.generation.placement_strategies import RandomPlacementStrategy`. The comment explicitly states "Import here to avoid circular dependency".
**Code:**
```python
def generate_systems(self, count: int, ...):
    # Import here to avoid circular dependency
    from game.strategy.generation.placement_strategies import RandomPlacementStrategy
```
**Impact:** Indicates a structural coupling issue between galaxy data and generation logic. Circular dependencies are design smells that make the code harder to understand and test.
**Recommendation:** Consider extracting a GalaxyGenerator class that owns system generation logic, accepting Galaxy as a dependency rather than being a method on Galaxy. This would eliminate the circular import need.
**Effort:** Medium

#### MINOR: Intentional Late Imports - Documented but Numerous
**ID:** ADR-STR-004
**Location:** Multiple files (fleet.py:142, ship_instance.py:170,230,501, fleet_capability_calculator.py:115,135)
**Issue:** 8 intentional late imports documented with "INTENTIONAL LATE IMPORT" comments. While these are acknowledged and documented in docs/ARCHITECTURE.md "Intentional Late Imports" section, the quantity suggests the architecture has pain points that force these workarounds.
**Impact:** Late imports add cognitive overhead, can mask import-time errors, and indicate structural coupling. However, since these are documented and intentional for edge operations, the impact is limited.
**Recommendation:** Continue monitoring. Consider whether future refactoring (such as Protocol patterns or dependency injection) could eliminate some of these. The current state is acceptable but not ideal.
**Effort:** Complex (if addressing root causes)

#### MINOR: RGB Color Tuples in Game Config
**ID:** ADR-STR-005
**Location:** `game/strategy/engine/game_config.py:26-35`
**Issue:** THEME_DEFAULTS contains RGB color tuples that are stored in save games and used for empire identification. The comment acknowledges this is intentional:
```python
# ARCHITECTURE NOTE: Colors here are game-semantic identifiers for empires,
# stored in save games, and used consistently across UI.
```
**Impact:** This is a borderline case. While RGB tuples could be considered UI data, they're being used as semantic identifiers that persist in save files. The rationale in the comment is reasonable, but it does couple save format to UI color representation.
**Recommendation:** This is acceptable as-is given the documented rationale. If save format ever changes, consider abstracting to color identifiers rather than raw RGB.
**Effort:** Simple (if ever needed)

#### INFO: Extensive TYPE_CHECKING Imports
**ID:** ADR-STR-006
**Location:** 36 files across game/strategy/
**Issue:** 36 files use TYPE_CHECKING blocks for type hints. While this is a valid Python pattern and necessary for avoiding circular imports with type annotations, the quantity suggests the module graph has complex interdependencies.
**Impact:** No operational impact. TYPE_CHECKING imports are resolved at static analysis time only. This is informational about architecture complexity.
**Recommendation:** No action needed. This is a standard pattern and the usage appears appropriate.
**Effort:** N/A

## Top 5 Priority Issues

1. **ADR-STR-001 (CRITICAL): Strategy imports AI** - Direct layer violation that contradicts documented architecture. Should be fixed by injecting AIControllerFactory rather than importing it directly.

2. **ADR-STR-002 (MAJOR): ShipDisplayFormatter location** - Presentation logic in strategy layer indicates a data/presentation boundary issue. Consider protocol-based separation.

3. **ADR-STR-003 (MAJOR): Galaxy circular import** - Circular dependency workaround suggests Galaxy class has too many responsibilities. Consider extracting generation logic.

4. **ADR-STR-004 (MINOR): Intentional late imports** - 8 documented late imports indicate architecture pain points. Monitor and consider long-term restructuring.

5. **ADR-STR-005 (MINOR): RGB colors in config** - Borderline data flow issue but adequately documented and justified.
