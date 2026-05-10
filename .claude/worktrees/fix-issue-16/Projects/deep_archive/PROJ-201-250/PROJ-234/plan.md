# PROJ-234: ShipInstance God Object Decomposition

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-234` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-234 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Delete Dead Code & Fix Minor Issues | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Extract ShipInstanceSerializer | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Extract ShipInstanceBridge | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Final Cleanup & Verification | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-03-28
**Active Phase:** Complete
**Last Action:** All 4 phases completed. Full test suite: 13926 passed (22 new), 17 pre-existing failures, 0 regressions.
**Next Action:** None — project complete. Ready for audit.
**Blockers:** None
**Context for Next Agent:** ShipInstance reduced from 756 to 579 lines. Two new files: ship_instance_bridge.py (135L) and ship_instance_serializer.py (136L). 22 new tests added. All facade methods preserve backward compatibility — zero call-site changes.

## Overview

`game/strategy/data/ship_instance.py` is 756 lines with 44 public methods — a god object mixing simulation bridging, serialization, stats, state management, cargo, resources, and display. Three delegates already exist. This project extracts two more classes (ShipInstanceBridge, ShipInstanceSerializer), deletes dead code (`from_ship()`), and fixes magic numbers to bring ShipInstance closer to the 500-line target.

## Goals
- Reduce ShipInstance from 756 to ~540 lines (28% reduction)
- Extract simulation bridge logic to ShipInstanceBridge delegate
- Extract serialization logic to ShipInstanceSerializer utility
- Remove dead `from_ship()` classmethod (zero callers)
- Fix magic numbers (`max_hp=100`, `'06d'` format string)
- Zero breaking changes — all external call sites unchanged

## Scope
**In:**
- ShipInstance method decomposition (bridge + serializer extraction)
- Dead code deletion (`from_ship()`)
- Magic number extraction
- New unit tests for extracted classes
- Protocol docstring updates in `game/core/protocols.py`

**Out:**
- Existing delegate refactoring (cargo/resources/display stay as-is)
- Aligning ShipInstance delegates to Fleet's property pattern (PROJ-210 style)
- Stats/damage cluster extraction (stays on ShipInstance)
- Call-site changes (facade methods preserve backward compatibility)

## Key Files Reference
| Component | File Path | Class/Function |
|-----------|-----------|----------------|
| Primary target | `game/strategy/data/ship_instance.py` | `ShipInstance` |
| New bridge | `game/strategy/data/ship_instance_bridge.py` | `ShipInstanceBridge` |
| New serializer | `game/strategy/data/ship_instance_serializer.py` | `ShipInstanceSerializer` |
| Display formatter | `game/strategy/data/ship_display_formatter.py` | `ShipDisplayFormatter` |
| Protocol docstrings | `game/core/protocols.py` | `IPostBattleShip` |
| Fleet adapter (caller) | `game/strategy/data/fleet_battle_adapter.py` | `FleetBattleAdapter` |
| Test fixtures | `tests/unit/strategy/ship_instance/conftest.py` | `make_ship_with_stats` |

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-28 | Scope: Bridge + Serializer (not stats) | Gets file under 500L target. Stats cluster already delegates to ShipStatsCalculator. |
| 2026-03-28 | Delete from_ship() | Zero callers in entire codebase. Active path uses update_from_ship(). |
| 2026-03-28 | Fix magic numbers during extraction | Natural part of refactor — touching same code anyway. |
| 2026-03-28 | Bridge = eager delegate, Serializer = static utility | Bridge mutates state (needs parent ref). Serializer is stateless (matches FleetOrderSerializer). |
| 2026-03-28 | Keep facade methods | Preserves all 126+ existing tests without changes. |

## Initial Analysis

ShipInstance has 44 public methods grouped into 9 responsibility clusters:
- **State Management** (6 methods) — is_damaged, is_combat_capable, set/is_component_enabled
- **Stats/Damage** (6 methods) — get_calculated_stats, repair, get_hp_percentage, get_damaged_components_by_layer
- **Simulation Bridge** (3 methods) — to_ship, update_from_ship, from_ship (dead)
- **Serialization** (5 methods) — to_dict, from_dict, to_json, from_json, clone
- **Resource Management** (7 methods) — delegated to ShipResourceManager
- **Cargo Management** (5 methods) — delegated to ShipCargoManager
- **Display** (5 methods) — delegated to ShipDisplayFormatter
- **Design/Component** (2 methods) — get_components_by_layer, get_damaged_components_by_layer
- **Identity** (5 properties) — design_name, hull_class, ship_name, serial_number, hash/eq

## Swarm Findings Summary

### Architecture (3 agents)
- ShipInstance already well-delegated: 3 managers for cargo/resources/display
- Established delegate pattern: eager init in `__post_init__`, stored as `field(init=False)`
- Serializer pattern: FleetOrderSerializer uses static methods with late imports
- `from_ship()` at lines 203-245 has zero callers — confirmed dead code

### Test Impact (126+ tests)
- 9 unit test files in `tests/unit/strategy/ship_instance/` (126 tests)
- 6 integration test files in `tests/integration/save_load/`
- All tests call ShipInstance public methods — facades preserve signatures
- FleetBattleAdapter tests MOCK `to_ship()`/`update_from_ship()` — don't test actual behavior
- **Coverage gap:** No integration test for actual to_ship() → Ship with damage applied

### Risks Identified
1. **Save game compatibility (MEDIUM)** — `from_dict()` must call dataclass constructor so `__post_init__` runs. Mitigation: keep logic identical.
2. **All other risks LOW** — No circular imports (TYPE_CHECKING), no threading, no pickle, no `__post_init__` ordering issues.

### Data Flows Validated
- Battle entry: `FleetBattleAdapter → instance.to_ship() → ShipSerializer.from_dict → apply damage/resources`
- Battle exit: `FleetBattleAdapter → s.update_from_ship() → update HP/damage/resources → invalidate cache`
- Save: `GameSession → Empire → Fleet → ShipInstance.to_dict()` (registries NOT serialized)
- Load: reverse, registries injected via `from_dict()` parameter

### Key Patterns to Reuse
- **Delegate init**: `ship_instance.py:81-89` — `field(default=None, repr=False, init=False)` + `__post_init__`
- **Static serializer**: `fleet_order_serializer.py` — static methods with late imports
- **Late import**: `ship_instance.py:216,538` — `from game.simulation.entities.ship_serialization import ShipSerializer`
- **Test fixture**: `conftest.py:25-43` — `make_ship_with_stats(fresh_registries)`

---

## Phases

### Phase 1: Delete Dead Code & Fix Minor Issues [Simple]
**Objective:** Remove dead `from_ship()`, fix magic numbers, update docstrings.
**Status:** Not Started

See [phase_1_checklist.md](phase_1_checklist.md) for detailed tasks.

### Phase 2: Extract ShipInstanceSerializer [Medium]
**Objective:** Move to_dict/from_dict/to_json/from_json/clone to static utility class.
**Status:** Not Started

See [phase_2_checklist.md](phase_2_checklist.md) for detailed tasks.

### Phase 3: Extract ShipInstanceBridge [Medium]
**Objective:** Move to_ship/update_from_ship/_capture_resource_levels to eager delegate.
**Status:** Not Started

See [phase_3_checklist.md](phase_3_checklist.md) for detailed tasks.

### Phase 4: Final Cleanup & Verification [Simple]
**Objective:** Update docstrings, run full test suite, verify baseline.
**Status:** Not Started

See [phase_4_checklist.md](phase_4_checklist.md) for detailed tasks.

---

## Verification Checklist

### Project Start (REQUIRED)
- [x] Read `docs/` foundation docs (01_ARCHITECTURE, 02_PATTERNS, 03_CONVENTIONS)
- [x] Run full test suite: `pytest tests/` — 13904 passed, 17 pre-existing failures (star color mapping + assets)

### After Each Phase
- [ ] Run `pytest tests/unit/strategy/ship_instance/ -x` — all tests pass
- [ ] Run `pytest tests/unit/strategy/ -x` — broader strategy tests pass

### Final Verification
- [ ] `pytest tests/ -n 12` — full suite, same baseline (13904 passed)
- [ ] `pytest tests/integration/save_load/ -v` — save/load round-trips work
- [ ] `pytest tests/unit/strategy/fleet/ -x` — fleet battle adapter still works
- [ ] Verify changes consistent with `docs/` — update docs if needed

---

## Audit Log
| Cycle | Date | Findings | Resolution |
|-------|------|----------|------------|
| 1 | | | |

## Completion Checklist
- [x] All Phase 1 tasks checked off
- [x] All Phase 2 tasks checked off
- [x] All Phase 3 tasks checked off
- [x] All Phase 4 tasks checked off
- [x] All tests passing (13926 passed, 17 pre-existing failures)
- [x] Regression tests passing (zero new failures)
- [ ] Audit passed (no significant issues)
- [ ] User verified

## Related Documents
- [design.md](design.md) - Architecture analysis and design rationale
- [decisions.md](decisions.md) - Full decisions log
- [manifest.md](manifest.md) - File manifest for parallel execution
