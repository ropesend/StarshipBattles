# PROJ-365: TurnEngine phase descriptor registry

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-365`
> - Open the phase checklist file for your current phase

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Golden phase-list test (TDD baseline) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Define TickPhase + TickContext + DEFAULT_TICK_PHASE_LIST | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Replace `_process_tick` body with descriptor iteration | Complete | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Ready for user verification
**Last Action:** All three phases implemented and committed. `_process_tick` body replaced with descriptor iteration over `DEFAULT_TICK_PHASE_LIST` (15 entries). New module `game/strategy/engine/turn_phase_registry.py` defines `TickPhase`, `TickContext`, and the registry. Two new test modules pin the golden phase ordering, the descriptor shape, and the PROJ-320 `moved_fleet_ids` invariant. Three pre-existing tests updated for the 21-key `_phase_times` dict (added `planet_modifier_effects`).
**Next Action:** User verification — review the diff and confirm.
**Blockers:** None.

## Test Results
- Focused: `pytest tests/unit/strategy/turn_engine/` → 110 passed.
- Strategy integration: `pytest tests/integration/strategy/` → 483 passed, 1 skipped.
- Full sharded: `python Tools/test_sharded/test_sharded.py` → 17325 passed / 0 failed / 4 skipped.

## Overview
`TurnEngine.__init__` (`turn_engine.py:139-217`) wires 18 collaborators. `_process_tick` (`turn_engine.py:703-782`) hardcodes the 14-phase per-tick sequence as imperative `self._time_phase('name', engine.method, args...)` calls. Adding a per-tick system requires constructor growth + property growth + protocol growth + `_process_tick` edits. PROJ-365 makes the phase list a declarative `TickPhase` descriptor list that can be iterated, introspected, and overridden in tests.

End-of-turn engines (organics consumption / happiness / population growth / quality / atmosphere / water at lines 571-602) are explicitly **out of scope**.

## Goals
- Define `TickPhase` (frozen dataclass) and `TickContext` (mutable per-tick context).
- Define `DEFAULT_TICK_PHASE_LIST` matching the current 14 tick-loop phases exactly.
- Replace `_process_tick` body with a single iteration loop over the descriptor list, preserving `_time_phase` timing semantics.
- Convert mid-phase `_log_empire_state` calls (lines 705, 723-724) to `post_exec_hook` on the relevant descriptors with `tick_gating='only_tick_1'`.
- Preserve cross-phase state for the PROJ-320 `moved_fleet_ids` derivation (between phases 3 and 4) via `TickContext`.
- Land a golden-list test that pins phase ordering — protects against accidental reordering.

## Scope
**In:**
- `game/strategy/engine/turn_engine.py` (constructor unchanged; `_process_tick` body replaced)
- New `game/strategy/engine/turn_phase_registry.py`
- New tests under `tests/unit/strategy/turn_engine/`

**Out:**
- End-of-turn engine block (lines 571-602) — keeps imperative form
- TurnEngineConfig (PROJ-259) — orthogonal, untouched
- Constructor decomposition / engine field reduction — separate concern (review finding #3 mentions but is broader; PROJ-365 only touches `_process_tick`)
- Save/load — TurnEngine instance state is ephemeral; no serialization changes

## Key Files
| Component | File Path |
|-----------|-----------|
| TurnEngine | `game/strategy/engine/turn_engine.py` (constructor 139-217, `_process_tick` 703-782, `_time_phase` 243) |
| TurnEngineConfig (untouched) | `game/strategy/engine/turn_engine_config.py` |
| Engine interfaces | `game/strategy/interfaces/engines.py` |
| New phase registry module | `game/strategy/engine/turn_phase_registry.py` (new) |
| Existing phase-ordering test | `tests/unit/strategy/turn_engine/test_turn_processing.py` (lines 69-108) |
| PROJ-320 invariant | `tests/unit/strategy/turn_engine/test_turn_engine_phase_320_movement_diff.py` |
| New golden-list test | `tests/unit/strategy/turn_engine/test_default_tick_phase_list.py` (new) |
| New TickPhase unit test | `tests/unit/strategy/turn_engine/test_tick_phase_descriptors.py` (new) |

## Related Documents
- [design.md](design.md)
- [decisions.md](decisions.md)
- [findings/01_architecture.md](findings/01_architecture.md) - Phase table; cross-phase state design (TickContext); risks
- [findings/02_dependencies.md](findings/02_dependencies.md) - Caller graph; engine interfaces; lazy import; save/load assessment
- [findings/03_test_impact.md](findings/03_test_impact.md) - Phase-order-pinning tests; golden-list test gap

## Verification
- [x] All phase checklists complete
- [x] `pytest tests/unit/strategy/turn_engine/ tests/integration/strategy/` — green
- [x] PROJ-320 `moved_fleet_ids` characterization preserved
- [x] `_time_phase` timing accumulator semantics preserved (now 21 keys — `planet_modifier_effects` added uniformly; see decisions.md)
- [ ] Audit passed
- [ ] User verified
