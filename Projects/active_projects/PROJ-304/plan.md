# PROJ-304: Star System Archetype Ability Sources

> **PRECONDITION:** PROJ-300 (Universal IAbilitySource Framework). PROJ-301 strongly recommended (provides `roll_intrinsic_abilities`).

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. System archetypes data registry | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. `StarSystem.archetype` + `intrinsic_abilities` fields + generation | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. `SystemAbilitySource` adapter + iterator registration | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI verification + docs | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-26
**Active Phase:** Planning (plan approved, awaiting PROJ-300 completion)
**Last Action:** Project documents populated from approved master plan
**Next Action:** Wait for PROJ-300, then begin Phase 1
**Blockers:** PROJ-300 framework
**Context for Next Agent:** Read `Projects/active_projects/PROJ-300/design.md` first. This project adds the **`StarSystem` entity itself** as an ability source, distinct from the contents (stars, planets, warp points) within it. A "nebula system" archetype projects sector-scope sensor obscuration across every hex; an "ancient battlefield" projects sector-scope salvage opportunities; a "precursor ruins" system projects exploration bonuses. System archetypes are an additional, optional layer of randomization at galaxy generation.

## Overview

After PROJ-300..303 land, the framework supports facilities, storms, planets-themselves, stars, warp points. This project adds **the system itself** — a new `archetype: Optional[str]` field on `StarSystem` that, if set, points to an entry in `data/system_archetypes.json` declaring system-scope abilities. A nebula system, an ancient battlefield, a precursor ruins — each is a system-wide flavor with mechanical effects.

Unlike previous projects, archetype assignment is OPTIONAL — most systems have `archetype = None` and project no system-level abilities of their own. Galaxy generation rolls archetypes onto a configurable percentage of systems.

## Goals
- New data registry: `data/system_archetypes.json`.
- `StarSystem.archetype: Optional[str]` and `StarSystem.intrinsic_abilities: Dict[str, Any]` fields.
- Galaxy generation rolls archetypes onto a configurable percentage (e.g. 10–20%) of systems.
- `SystemAbilitySource` adapter implementing `IAbilitySource`.
- Adapter registered with the iterator; archetype effects appear in System panel.
- Save/load roundtrip preserves archetype + rolled values.

## Scope

**In:**
- `data/system_archetypes.json` schema + initial archetypes: `nebula`, `ancient_battlefield`, `precursor_ruins`, `ion_field`, `void`.
- `StarSystem.archetype` (Optional[str]) and `StarSystem.intrinsic_abilities` (Dict[str, Any]) fields.
- Galaxy generator integration — assign archetypes to a percentage of generated systems.
- `SystemAbilitySource` adapter.
- Iterator registration.
- Save/load roundtrip.
- Documentation update.

**Out:**
- Visual map decoration for archetypes (e.g. nebula clouds rendered behind a nebula system) — that's a UI flavor project.
- Archetype-specific gameplay events (e.g. "discovering precursor ruins triggers a research event") — those are research/event-system features, not ability framework.

## Key Files

| Component | File Path |
|-----------|-----------|
| System archetype registry | `data/system_archetypes.json` (NEW) |
| Path constant | `game/core/paths.py` |
| StarSystem dataclass | `game/strategy/data/galaxy.py` |
| Galaxy generator | `game/strategy/generation/` (galaxy generation entry; locate during Phase A) |
| Adapter | `game/strategy/services/ability_sources/system.py` (NEW) |
| Iterator registration | `game/strategy/services/ability_iterator.py` |

## Related Documents
- [design.md](design.md) — Architecture, schema, archetype assignment percentage.
- [decisions.md](decisions.md) — Decisions log.
- [manifest.md](manifest.md) — File manifest.
- **PRECONDITION**: [`Projects/active_projects/PROJ-300/`](../PROJ-300/).

## Verification
- [ ] Manual smoke test: generate a galaxy with archetype rolling enabled. Find a nebula system. Click any hex inside — System panel shows nebula effects (e.g. sensor obscuration / shield modifier).
- [ ] Save/load preserves archetype + rolled values.
- [ ] `python Tools/test_sharded/test_sharded.py` clean.
- [ ] User verified.
