# PROJ-287: Race Registry Facade + Empire.resident_species

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-287` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-287 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. `IRaceRegistry` protocol + `CachedRaceRegistry` impl | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Facade exposure: `StrategySessionFacade.get_race_registry()` | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. `Empire.resident_species()` derived helper | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Docs + cleanup | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-18
**Active Phase:** Planning complete; ready to begin Phase 1
**Last Action:** Project scaffolded. Scope and decisions captured from user design session 2026-04-18.
**Next Action:** Phase 1 Task 1.1 — design and implement `IRaceRegistry` protocol with `CachedRaceRegistry` in-memory implementation. This is the infrastructure primitive PROJ-288, 289, 290 all depend on for resolving `race_id → RaceConfig`.
**Blockers:** None. Independent of PROJ-286.
**Context for Next Agent:** Today `RaceLibrary` at `game/strategy/systems/race_library.py` is file-backed and loads from `output/races/*.json` on every `get_race(race_id)` call. The new UI work (PROJ-289, 290) hits this on every frame for every species on every colony — unacceptable. We need a cached `IRaceRegistry` protocol with `get_race(race_id) -> Optional[RaceConfig]` + invalidation hook, exposed through the `StrategySessionFacade` so panels can pull it once per session. The `Empire.resident_species()` helper returns `Set[str]` of race_ids with `count >= 1` anywhere in the empire's colonies — defined by user decision 2026-04-18 as the canonical "species in this empire" set for UI iteration.

## Overview

Add a cached race-registry protocol + facade exposure so UI panels can resolve `race_id → RaceConfig` without hitting the filesystem per call. Add `Empire.resident_species() -> Set[str]` as the canonical "which species live in this empire" query used by all downstream UI projects (notably PROJ-290's uncolonized-habitability display).

## Goals

- `IRaceRegistry` protocol at `game/core/protocols.py` — one method: `get_race(race_id: str) -> Optional[RaceConfig]`.
- `CachedRaceRegistry` implementation at `game/strategy/systems/race_library.py` (or a new sibling file) — wraps `RaceLibrary`, caches results on first access, exposes an `invalidate()` method for race-editor save flows.
- `StrategySessionFacade.get_race_registry() -> IRaceRegistry` — single shared instance per session.
- `Empire.resident_species() -> Set[str]` — derived property returning race_ids with `count >= 1` across `self.colonies`.
- Existing `PopulationEngine._get_race_config` + `HappinessEngine._get_race_config` can OPTIONALLY migrate to read from the registry (out of scope if risky; defer).
- Full sharded suite green.

## Scope

**In:**
- `IRaceRegistry` protocol + `CachedRaceRegistry` class + tests.
- `StrategySessionFacade.get_race_registry()` method.
- `Empire.resident_species()` helper + tests.
- Cache invalidation hook + one caller (race-save flow) that invokes it.
- Unit tests for the cache: first-call loads from library, second-call uses cache, invalidate() clears.

**Out:**
- Replacing `RaceLibrary` itself (file-backed) — the registry wraps it.
- Migrating `PopulationEngine` / `HappinessEngine` to use the new registry — they already have working race-config resolution. Optional future cleanup.
- Multi-race engine support (some future feature where engines iterate `resident_species()` themselves). Out of scope.

## Key Files

| Component | File Path |
|-----------|-----------|
| `IRaceRegistry` protocol | `game/core/protocols.py` |
| `CachedRaceRegistry` implementation | `game/strategy/systems/race_library.py` or new `race_registry.py` |
| `StrategySessionFacade.get_race_registry` | `game/strategy/facade/strategy_session_facade.py` |
| `Empire.resident_species` | `game/strategy/data/empire.py` |

## Related Documents
- [design.md](design.md) — Architecture rationale (cache strategy, invalidation)
- [decisions.md](decisions.md) — Decisions log
- [manifest.md](manifest.md) — Full file manifest

## Related Projects

| PROJ | Relationship |
|------|--------------|
| PROJ-286 | Parallel — no overlap (different files) |
| PROJ-288 | Consumer — uses `get_race_registry()` + `resident_species()` for projection helpers |
| PROJ-289 | Consumer — planet report panel iterates species on a colony, resolves race_config via registry |
| PROJ-290 | Consumer — uncolonized habitability iterates `empire.resident_species()` and scores each against the planet |

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing via `python Tools/test_sharded/test_sharded.py`
- [ ] Manual scenario:
  - [ ] Start game → open strategy screen → confirm no new per-frame filesystem reads (check via logging that `RaceLibrary.get_race` is called once per race_id per session).
  - [ ] Edit a race in the race editor, save → confirm the registry invalidates and the next read returns fresh data.
- [ ] User verified end-to-end.
