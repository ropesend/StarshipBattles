# Pattern Cataloguer Report

## Summary
- Total issues found: 17
- Critical: 1, Major: 4, Minor: 6, Info: 6
- Patterns catalogued: 17

## Pattern Catalog

### Registry Pattern — Mature, 7 implementations, Excellent consistency
### Singleton Pattern — Mature via SingletonMeta metaclass, Excellent consistency
### Protocol Pattern — Partial (15 protocols but 606+ hasattr calls suggest 50+ more needed)
### Facade Pattern — Strategic use for god class decomposition (PROJ-87)
### Command Handler Registry — New, single implementation, not yet generalized
### Template Method — Validation only, missing for Loaders/Calculators/Processors
### Strategy Pattern — Ad-hoc, 2 implementations in different domains
### Factory Pattern — Underutilized, 3 inconsistent implementations
### Builder Pattern — Ad-hoc, no consistent pattern
### Service Pattern — Mature, 18 services, Excellent consistency
### Manager Pattern — Overused antipattern (25 classes), refactoring in progress
### Observer/Event Pattern — UI only (EventBus), missing from domain layers
### DTO Pattern — Partial, 98 dataclasses but 57 duplicate conversion methods
### Validator Pattern — Partial, 7 validators, no shared base class
### Loader/Parser Pattern — No base class, 9 loaders with duplicate file I/O
### Calculator/Aggregator Pattern — Ad-hoc, 9 calculators with similar structure
### Two-Stage Aggregation — Mature, documented architecture pattern

## Findings

### CRITICAL: Manager Pattern — God Class Indicator
**ID:** PC-011
**Location:** 25 manager classes across game/
**Issue:** "Manager" suffix used for 3 different patterns: legitimate singletons, utility namespaces, and god classes
**Impact:** God class managers violate SRP, utility managers should be functions/services
**Deliberate?:** Partially — god class refactoring underway (PROJ-86/87/88/89)
**Recommendation:** Rename utility managers, decompose god classes, reserve "Manager" for singleton coordinators
**Effort:** Major (part of PROJ-86/87/88/89)

### MAJOR: Protocol Pattern — 590+ hasattr Calls Without Type Safety
**ID:** PC-003
**Location:** 606 hasattr/getattr calls across 131 files vs 15 protocols in core/protocols.py
**Issue:** Only ~15 protocols defined but 606 hasattr/getattr calls suggest 50+ candidates needed
**Impact:** Type safety gaps, poor IDE support, refactoring difficulty
**Deliberate?:** Partially — protocols exist but not systematically applied
**Recommendation:** Extract 20-30 new protocols, replace hasattr with isinstance(Protocol) checks
**Effort:** Major (2-3 weeks)

### MAJOR: Observer Pattern — Missing Domain Events
**ID:** PC-012
**Location:** `game/ui/screens/builder/event_bus.py` — only implementation
**Issue:** Event bus only in UI. Strategy/simulation layers use direct method calls. No domain events.
**Impact:** Tight coupling in TurnEngine/BattleEngine. Hard to extend, no event replay.
**Deliberate?:** No — EventBus added for UI refactoring, not generalized
**Recommendation:** Extract EventBus to core, create DomainEventBus, emit events from engines
**Effort:** Major (2-3 weeks)

### MAJOR: DTO Pattern — 57 Duplicate Conversion Methods
**ID:** PC-013
**Location:** 57 to_dict/from_dict methods across 18 files, 98+ @dataclass decorations
**Issue:** No base class, each DTO reimplements field mapping logic
**Impact:** Fragility, duplication, no centralized validation
**Deliberate?:** No — DTOs added per-feature without unifying abstraction
**Recommendation:** Create BaseDTOConverter with generic field mapping
**Effort:** Major (2-3 weeks)

### MAJOR: Loader Pattern — 9 Loaders With Duplicate File I/O
**ID:** PC-015
**Location:** 9 loader/parser classes in strategy/generation/loaders, simulation, UI
**Issue:** No base class, ~100 lines of duplicate open/json.load/error handling code
**Deliberate?:** No — loaders added per-feature
**Recommendation:** Create BaseJSONLoader template method class
**Effort:** Medium (1 week)

### MINOR: Command Handler Registry — Limited Adoption
**ID:** PC-005
**Location:** `game/strategy/engine/command_handlers.py`
**Issue:** Pattern extracted for GameSession but not generalized to UI event routing, input handling, order processing
**Deliberate?:** Partially — introduced for one use case
**Recommendation:** Generalize to game/core/, apply to 3-5 dispatch sites
**Effort:** Medium (1 week)

### MINOR: Template Method — Missing for Loaders/Calculators/Processors
**ID:** PC-006
**Location:** Validation only (1 ABC), 27 files could use template method
**Issue:** 9 loaders, 9 calculators, 9 processors all have common structure without base class
**Recommendation:** Create BaseLoader, BaseCalculator, BaseProcessor templates
**Effort:** Medium (1-2 weeks)

### MINOR: Strategy Pattern — Ad-hoc Usage
**ID:** PC-007
**Location:** UI grouping (3 strategies), galaxy placement
**Issue:** Not applied to AI targeting, pathfinding, damage calculation
**Recommendation:** Extract ITargetingStrategy, IPathfindingStrategy
**Effort:** Medium per extraction

### MINOR: Factory Pattern — Underutilized
**ID:** PC-008
**Location:** AIControllerFactory, ShipFactory, create_ability()
**Issue:** 3 implementations with different patterns. 57 manual from_dict methods suggest factory gap.
**Recommendation:** Create DTOFactory base, extract ShipInstantiationFactory
**Effort:** Medium (1-2 weeks)

### MINOR: Builder Pattern — Missing Consistent Implementation
**ID:** PC-009
**Location:** QuickstartBuilder (fluent), UI builders (procedural)
**Issue:** Inconsistent, missing for ship design, galaxy generation, battle setup
**Recommendation:** Create builders for complex object construction
**Effort:** Low-Medium (3-5 days per builder)

### MINOR: Validator Pattern — No Shared Base Class
**ID:** PC-014
**Location:** 7 validators, no common base despite similar structure
**Issue:** Duplicate guard clauses, no shared validation primitives
**Recommendation:** Create BaseValidator with common helpers
**Effort:** Low-Medium (3-5 days)

### INFO: Registry Pattern — Mature and Consistent
**ID:** PC-001
**Issue:** 7 registry implementations, excellent consistency, DI-enabled

### INFO: Singleton Pattern — Clean Metaclass Implementation
**ID:** PC-002
**Issue:** Thread-safe SingletonMeta, consistent usage, test-friendly reset()

### INFO: Facade Pattern — Strategic Use
**ID:** PC-004
**Issue:** StrategySessionFacade with CQRS-lite, part of PROJ-87

### INFO: Service Pattern — Mature
**ID:** PC-010
**Issue:** 18 services, excellent consistency, DI via GameRegistries

### INFO: Calculator/Aggregator Pattern
**ID:** PC-016
**Issue:** 9 calculators with similar structure, could benefit from base class

### INFO: Two-Stage Aggregation — Well-Adopted
**ID:** PC-017
**Issue:** Core architecture pattern, excellent consistency

## Top 5 Priority Issues

1. **PC-012 (Major):** Observer Pattern — Missing Domain Events
2. **PC-013 (Major):** DTO Pattern — 57 Duplicate Conversion Methods
3. **PC-003 (Major):** Protocol Pattern — 590+ hasattr Without Type Safety
4. **PC-015 (Major):** Loader Pattern — 9 Loaders Duplicating File I/O
5. **PC-006 (Minor):** Template Method — Missing for 27 Files
