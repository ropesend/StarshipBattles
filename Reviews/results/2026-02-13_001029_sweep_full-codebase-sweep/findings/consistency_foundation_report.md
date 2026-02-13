# Consistency Violations Sweep: Foundation

## Summary
- **Shard:** Foundation (game/core/, game/ai/, game/research/, game/engine/)
- **Files Scanned:** 41
- **Total Issues Found:** 18
- **Critical:** 1 | **Major:** 4 | **Minor:** 10 | **Info:** 3

## Findings

#### CRITICAL: Inconsistent Singleton Pattern Usage - SingletonMeta vs Module-Level Globals
**ID:** CON-FND-001
**Location:** `game/core/registry.py:79-120`, `game/core/registry.py:379-398`
**Issue:** The codebase uses two incompatible singleton patterns side-by-side. `RegistryManager` uses `SingletonMeta`, but `_default_registries` and `_default_provider` use module-level global variables with manual getter/setter functions. This creates confusion about which pattern is authoritative and risks inconsistent state management.
**Impact:** Developers must understand both patterns; potential for state inconsistencies if one pattern is reset without the other; cognitive overhead in maintenance.
**Recommendation:** Standardize on `SingletonMeta` for all singleton services. Convert `_default_registries` and `_default_provider` to use `SingletonMeta`-based classes or document the explicit reason for the different approaches (e.g., GameRegistries is intentionally a container, not a service).
**Effort:** Medium

#### MAJOR: Inconsistent Logging Pattern - Logger Singleton vs Standard logging.getLogger
**ID:** CON-FND-002
**Location:** `game/core/logger.py` (singleton), `game/ai/combat_utils.py:19`, `game/ai/controller.py:55`
**Issue:** The codebase has two competing logging patterns: (1) A custom `Logger` singleton in `game/core/logger.py` with helper functions (`log_debug`, `log_info`, etc.), and (2) Standard Python `logging.getLogger(__name__)` used directly in AI modules. The AI layer uses `logger = logging.getLogger(__name__)` while core/research use the custom Logger.
**Impact:** Inconsistent log formatting, difficulty in configuring log levels per module, cognitive overhead when deciding which pattern to use.
**Recommendation:** Choose one pattern. The custom Logger is already widely used and provides module-level functions. Either migrate AI to use `log_debug/log_info/log_warning/log_error` from `game.core.logger`, or migrate everything to standard `logging.getLogger(__name__)`.
**Effort:** Medium

#### MAJOR: Mixed Return Semantics for Not-Found Cases
**ID:** CON-FND-003
**Location:** `game/core/registry.py:98-120` vs `game/ai/strategy_manager.py:107-120`
**Issue:** `get_default_registries()` raises `StateException` when not initialized, but `StrategyManager.get_strategy()` returns a default value when strategy_id is not found. Similar inconsistency: `json_utils.load_json()` returns default on failure, but `load_json_required()` raises. While this is partially documented, the pattern is inconsistent.
**Impact:** Callers must know which functions raise vs return defaults; potential for bugs when assumptions are wrong.
**Recommendation:** Establish a project-wide convention: either (a) All getters return Optional/default and callers must check, or (b) Add parallel `get_X_required()` methods that raise when not found. Document the convention in CLAUDE.md.
**Effort:** Simple

#### MAJOR: Inconsistent Method Naming for Position/State Access
**ID:** CON-FND-004
**Location:** `game/ai/interfaces/controllable.py`, `game/ai/combat_utils.py`, `game/engine/physics.py`
**Issue:** Position access uses inconsistent patterns:
- `IControllable.get_position()` - getter method
- `PhysicsBody.position` - direct property
- `get_position(entity)` helper in `combat_utils.py` - attempts both
The combat_utils helper exists specifically because of this inconsistency, adding an extra layer of indirection.
**Impact:** Code must handle multiple access patterns; the helper function's existence indicates the pattern is known to be inconsistent.
**Recommendation:** Standardize on property-based access (`position`, `velocity`, `rotation`) for data access, reserve `get_*()` for computed values or values requiring parameters. Update IControllable to use properties.
**Effort:** Complex

#### MAJOR: Class Naming Suffix Inconsistency - Service vs Manager vs System
**ID:** CON-FND-005
**Location:** `game/ai/strategy_manager.py`, `game/research/systems/research_service.py`, `game/engine/collision.py`
**Issue:** Similar singleton/stateless service classes use inconsistent suffixes:
- `StrategyManager` - "Manager" suffix
- `ResearchService` - "Service" suffix
- `CollisionSystem` - "System" suffix
- `StrategyMetadataService` - "Service" suffix
**Impact:** Unclear distinction between Manager/Service/System; cognitive overhead when naming new classes.
**Recommendation:** Establish naming convention: "Manager" for singletons with mutable state, "Service" for stateless business logic, "System" for ECS-style processors. Document in CLAUDE.md.
**Effort:** Simple (documentation) / Complex (renaming)

