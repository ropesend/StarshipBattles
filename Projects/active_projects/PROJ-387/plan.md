# PROJ-387: Legacy removal — Galaxy backward-compat property forwarders (2026-05-07)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-387` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-387 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Migrate 3 readers + delete 5 forwarders | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-08
**Active Phase:** Phase 1 (Complete)
**Last Action:** Migrated 3 production readers (`engine/handlers/movement.py`, `services/fleet_navigation_service.py`, `ui/screens/strategy_render/hex_outlines.py`) + 4 affected test files to `galaxy._state.<field>`; deleted 5 backward-compat forwarders on `Galaxy`. Sharded suite: 19084 passed, 3 failed (matches pre-existing baseline; zero new failures).
**Next Action:** Awaiting user verification
**Blockers:** None

## Overview
Removes 5 backward-compat property forwarders on `Galaxy` (`_global_hex_*`, `_planet_to_system`, `_zone_to_system`) at `game/strategy/data/galaxy.py:97-131`. The docstring at line 93 explicitly marks them "backwards-compat under-prefixed forwarders" and notes "Phase 3-cleanup work will migrate those to public accessors." Three external readers must be migrated first.

## Goals
- Migrate 3 external readers (`movement.py`, `fleet_navigation_service.py`, `hex_outlines.py`) to use public `GalaxyState` accessors directly.
- Delete the 5 underscore-prefixed forwarders on `Galaxy`.

## Scope
**In:** LEG-03-022.
**Out:** Other clusters from the same audit (siblings PROJ-383..PROJ-386, PROJ-388..PROJ-393); REJECTED and OUT_OF_SCOPE items recorded in [findings/verification_report.md](findings/verification_report.md) and the shared [findings/bundling_decisions.md](findings/bundling_decisions.md).

## Key Files
| Component | File Path |
|-----------|-----------|
| Production target | `game/strategy/data/galaxy.py` |
| External reader | `game/strategy/engine/handlers/movement.py` |
| External reader | `game/strategy/services/fleet_navigation_service.py` |
| External reader | `game/ui/screens/strategy_render/hex_outlines.py` |

## Related Documents
- [design.md](design.md) — source audit, cluster identity, severity breakdown
- [decisions.md](decisions.md) — full decisions log
- [findings/verification_report.md](findings/verification_report.md) — third-pass verification of audit claims
- [findings/source_audit.md](findings/source_audit.md) — pointer to the originating audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — interactive bundling record (shared across siblings)

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] No remaining references to `_global_hex_*`, `_planet_to_system`, `_zone_to_system` on `Galaxy` (`grep -rn -E "galaxy\._(global_hex|planet_to_system|zone_to_system)" .`)
- [ ] User verified
