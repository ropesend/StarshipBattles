# PROJ-303: Warp Point Intrinsic Ability Sources

> **PRECONDITION:** PROJ-300 (Universal IAbilitySource Framework). PROJ-300 ships the shared `roll_intrinsic_abilities` + `format_intrinsic_source_label` helpers (D15); PROJ-303 is a pure consumer. PROJ-301 is no longer a precondition for the helpers.

> **2026-04-27 review note:** the original plan treated `WarpPoint` types as an existing concept that just needed registry-ifying. Verified during review: `WarpPoint` ([game/strategy/data/galaxy.py:34-72](../../../game/strategy/data/galaxy.py#L34)) currently has only `destination_id`, `location`, `to_dict`, `from_dict` — there is no `type` field. PROJ-303 is therefore introducing the warp-point-type concept itself, not just registry-driving an existing taxonomy. Phase 1 must add a `type: str` field to `WarpPoint` AND the type registry. Re-scope or split if this becomes too large for a 4-phase project.

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Warp point types data registry | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. `WarpPoint.intrinsic_abilities` field + generation | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. `WarpPointAbilitySource` adapter + iterator registration | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. UI verification + docs | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-04-27
**Active Phase:** Complete (post-remediation 2026-04-27)
**Last Action:** Skeptical-review remediation landed: critical/high fixes, RNG seeded, D16/D17/D13 validations, Phase-3 integration tests
**Next Action:** D20 perf baseline + final docs sync (low priority follow-up)
**Blockers:** None
**Context for Next Agent:** Read `Projects/active_projects/PROJ-300/design.md` first. Warp points are fixed single-hex entities that can declare sector-scope intrinsic abilities (warp shear, navigational hazard, scan obscuration). Most are mechanically simpler than stars/planets — single sector, no system-scope reach.

## Overview

Adds warp points as ability sources. An "unstable" warp point projects sector-scope warp shear damaging passing ships; a "dimensional rift" interferes with sensors; a "stable" warp point has no intrinsic effects. Adds variety and danger to traversing systems via specific warp paths.

## Goals
- New data registry: `data/warp_point_types.json`.
- `WarpPoint.intrinsic_abilities` field.
- `WarpPointAbilitySource` adapter.
- Iterator registration.
- Save/load roundtrip.
- Documentation update.

## Scope

**In:**
- `data/warp_point_types.json` — initial types: `stable`, `unstable`, `dimensional_rift`, `precursor_gateway` (or whatever taxonomy currently exists; verify in `game/strategy/data/`).
- `WarpPoint.intrinsic_abilities` field.
- `WarpPointAbilitySource` adapter (sector-scope only).
- Iterator registration.
- Save/load roundtrip.

**Out:**
- New warp_point types beyond confirming the existing taxonomy. (If only one type exists today, add at least one new "unstable" type to give the system substance — coordinate with the user before doing so.)
- Warp travel mechanics changes. Existing warp behavior is unaffected; this project only adds stationary intrinsic effects at the warp point's hex.

## Key Files
| Component | File Path |
|-----------|-----------|
| Warp point type registry | `data/warp_point_types.json` (NEW) |
| Path constant | `game/core/paths.py` |
| Warp point dataclass | `game/strategy/data/` (find the warp_point file) |
| Generator | `game/strategy/generation/` |
| Adapter | `game/strategy/services/ability_sources/warp_point.py` (NEW) |
| Iterator registration | `game/strategy/services/ability_iterator.py` |

## Related Documents
- [design.md](design.md)
- [decisions.md](decisions.md)
- [manifest.md](manifest.md)
- **PRECONDITION**: [`Projects/active_projects/PROJ-300/`](../PROJ-300/).

## Verification
- [ ] Manual smoke test: generate a galaxy with at least one unstable warp point. Click on its hex — Sector panel shows warp-shear effects.
- [ ] Sail a fleet through an unstable warp point hex; verify the appropriate damage/effect applies.
- [ ] Save/load preserves rolled values.
- [ ] `python Tools/test_sharded/test_sharded.py` clean.
- [ ] User verified.
