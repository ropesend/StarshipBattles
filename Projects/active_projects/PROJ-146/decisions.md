# PROJ-146: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-13 | Project created from review | Review identified 145 findings; 35 selected for remediation |
| 2026-02-13 | Severity-based phasing | Critical findings in Phase 1, Major in Phase 2, etc. |
| 2026-02-14 | CON-FND-009 INTENTIONAL DESIGN | clear() empties registry contents, reset() destroys singleton - distinct concepts per SingletonMeta design |
| 2026-02-14 | CON-FND-011 INTENTIONAL DESIGN | __all__ exports match all public items; Colors/FONT_MAIN moved to ui.colors per PROJ-113 (documented) |
| 2026-02-14 | CON-FND-013 INTENTIONAL DESIGN | ErrorCode enum gaps (V002, C003) are reserved for future use - standard enum practice |
| 2026-02-14 | ADR-FND-004 POSITIVE | Informational finding confirming good architecture - core layer isolates strategy |
| 2026-02-14 | DUP-FND-008 POSITIVE | Informational finding confirming SingletonMeta provides consistent singleton pattern |
| 2026-02-14 | DUP-FND-009 POSITIVE | PROJ-108 already consolidated combat_utils - this finding documents success, not problem |
| 2026-02-14 | ADR-SIM-001 ALREADY FIXED | PROJ-126 moved ai_factory.py from game/simulation to game/ai - layer violation resolved |
| 2026-02-14 | ADR-SIM-002 ALREADY FIXED | PROJ-132 changed TYPE_CHECKING imports to use protocols from simulation.interfaces |
| 2026-02-14 | ADR-SIM-003 IMPROVED | BattleController reduced 848→659 LOC (22% reduction) - actively decomposed |
| 2026-02-14 | ADR-SIM-004 INTENTIONAL | Ship decomposition complete - 8 helper modules extracted, Ship.py is now facade |
| 2026-02-14 | ADR-SIM-005 INTENTIONAL | Late import in ship_stats.py is defensive pattern - no actual circular dependency |
| 2026-02-14 | ADR-SIM-006 ACCEPTABLE | Component.py 723 LOC is core domain model - well-documented, complexity inherent |
| 2026-02-14 | CON-SIM-009 ALREADY FIXED | Magic numbers extracted to constants (TURN_COMMITMENT_THRESHOLD_DEG, SimulationConstants) |
| 2026-02-14 | CON-SIM-012 INTENTIONAL | String-based type checking is correct for JSON-driven component system |
| 2026-02-14 | ADR-SIM-007 INTENTIONAL | TYPE_CHECKING extensive usage is Python standard for forward references |
| 2026-02-14 | CON-SIM-018 INTENTIONAL | Singleton pattern via SingletonMeta is project standard for registries |
| 2026-02-14 | CON-SIM-019 INTENTIONAL | ABILITY_REGISTRY module-level dict is Python standard factory pattern |
| 2026-02-14 | CON-SIM-020 INTENTIONAL | Late import comments document defensive programming - good practice |
| 2026-02-14 | ADR-STR-001 INTENTIONAL | PROJ-126 documented: strategy layer CAN depend on AI layer (simulation_adapter imports AIControllerFactory) |
| 2026-02-14 | ADR-STR-002 ACCEPTABLE | Galaxy 914 LOC is central world model with clear responsibilities (systems, spatial indexes, fleet/zone registry, serialization) |
| 2026-02-14 | CON-STR-004 INTENTIONAL | Engines use interface-based DI (IMovementEngine, IProductionEngine, etc. in engines.py) |
| 2026-02-14 | CON-STR-005 INTENTIONAL | FleetSpeedCalculator uses @staticmethod for stateless pure functions (no registry dependencies) |
| 2026-02-14 | ADR-STR-003 ACCEPTABLE | ProductionEngine 731 LOC - complex domain logic, well-structured with helper methods |
| 2026-02-14 | ADR-STR-004 ACCEPTABLE | FleetOrderProcessor 630 LOC - under 700 threshold, handles complex order processing |
| 2026-02-14 | ADR-STR-005 INTENTIONAL | TYPE_CHECKING for forward references is Python standard pattern |
| 2026-02-14 | CON-STR-014 NATURAL | Method signatures naturally vary based on domain requirements |
| 2026-02-14 | CON-STR-015 INTENTIONAL | StrategySessionFacade with DTOs enforces strict layer boundary via CQRS-lite |
| 2026-02-14 | CON-STR-016 INTENTIONAL | Fleet delegates to specialized calculators (FleetResourceAggregator, FleetCapabilityCalculator, FleetBattleAdapter) |
| 2026-02-14 | CON-STR-017 INTENTIONAL | EventType/EventCategory use str(Enum) inheritance for JSON serialization |
| 2026-02-14 | CON-STR-018 INTENTIONAL | Interface naming follows Python "I" prefix convention (IMovementEngine, etc.) |
| 2026-02-14 | ADR-UI2-001 FIXED | ShipFactory.configure_ship now accepts Union[Vector2, pygame.Vector2], converts to core Vector2 internally |
| 2026-02-14 | ADR-UI2-003 INTENTIONAL | Camera is renderer layer - correctly uses pygame Vector2 for direct pygame.draw operations |
| 2026-02-14 | ADR-UI2-006 PARTIAL FIX | ValidationService typed properly; ComponentService Any types match underlying IRegistryProvider protocol |
| 2026-02-14 | ADR-UI2-007 INTENTIONAL | DesignLoaderAdapter correctly provides DI + simplified API; runtime sim→UI imports allowed |
| 2026-02-14 | ADR-UI2-008 ACCEPTABLE | Screenshot manager direct attribute access works reliably; protocol abstraction low priority for INFO finding |
