# PROJ-302: Star Intrinsic Ability Sources

> **PRECONDITION:** PROJ-300 (Universal IAbilitySource Framework) merged. PROJ-300 ships the shared `roll_intrinsic_abilities` and `format_intrinsic_source_label` helpers (per PROJ-300 D15) — PROJ-302 is a pure consumer. PROJ-301 is no longer a precondition for the helpers (was, in the original 2026-04-26 plan).

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-302` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-302 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Star types data registry | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. `Star.intrinsic_abilities` field + generation | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. `StarAbilitySource` adapter + iterator registration | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI verification + docs | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-27
**Active Phase:** Complete (post-remediation 2026-04-27)
**Last Action:** Skeptical-review remediation landed: critical/high fixes, RNG seeded, D16/D17/D13 validations, Phase-3 integration tests
**Next Action:** D20 perf baseline + final docs sync (low priority follow-up)
**Blockers:** None
**Context for Next Agent:** Read `Projects/active_projects/PROJ-300/design.md` first. Stars differ from planets in that most of their abilities are **system-scope** (radiation field across the entire system) rather than sector-scope. The `StarAbilitySource.affects_system` method returns True when the queried system contains the star; `affects_hex` returns True only at the star's hex (for sector-scope abilities like coronal flares).

## Overview

After PROJ-300 lands the unified framework and PROJ-301 adds planet intrinsics, this project adds **stars** as ability sources. A neutron star projects system-wide radiation, a red giant projects stellar heat, a binary projects gravitational lensing. Most star abilities are system-scope — they apply to every hex in the star system. Some star types may also project sector-scope abilities at the star's own hex (e.g. coronal flares).

## Goals
- New data registry: `data/star_types.json` declaring intrinsic ability templates per star type, with optional generation-time roll ranges.
- `Star.intrinsic_abilities: Dict[str, Any]` field populated at generation.
- `StarAbilitySource` adapter implementing `IAbilitySource`. Honors both system and sector scope.
- Adapter registered with the iterator.
- System panel (NOT just Sector panel) picks up system-scope star effects.
- Save/load roundtrip preserves rolled values.

## Scope

**In:**
- `data/star_types.json` schema + initial set of star types matching the existing star type taxonomy (verify against `game/strategy/data/star_generation_config.py` and `game/strategy/data/stars.py`).
- `Star.intrinsic_abilities` field.
- `StarAbilitySource` adapter.
- Iterator registration for both hex (sector-scope at star's hex) and system (system-scope).
- Save/load roundtrip.
- Documentation update.

**Out:**
- Star data layout changes beyond `intrinsic_abilities`. Existing star fields (radius_hexes, etc.) untouched.
- New scope keywords. `system`, `allied_system`, `sector` from PROJ-300 are sufficient.
- Combat consumption of stellar effects beyond what already flows through ShieldModifier/DamageModifier/etc.

## Key Files

| Component | File Path |
|-----------|-----------|
| Star type registry | `data/star_types.json` (NEW) |
| Path constant | `game/core/paths.py` |
| Star dataclass | `game/strategy/data/stars.py` (confirm during Phase A) |
| Star generator | `game/strategy/generation/` (locate the star placement / type assignment file) |
| Adapter | `game/strategy/services/ability_sources/star.py` (NEW) |
| Iterator registration | `game/strategy/services/ability_iterator.py` |

## Related Documents
- [design.md](design.md) — Architecture, schema, system-vs-sector scope behavior.
- [decisions.md](decisions.md) — Decisions log.
- [manifest.md](manifest.md) — File manifest.
- **PRECONDITION**: [`Projects/active_projects/PROJ-300/`](../PROJ-300/).

## Verification

- [ ] Manual smoke test: generate a galaxy, click on any hex inside a system whose star is a neutron star — System panel shows `Radiation Field — Active (<star.name> (Neutron Star))`. Click on the star's own hex — Sector panel shows any sector-scope effects (coronal flares).
- [ ] Save/load preserves rolled values.
- [ ] `pytest tests/ --testmon` clean.
- [ ] `python Tools/test_sharded/test_sharded.py` clean.
- [ ] All phase checklists complete.
- [ ] User verified.
