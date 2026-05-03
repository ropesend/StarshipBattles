# Deliberate Design Reviewer Report

## Summary
- Total issues found: 38
- Critical: 0, Major: 5, Minor: 15, Info: 18
- Likely deliberate: 22, Likely accidental: 3, Could go either way: 8, Probably deliberate: 5

## Findings (Top Priority — "Could Go Either Way" Items)

### Major: StrategyScreen Properties Break Facade Pattern
**ID:** DD-006
**Location:** `game/ui/screens/strategy_screen.py:126-148`
**Looks Wrong Because:** 6 properties expose domain objects (galaxy, empires, player_empire) despite having self._facade for proper UI-to-engine communication
**Might Be Intentional Because:** Comments say "for internal convenience", sub-modules may need direct access
**Confidence:** Could go either way
**Recommendation:** Investigate — either enforce DTO-only or remove facade pretense
**Effort:** Medium

### Major: StrategySessionFacade Internal Methods Return Domain Objects
**ID:** DD-018
**Location:** `game/strategy/facade/strategy_session_facade.py:79-90`
**Looks Wrong Because:** Facade should only expose DTOs but private methods return Fleet domain objects
**Might Be Intentional Because:** Private methods for internal use, public methods do return DTOs, mid-migration (PROJ-87)
**Confidence:** Could go either way
**Recommendation:** Enforce DTO-only or document why private methods are exempt
**Effort:** Medium

### Major: TestLabScreen 1906 Lines
**ID:** DD-003
**Location:** `game/ui/screens/test_lab/screen.py` (1906 lines)
**Looks Wrong Because:** Largest file, violates SRP, not yet refactored like StrategyScreen was
**Might Be Intentional Because:** Has extracted sub-modules, may await PROJ-89 refactoring
**Confidence:** Could go either way
**Recommendation:** Refactor with delegates like StrategyScreen pattern
**Effort:** Complex

### Major: Galaxy Class 928 Lines
**ID:** DD-032
**Location:** `game/strategy/data/galaxy.py` (928 lines)
**Looks Wrong Because:** Should be data container but has pathfinding, system placement, querying logic
**Might Be Intentional Because:** Many methods are simple lookups, PROJ-87 may address
**Confidence:** Could go either way
**Recommendation:** Investigate further decomposition
**Effort:** Medium

### Major: 365 Getattr Calls Suggest Duck Typing
**ID:** DD-017
**Location:** 86 files
**Looks Wrong Because:** Heavy use of getattr(obj, 'attr', default) hides missing attributes, poor IDE support
**Might Be Intentional Because:** Backwards compatibility during refactoring, protocol-based design
**Confidence:** Could go either way
**Recommendation:** Add Optional type hints or use proper Protocol definitions
**Effort:** Medium

## Other Notable Findings

### Probably Deliberate (Accept)
- **DD-001:** RegistryManager Singleton — Almost certainly deliberate, documented migration
- **DD-008:** Deep Copy with PERF-ANALYSIS — Almost certainly deliberate, documented trade-off
- **DD-010:** Ability Index O(1) — Almost certainly deliberate, performance critical
- **DD-011:** INTENTIONAL LATE IMPORT pattern — Almost certainly deliberate, documented in ARCHITECTURE.md
- **DD-013:** Intentional broad exception catches — Almost certainly deliberate, all 3 commented
- **DD-020:** Fleet delegate pattern — Almost certainly deliberate, PROJ-87 decomposition
- **DD-023:** No save migration — Almost certainly deliberate, explicit policy in CLAUDE.md
- **DD-026:** Protocol over inheritance — Almost certainly deliberate, PROJ-40 decision
- **DD-028:** Adapter pattern — Almost certainly deliberate, clean layer separation
- **DD-029:** CQRS-Lite — Probably deliberate, standard game state management
- **DD-033:** No ABC usage — Almost certainly deliberate, Protocol preferred
- **DD-034:** Public mutable attributes — Almost certainly deliberate, Python convention

### Probably Deliberate But Worth Monitoring
- **DD-002:** Static methods + singletons — Different tools for different purposes
- **DD-005:** Game class 705 lines — Appropriate as composition root
- **DD-007:** Ship properties expose state — Caching pattern (PROJ-49)
- **DD-009:** HP ratio caching — PROJ-49 optimization
- **DD-019:** ShipPhysicsMixin getattr — Mixin flexibility
- **DD-024:** Constants in class namespaces — Self-documenting grouping
- **DD-025:** Mixed enum styles — Right tool for right job
- **DD-027:** MVVM with EventBus — Pays off for complex UI
- **DD-030:** Manual resource tracking — Game resources ≠ system resources
- **DD-031:** Ship 810 lines — Mid-refactoring (PROJ-88)

### Could Go Either Way (Investigate)
- **DD-012:** Pygame imports in simulation — Check if simulation layer imports pygame.math.Vector2
- **DD-015:** Zero type: ignore comments — Unclear if type checking enforced
- **DD-022:** pygame display surface reuse check — Unclear purpose
- **DD-037:** Mixed magic numbers vs named constants — Common in development

### Additional Context
- **DD-035:** Dual registry access (Singleton + DI) — Migration in progress, should complete
- **DD-038:** Incomplete DI migration — PROJ-38/50 phased, should continue

## Top 5 Priority Issues (Focus: "Could Go Either Way")

1. **DD-006:** StrategyScreen facade bypass — High severity, investigate intent
2. **DD-018:** Facade returning domain objects — High severity, undermines pattern
3. **DD-003:** TestLabScreen 1906 lines — High severity, needs refactoring
4. **DD-032:** Galaxy 928 lines — High severity, needs decomposition analysis
5. **DD-017:** 365 getattr calls — Medium severity, needs type audit
