# PROJ-472: Facade read-path migration: route game/ui access through strategy facade DTOs (deferred from PROJ-470)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-472` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-472 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Read-path policy + static guard + first migration slice | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-20
**Active Phase:** Planning
**Last Action:** Scope captured from PROJ-470 Protocol-06 revision (dual independent+Codex review). FAC-001/FAC-002/FAC-003 deferred here.
**Next Action:** Plan Phase 1 (policy decision + read-path static guard + densest-site migration slice)
**Blockers:** None — this is incremental migration work, not blocking PROJ-470.

## Overview
The `StrategySessionFacade` enforces the strategy **write path** (commands route through `facade.handle_command()`, guarded by `tests/static_guards/test_facade_bypass_guard.py`), but there is **no equivalent guard for the read path**. ~93 `game/ui/` files import `game.strategy` data/engine types directly for reads (`BuildQueueSource`, `FleetCapabilityCalculator`, `CarriedVehicle`, deployed-group dataclasses, `ContainableKind`, `StrategyScreen.session.<x>` accessors, etc.), making the facade a write-path-only half-facade. This project closes that gap incrementally: decide and document the read-path policy, add a read-path static guard, and migrate the densest bypass sites — without attempting a single-pass migration of all ~93 files.

## Goals
- **Phase 1:** Decide the read-path policy (read DTOs on the facade vs a documented UI-safe read surface enforced by static guard + convention); record it in Pattern #5 of `docs/02_PATTERNS.md`. Add a read-path static guard mirroring the write-path guard. Migrate the densest BuildQueue/fleet bypass sites plus the `StrategyScreen.session` read-path consumers as the first slice. Remaining sites migrate incrementally under the guard.

## Scope
**In:** Pattern #5 (Facade / Delegate) read-path. Layers: ui, strategy. The FAC-001/FAC-002/FAC-003 findings from pattern-audit `2026-05-20_075227_pattern-audit`:
- **FAC-001** — ~93 `game/ui/` files importing strategy data/engine types directly for reads (write-path-only half-facade). Audit-listed read types include: `CarriedVehicle`, `DropPod`, `FighterWing`, `SatelliteConstellation`, `MineGroup`, `BuildQueueSource`, `BuildContext`, `FleetCapabilityCalculator`, `ActivationPhase`, `ComponentActivationState`, `ContainableKind`, `FacilityAbilitySource`, `RaceConfig`, `HabitabilityFactors`, `DesignMetadata`, `DesignRoleRegistry`, `GameConfig`.
- **FAC-002** — densest single-file bypass sites: `game/ui/panels/build_queue_controller.py` (TYPE_CHECKING strategy imports, lines 18-20), `game/ui/screens/build_queue_screen.py:23` (`BuildQueueSource`/`collect_build_queues_at_hex` runtime import), `game/ui/screens/fleet_data_source.py:242` (`FleetCapabilityCalculator` late-import).
- **FAC-003** — `game/ui/screens/strategy_screen.py:242-257` public `session` property; 4 consumers read domain objects directly: `strategy_detail_formatter.py:112` (`.session.registries`), `strategy_detail_formatter.py:395-396` (`.session.turn_engine`), `strategy_windows/list_windows.py:69` (`.session.empires`), `hex_outlines.py:30` (`.session.active_empire.id`).

**Out:**
- The full single-pass migration of all ~93 files (Phase 1 is policy + guard + first slice; the rest is incremental under the guard, decomposed into further phases/projects as needed).
- Write-path facade work (already guarded; not in this project).
- Non-facade pattern conformance (handled in PROJ-470).

## Prior deferral history
This is NOT new architectural decay — it is a deliberately-deferred migration. PROJ-382 (Pattern #10 / #6 naming hygiene) and the U1–U3 work stream previously deferred the read-path migration. PROJ-470's pattern-audit re-surfaced it as a "CRITICAL", but the dual independent+Codex review (2026-05-20) re-classified it as a multi-PR architecture migration with prior deferral history — inappropriate to fold into a contained conformance pass. It is captured here per Protocol 07 (extract phase to project).

## Key Files
| Component | File Path |
|-----------|-----------|
| StrategyScreen.session property (FAC-003) | `game/ui/screens/strategy_screen.py` |
| Build queue controller (FAC-002) | `game/ui/panels/build_queue_controller.py` |
| Build queue screen runtime import (FAC-002) | `game/ui/screens/build_queue_screen.py` |
| Fleet data source late-import (FAC-002) | `game/ui/screens/fleet_data_source.py` |
| .session.registries consumer (FAC-003) | `game/ui/screens/strategy_detail_formatter.py` |
| .session.empires consumer (FAC-003) | `game/ui/screens/strategy_windows/list_windows.py` |
| .session.active_empire consumer (FAC-003) | `game/ui/screens/hex_outlines.py` |
| Existing write-path guard (mirror) | `tests/static_guards/test_facade_bypass_guard.py` |
| New read-path guard | `tests/static_guards/test_facade_read_path_guard.py` |
| Read-path policy doc | `docs/02_PATTERNS.md` (Pattern #5) |

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