#### MINOR: Inconsistent Parameter Naming - entity vs ship vs obj vs candidate
**ID:** CON-FND-006
**Location:** `game/ai/combat_utils.py`, `game/ai/target_evaluator.py`, `game/ai/controller.py`
**Issue:** The same concept (a combat entity) is named differently across functions:
- `entity` in `get_position(entity)`, `get_rotation(entity)`
- `ship` in `get_hp_percent(ship)`, controller methods
- `candidate` in `TargetEvaluator` methods
- `obj` in `SpatialGrid.insert(obj)`
**Impact:** Minor cognitive overhead when reading code; unclear if different names imply different types.
**Recommendation:** Standardize on `entity` for generic combat entity parameters, `ship` when specifically expecting Ship type, `target` for targeting context.
**Effort:** Simple

#### MINOR: Inconsistent Docstring Format - Google Style vs reST vs Plain
**ID:** CON-FND-007
**Location:** Throughout shard
**Issue:** Three docstring styles are used:
- Google style: `game/core/exceptions.py`, `game/core/json_utils.py`
- reST/Sphinx style: `game/core/hex_math.py` module docstring
- Plain text with no structured params: `game/engine/spatial.py`
**Impact:** Inconsistent documentation appearance; automated doc generation may be harder.
**Recommendation:** Standardize on Google-style docstrings (already dominant). Update outliers.
**Effort:** Simple

#### MINOR: Boolean Property Naming - is_alive() vs is_alive Property
**ID:** CON-FND-008
**Location:** `game/ai/interfaces/controllable.py:139-148` vs usage
**Issue:** `IControllable.is_alive()` is an abstract method, but the adapter accesses `self._ship.is_alive` as a property. Both are used interchangeably in the codebase. The interface defines it as a method but the Ship implementation is a property.
**Impact:** Code must call `entity.is_alive()` via interface but `ship.is_alive` directly; the adapter bridges this but it's confusing.
**Recommendation:** Make `is_alive` a property in the interface (using `@property @abstractmethod` pattern).
**Effort:** Simple

#### MINOR: Inconsistent Type Hint Coverage
**ID:** CON-FND-009
**Location:** `game/core/logger.py:27-41` vs `game/core/json_utils.py`
**Issue:** `json_utils.py` has comprehensive type hints with `Union[str, Path]`, `Optional[Any]`, etc. `logger.py` has minimal type hints (`msg: str`) and some methods lack return type annotations.
**Impact:** IDE support and static analysis less effective in some modules.
**Recommendation:** Add return type hints to all public methods. Use `-> None` for void functions.
**Effort:** Simple

#### MINOR: Inconsistent Import Organization
**ID:** CON-FND-010
**Location:** `game/ai/controller.py:51-66`, `game/research/ui/research_scene.py:14-24`
**Issue:** Import grouping is inconsistent. `controller.py` mixes standard library (`logging`, `math`) with game imports without blank line separation. `research_scene.py` properly separates groups.
**Impact:** Minor readability issue; harder to identify external dependencies at a glance.
**Recommendation:** Follow PEP 8 import organization: stdlib, blank line, third-party, blank line, local imports.
**Effort:** Simple

#### MINOR: Magic Numbers in AI Layer
**ID:** CON-FND-011
**Location:** `game/ai/controller.py:445`, `game/ai/behaviors.py`
**Issue:** While most constants are properly centralized in `AIConfig`, some magic numbers remain:
- `if abs(ang_diff) > 5:` in `navigate_to()` - angle threshold
- `if abs(ang_diff) < 30 and distance > eff_stop_dist:` - thrust angle threshold
**Impact:** Harder to tune AI behavior; constants scattered.
**Recommendation:** Extract to `AIConfig` as `NAVIGATE_ROTATE_THRESHOLD = 5` and `NAVIGATE_THRUST_ANGLE_THRESHOLD = 30`.
**Effort:** Simple

#### MINOR: Inconsistent Error Handling - Broad Except vs Specific
**ID:** CON-FND-012
**Location:** `game/ai/controller.py:217-223`, `game/ai/interfaces/controllable.py:474-477`
**Issue:** Error handling inconsistency:
- `controller.py:218` catches specific `(AttributeError, TypeError)` with logging
- `controllable.py:475` catches `(AttributeError, ValueError)` with pass (silent)
**Impact:** Silent failures in controllable.py make debugging harder.
**Recommendation:** Add logging to all exception handlers, even for expected conditions. Use `log_debug` for expected cases.
**Effort:** Simple

