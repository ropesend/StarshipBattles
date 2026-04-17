# PROJ-273: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-16 | Project initialized | Derived from combat system review. Eliminates duplicate ability→stat_key mapping between Battle Setup and Strategy compilers. |
| 2026-04-16 | Registry module lives at `game/simulation/combat/ability_stat_registry.py` | Both callers (UI + strategy layers) sit above simulation. Simulation layer has no upward deps. Natural home. |
| 2026-04-16 | Registry is a frozen `Dict[str, AbilityStatMapping]` keyed by ability class name | Matches how components.json serializes abilities (by class name string). Avoids circular import on ability classes themselves. |
| 2026-04-16 | Unknown stat_key in FleetAuraManager is WARN, not ERROR | Preserves forward-compat: data/designs/ can introduce a new ability before the registry is updated without hard-crashing battles. |
| 2026-04-16 | `_route_team_for_scope` return type stays `int` in this project | PROJ-275 (N-team combat) widens it to `List[int]`. Keeping this project narrow preserves execution ordering. |
| 2026-04-16 | Registry dict iteration order is the canonical emission order | Dict preserves insertion order in Python 3.7+. Tests that assert entry order remain stable. |
| 2026-04-16 | Glob-driven guard test replaces hardcoded 10-design list | Addresses skeptic finding H1 in `Projects/archived_projects/PROJ-270/findings/verification_2026_04_13_post_proj271/test_coverage_skeptic.md`. New complex designs auto-covered. |
