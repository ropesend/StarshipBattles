# PROJ-461: ShipInstance LOC reduction (F-A-007 spinout from PROJ-459)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-461` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| (TBD — scope phase before any code phases) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-19
**Active Phase:** Planning (scope-definition only — implementation TBD)
**Last Action:** Spun out from PROJ-459 Phase 3 verdict per Codex r4 directive ("F-A-007 should not be smuggled in as a side quest; if it still sits at 750+ LOC after PROJ-449, spin it as its own next-touch project"). PROJ-459's Phase 0 re-measurement and Phase 3 verdict locked in the SPINOUT decision: `game/strategy/data/ship_instance.py` is at **789 LOC** after PROJ-449 wrapper retirement + PROJ-454 component_inspector trim, +289 over the 500 ceiling.
**Next Action:** Scope phase. Audit which of the 5 TD-06 high-value shims (`create`, `to_dict`/`from_dict`, `clone`, `to_ship`/`update_from_ship`, the resource-manager facades) can be retired by migrating callers. The 910-caller sweep is the headline cost; this project plans + executes that sweep.
**Blockers:** None hard. Independent of in-flight Group A / B / C work.

## Overview

Reduce `game/strategy/data/ship_instance.py` from 789 LOC to below the 500-LOC ceiling. The file's overage is concentrated in:

1. The 5 retained TD-06 "high-value shim" entry points (`to_dict`/`from_dict`/`to_json`/`from_json`/`clone`/`to_ship`/`update_from_ship`/etc.) — ~360 LOC of method bodies that exist to support ~910 callers.
2. The class docstring's bullet-list catalog of retained shims (~25 LOC).
3. Read-only @property views (`consumable_levels`, `cargo_contents`) that survived PROJ-449 — ~25 LOC.
4. Inline `design_data` field carry-along and lookup methods.

PROJ-461 attacks (1) and possibly (4). (3) is a deliberate read-only contract from PROJ-449 and is out of scope. (2) shrinks naturally once (1) is retired.

## Goals

- Reduce `ship_instance.py` to <500 LOC.
- Closes **F-A-007** (carried from PROJ-459 — see `findings/PROJ-461_findings.md`).
- Zero behavior change. Save-load and bridge contracts byte-identical.
- Sharded suite green at every phase boundary.

## Scope

**In Scope:**

- `game/strategy/data/ship_instance.py` — primary target.
- Callers of the 5 TD-06 shims that currently use the ShipInstance facade rather than the underlying manager API. Migrate to manager APIs where possible.
- Test fixtures that hard-code the shim usage. Migrate alongside production callers (mechanical sweep).

**Out of Scope:**

- Read-only @property views on `consumable_levels` / `cargo_contents` — deliberately kept by PROJ-449 as the read surface (the substrate-widening seam was closing the setter halves, not the getter halves).
- `_consumable_levels` / `_cargo_contents` private fields — already canonical.
- Bridge layer (`ShipInstanceBridge`) and serializer (`ShipInstanceSerializer`) modules — they are the canonical write paths; the project removes the facades, not the delegates.

## Dependencies & Sibling Projects

| This project depends on | What | Why |
|-------------------------|------|-----|
| PROJ-449 (Strategy entity wrapper retirement) — **LANDED** | Wrapper + setter retirement | Primary driver of the LOC delta; without it, the project would have a different (larger) starting point. |
| PROJ-454 (component_inspector retirement) — **LANDED** | function-local component_inspector imports removed at `ship_instance.py:635/654/663` | Small but real LOC delta; the post-PROJ-454 measurement is the canonical baseline. |

No downstream project depends on PROJ-461.

## Phase Breakdown

**To be defined in a scope phase.** The standard shape per Codex r4:

1. Phase 1: scope audit. Enumerate the 5 TD-06 shims, count callers per shim, identify which callers can move to manager APIs vs. which must keep a facade.
2. Phase 2+: per-shim migration sweep (one shim per phase, or grouped by caller layer).
3. Final phase: delete the shims; close F-A-007.

## Verification

- [ ] Scope phase completed; per-shim caller table built
- [ ] Migration phases executed; callers moved off the shims
- [ ] ship_instance.py LOC < 500
- [ ] Sharded suite green
- [ ] Save-load byte-identical
- [ ] F-A-007 closed
- [ ] User verified

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Related Documents
- [decisions.md](decisions.md) — decisions log
- [findings/PROJ-461_findings.md](findings/PROJ-461_findings.md) — F-A-007 carried verbatim from PROJ-459
- Codex r4 redesign: `AgentCoordination/Scratchpad/Consult/20260519T004841Z_stages-1-2-audit-and-redesign/response.md` (job 11 spinout note)
