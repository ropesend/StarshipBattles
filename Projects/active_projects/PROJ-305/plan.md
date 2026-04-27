# PROJ-305: Fleet Strategic-Layer Ability Sources

> **PRECONDITION:** PROJ-300 (Universal IAbilitySource Framework) merged. Recommended that PROJ-301..304 are also merged so the framework's behavior under multiple source kinds is well-tested before adding the most complex source kind (fleets).

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Expand component ability `allowed_scopes` for strategic scopes | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. `FleetAbilitySource` adapter + iterator registration | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Sample component (Flagship Shield Projector) + integration | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Performance check + UI verification + docs | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-26
**Active Phase:** Planning (plan approved, awaiting PROJ-300 completion)
**Last Action:** Project documents populated from approved master plan
**Next Action:** Wait for PROJ-300, then begin Phase 1
**Blockers:** PROJ-300 framework
**Context for Next Agent:** Read `Projects/active_projects/PROJ-300/design.md` first. **Per user decision**, fleet abilities are **strategic-layer hex effects** — a flagship at hex H projects sector-scope abilities visible in the Sector panel for entities at H. This is distinct from existing combat-only fleet auras (handled by `FleetAuraManager`); those continue to function unchanged. The unification adds a NEW capability: ship components can now declare strategic-scope abilities (sector / system / allied_sector / etc.) that are picked up by the unified collector and rendered in the strategy UI.

## Overview

After PROJ-300..304 land, planets-themselves, stars, warp points, system archetypes, storms, and facilities all flow through the unified ability framework. This final project adds **fleets/ships** — a fleet at hex H projects sector-scope abilities visible to other entities at H on the strategy map. A flagship with a "Shield Projector" component (`ShieldModifier scope: allied_sector`) buffs allied ships sharing the hex; future components can extend the pattern.

> **2026-04-27 update (decisions.md D10):** original plan referenced a `SensorBoost` ability that does not exist in the codebase. Inventing it is a separate design item. PROJ-305 sample component now uses `ShieldModifier`, which already supports `allied_sector` ([planetary.py:443](../../game/simulation/components/abilities/planetary.py#L443)). PROJ-305 is plumbing only.

This is structurally distinct from the existing combat-only `FleetAuraManager`, which handles `scope: fleet` and `scope: team` aura abilities during battle. Those continue to function unchanged. PROJ-305 adds a parallel **strategic** projection path, gated by scope: components declare `scope: sector` (or system) → strategic-layer projection; `scope: fleet` (or team) → combat-internal aura.

## Goals
- Expand component ability `allowed_scopes` lists where appropriate so ship components can legitimately declare strategic-scope abilities (sector / system / allied_sector / enemy_sector). Tests for scope validation.
- `FleetAbilitySource` adapter wrapping a Fleet, walking its ships, walking their components, gathering abilities with strategic scopes (NOT combat-only scopes).
- Iterator registration: fleets at the queried hex contribute to sector effects.
- Sample component definition: `data/components.json` adds a "Flagship Shield Projector" with `ShieldModifier scope: allied_sector` (multiplier 1.25) — proves the integration works end-to-end. *(Per D10: re-uses an already-existing ability; no new ability classes invented in this project.)*
- Tests covering scope-filter-correctness (combat scopes don't leak into strategic projection; strategic scopes don't leak into combat aura).
- Performance check: fleet movements should not cause performance regression in the collector. Add caching if needed.
- UI: fleet provider in Sector Effects shows `source_label = "Flagship 'Indomitable' (Player 1)"`.

## Scope

**In:**
- Audit and update `allowed_scopes` lists on existing ability classes (`game/simulation/components/abilities/`) where strategic-scope projection makes design sense (e.g. ShieldModifier already supports sector via storms; SensorBoost should add it; some abilities are intentionally combat-only and stay that way).
- `FleetAbilitySource` adapter in `game/strategy/services/ability_sources/fleet.py`.
- Iterator registration so fleets-at-hex are picked up alongside other source kinds.
- One sample component (e.g. Flagship Sensor Array) demonstrating the new capability.
- Caching at the collector level if profiling shows regression — keyed by `(hex, empire_id, turn)`.
- UI verification + docs.

**Out:**
- Cloak/stealth interactions with fleet ability projection — flagged as a TODO; treat per-ability-type when stealth design comes up.
- Combat consumption of any new strategic abilities. Fleet abilities flow into the Sector Effects panel; combat consumption (if any) goes through the existing path that PROJ-300 generalized.
- Wholesale review of every component ability's `allowed_scopes` — only update those where strategic projection is design-meaningful.

## Key Files

| Component | File Path |
|-----------|-----------|
| Ability base/scope validation | `game/simulation/components/abilities/base.py` |
| Specific ability classes | `game/simulation/components/abilities/` (multiple files — defense.py, propulsion.py, etc.) |
| Fleet dataclass | `game/strategy/data/fleet.py` |
| Adapter | `game/strategy/services/ability_sources/fleet.py` (NEW) |
| Iterator registration | `game/strategy/services/ability_iterator.py` |
| Sample component | `data/components.json` |
| Collector caching (if needed) | `game/strategy/services/system_effects_collector.py` |

## Related Documents
- [design.md](design.md) — Architecture, scope dichotomy, performance plan, sample component spec.
- [decisions.md](decisions.md) — Decisions log.
- [manifest.md](manifest.md) — File manifest.
- **PRECONDITION**: [`Projects/active_projects/PROJ-300/`](../PROJ-300/).

## Verification
- [ ] Manual smoke test: A fleet equipped with a Flagship Sensor Array component sits on a hex. Click that hex with a friendly fleet — Sector panel shows `Sensor Boost — Active (Flagship 'Indomitable' (Player 1))` for the friendly viewer.
- [ ] Click the same hex with an enemy fleet — confirm `allied_sector`-scoped abilities are NOT shown to the enemy.
- [ ] Move the fleet to another hex; confirm the effect follows the fleet.
- [ ] Combat in the same hex — confirm `scope: fleet` combat-only abilities still function (not leaked into Sector panel; not double-applied).
- [ ] Performance: galaxy with 100 systems × 10 fleets — `collect_sector_effects` cost stays within target (define target during Phase 4 profiling).
- [ ] `python Tools/test_sharded/test_sharded.py` clean.
- [ ] User verified.
