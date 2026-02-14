# PROJ-147: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-14 | Project created from review | Review identified 241 findings; 19 selected for remediation |
| 2026-02-14 | Severity-based phasing | Critical findings in Phase 1, Major in Phase 2, etc. |
| 2026-02-14 | Phase 2 ADR-SIM-001: No action | Ship class already decomposed; report says "monitoring only" |
| 2026-02-14 | Phase 2 ADR-SIM-002: No action | Intentional late imports are documented architectural decision |
| 2026-02-14 | Phase 2 ADR-SIM-003: Deferred | MINOR severity; 100+ import sites makes cost > benefit |
| 2026-02-14 | Phase 3 ADR-STR-001: Fixed | Removed module-level AI import; added DI pattern with late import fallback |
| 2026-02-14 | Phase 3 ADR-STR-002: No action | ShipDisplayFormatter intentionally in strategy layer - docstring documents rationale (no pygame deps, pure string formatting) |
| 2026-02-14 | Phase 3 ADR-STR-003: No action | Intentional late import pattern (line 468) - documented in comment, per ARCHITECTURE.md |
| 2026-02-14 | Phase 3 ADR-STR-004: No action | Same as ADR-SIM-002/STR-003 - documented intentional pattern |
| 2026-02-14 | Phase 3 ADR-STR-005: No action | RGB tuples in game_config.py - docstring explains they're game-semantic identifiers, not pygame types |
| 2026-02-14 | Phase 4 ADR-UI2-001: Fixed | ShipIO now uses DesignLoaderAdapter for ship loading; TYPE_CHECKING for Ship type hints |
| 2026-02-14 | Phase 4 ADR-UI2-002: No action | Camera using pygame.math.Vector2 is intentional - it's a pygame rendering component; core Vector2 is for layer-agnostic code |
| 2026-02-14 | Phase 4 ADR-UI2-003: Fixed | Moved ShipThemeManager import to module level in game_renderer.py |