#### MINOR: Inconsistent `__all__` Export Patterns
**ID:** CON-FND-013
**Location:** `game/core/constants.py:1-15`, `game/ai/__init__.py:93-110`
**Issue:** `constants.py` defines `__all__` at the top before definitions; `game/ai/__init__.py` defines it at the bottom after imports. Both work but inconsistent ordering.
**Impact:** Minor; harder to find exports quickly.
**Recommendation:** Standardize: Define `__all__` after imports but before class/function definitions for clarity.
**Effort:** Simple

#### MINOR: Redundant Protocol Definition
**ID:** CON-FND-014
**Location:** `game/core/validation.py:23-60` (IValidationRule), `game/core/protocols.py`
**Issue:** `IValidationRule` is defined in `validation.py`, while other protocols are in `protocols.py`. The validation module even has its own `@runtime_checkable` Protocol import.
**Impact:** Inconsistent location for protocol definitions; developers may not find IValidationRule when looking in protocols.py.
**Recommendation:** Move `IValidationRule` to `game/core/protocols.py` with other protocols, re-export from `validation.py` for backward compatibility.
**Effort:** Simple

#### INFO: os.path vs pathlib.Path Mixed Usage
**ID:** CON-FND-015
**Location:** `game/core/paths.py:53-103`
**Issue:** `Paths` class uses both `os.path.join` for class attributes (strings) and `pathlib.Path` for classmethod accessors. This is intentional (attributes are strings for backward compatibility) but creates two parallel access patterns.
**Impact:** Low - documented design decision, but developers must choose between `Paths.DATA_DIR` (str) and `Paths.get_data_dir()` (Path).
**Recommendation:** Document the pattern in class docstring. Consider deprecating string attributes in favor of Path methods over time.
**Effort:** Simple

#### INFO: ResourceType is a Class, Not an Enum
**ID:** CON-FND-016
**Location:** `game/core/constants.py:83-92`
**Issue:** `ResourceType` is a plain class with class attributes, while similar constants (`AttackType`, `GameState`, `LayerType`) are Enums. This is intentional (ResourceType values are strings used as dict keys) but inconsistent with the enum pattern used elsewhere.
**Impact:** Low - works correctly but unexpected pattern.
**Recommendation:** Document rationale in class docstring explaining why it's not an Enum (string values used as dict keys).
**Effort:** Simple

#### INFO: TechNode/TechTree Separate from Core Registry Pattern
**ID:** CON-FND-017
**Location:** `game/research/data/tech_tree.py`, `game/research/data/tech_node.py`
**Issue:** The research module uses its own data loading pattern (`TechTree.load_from_json()`) rather than integrating with the core `RegistryManager` pattern used for components/modifiers. This may be intentional since the tech tree is session-specific.
**Impact:** Low - the research system is a standalone sandbox and may not need registry integration.
**Recommendation:** If the research system will integrate with the main game, consider whether tech definitions should be in a registry. Otherwise, document that this is intentionally standalone.
**Effort:** N/A (design decision)

#### INFO: Research Layer Has Direct pygame Import
**ID:** CON-FND-018
**Location:** `game/research/ui/research_scene.py:14-15`
**Issue:** The research UI layer imports pygame directly (`import pygame`) and imports Camera from `game.ui.renderer.camera`. This creates a dependency from research -> UI layer, which may violate strict layer separation (research should depend on core/simulation, not UI).
**Impact:** Low for a standalone sandbox. Could be problematic if research logic needs to be tested without pygame.
**Recommendation:** Consider extracting research-specific Camera needs into a protocol or moving the research UI into `game/ui/` to maintain layer boundaries.
**Effort:** Complex

## Top 5 Priority Issues

1. **CON-FND-001 (CRITICAL): Singleton Pattern Inconsistency** - Having two singleton patterns creates confusion and maintenance burden. This should be standardized before adding more singletons.

2. **CON-FND-002 (MAJOR): Logging Pattern Inconsistency** - Mixed logging approaches make log configuration and debugging harder. Pick one pattern and migrate.

3. **CON-FND-004 (MAJOR): Position Access Pattern** - The existence of a helper function (`get_position()`) to handle inconsistent access patterns indicates this is a known pain point worth addressing.

4. **CON-FND-005 (MAJOR): Manager/Service/System Naming** - Clear naming conventions help developers understand class responsibilities at a glance. Document and enforce conventions.

5. **CON-FND-003 (MAJOR): Return Semantics for Not-Found** - Inconsistent error/default behavior leads to bugs. Establish and document a convention.
