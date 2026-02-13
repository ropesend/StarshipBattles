# PROJ-93: Update Protocol Layer Type Annotations

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-93` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-93 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Update Protocol Type Annotations | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-02-10
**Active Phase:** Audit Passed — Awaiting User Verification
**Last Action:** Audit Cycle 1 PASSED — all 3 goals verified
**Next Action:** User verification
**Blockers:** None
**Context for Next Agent:** Project complete. Both protocol `layers` return types updated to `Dict['LayerType', 'LayerData']`. Test strengthened. 7616 tests passing.

## Overview
PROJ-84 converted ship layers from raw `Dict[str, Any]` to a typed `LayerData` dataclass. All ~90 access sites across 29 files now use typed attribute access (`layer_data.components`, not `layer_data['components']`). However, two protocol definitions in `game/core/protocols.py` still declare `layers` as `Dict[str, Any]` — the only remaining untyped layer references in the codebase. This project finishes what PROJ-84 started.

## Goals
- Update `IPostBattleShip.layers` return type from `Dict[str, Any]` to `Dict[LayerType, LayerData]`
- Update `IResourceHolder.layers` return type from `Dict[str, Any]` to `Dict[LayerType, LayerData]`
- Strengthen protocol conformance tests to verify typed layer data

## Scope
**In:**
- Type annotation updates in `game/core/protocols.py`
- Import additions (direct for `LayerType`, TYPE_CHECKING for `LayerData`)
- Strengthened assertions in `tests/unit/core/test_protocols_boundary.py`

**Out:**
- Any runtime behavior changes
- Modifying any other protocol properties
- Touching any consumer code (already uses typed access)

## Key Files
| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| Protocols | `game/core/protocols.py` | `IPostBattleShip`, `IResourceHolder` |
| LayerData | `game/simulation/entities/layer_data.py` | `LayerData` dataclass |
| LayerType | `game/core/constants.py` | `LayerType` enum |
| Protocol tests | `tests/unit/core/test_protocols_boundary.py` | `TestIPostBattleShipConformance` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-10 | Import `LayerType` directly, `LayerData` under TYPE_CHECKING | LayerType is in `game.core.constants` (same layer as protocols). LayerData is in `game.simulation.entities` (cross-layer) — must use TYPE_CHECKING guard. No circular deps: simulation never imports protocols.py. |
| 2026-02-10 | Use string forward references `'LayerType'`, `'LayerData'` in annotations | @runtime_checkable protocols execute at import time. String refs prevent runtime import errors when LayerData isn't available outside TYPE_CHECKING block. |
| 2026-02-10 | Keep IResourceHolder (don't delete as dead code) | Created intentionally by PROJ-91 to formalize resource access contract. Has no external consumers yet but is planned infrastructure. |

## Initial Analysis
- **Baseline:** 7615 tests passing, 1 known flaky (`test_different_warp_points_get_different_offsets`)
- **Layer system:** Fully typed via PROJ-84 — `LayerData` dataclass in `game/simulation/entities/layer_data.py`, `Dict[LayerType, LayerData]` in `ship.py:338`
- **Protocols:** `IPostBattleShip` (line 382-428) and `IResourceHolder` (line 437-464) both declare `layers -> Dict[str, Any]`
- **Consumers:** 5 files use `IPostBattleShip` (ship_instance.py, fleet.py, battle_resolver.py, fleet_battle_adapter.py, test_protocols_boundary.py). `IResourceHolder` has zero external consumers.
- **All consumers already access layers as typed objects** — `layer_data.components`, not `layer_data['components']`

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log

---

## Phases

### Phase 1: Update Protocol Type Annotations [Simple]
**Objective:** Update the two protocol `layers` return types and strengthen tests
**Status:** Not Started

See [phase_1_checklist.md](phase_1_checklist.md) for detailed tasks.

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Run full test suite: `pytest tests/` — 7615 passed, 1 known flaky

### After Phase 1
- [x] Run `pytest tests/unit/core/test_protocols_boundary.py` — all pass
- [x] Run `pytest tests/ -n 12` — no regressions

### Final Verification
- [x] Full test suite passes: `pytest tests/ -n 12`
- [x] Audit passed

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | 2026-02-10 | All 3 goals verified: IPostBattleShip.layers, IResourceHolder.layers typed, test strengthened | PASSED |

## Completion Checklist
- [x] Phase 1 tasks checked off
- [x] All tests passing
- [x] Audit passed
- [ ] User verified
