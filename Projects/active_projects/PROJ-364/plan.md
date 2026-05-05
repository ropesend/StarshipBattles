# PROJ-364: Superweapon spec table refactor

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-364`
> - Open the phase checklist file for your current phase

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Order-pop / event-payload characterization | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Define SuperweaponSpec + SUPERWEAPONS table | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Spec-driven dispatch + per-weapon effect closures | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Phase 2 (in progress)
**Last Action:** Phase 1 landed (21 characterization tests; 148 superweapon tests + 17617 sharded all green).
**Next Action:** Phase 2 — define SuperweaponSpec + SUPERWEAPONS table.
**Blockers:** None (PROJ-363 landed at 579a097ec).

## Overview
`game/strategy/engine/superweapon_order_processor.py` has 5 strategic-superweapon `process_*` methods (IMPLODE_PLANET, STELLERATE_STAR, OPEN_WARP_POINT, CLOSE_WARP_POINT, CREATE_DYSON_SPHERE) — each ~50 LOC repeating: get current order → check type → resolve target → check stabilizer → find ship by hardcoded ability name → mutate galaxy → call shared `_finalize_superweapon` tail. The shared tail exists; the prologue is copy-pasted. SELF_DESTRUCT is structurally different (no ability check, no stabilizer block) and stays out of the spec.

The existing `stabilizer_registry.py:36-70` is the reference pattern — frozen dataclass + tuple registry + lookup function. PROJ-364 mirrors it.

## Goals
- Define `SuperweaponSpec` (frozen dataclass): order_type, ability_name, target_type, consume_ship, event_type, stabilizer_blocks.
- Populate `SUPERWEAPONS` tuple for the 5 strategic superweapons.
- Replace each `process_*` method's prologue with a single `execute_superweapon(spec, ...)` shared dispatcher; per-weapon effect logic becomes a small effect closure.
- Keep `_finalize_superweapon` (already shared).
- Preserve all current behavior (per-weapon characterization tests in Phase 1 lock it down).
- SELF_DESTRUCT stays in its current ad-hoc form (out of spec).

## Scope
**In:**
- `game/strategy/engine/superweapon_order_processor.py`
- New `game/strategy/services/superweapon_registry.py`
- `game/strategy/engine/order_processor.py:706-725` superweapon dispatch table (replace the lambda dict with a spec lookup)
- New tests under `tests/unit/strategy/services/` and `tests/unit/strategy/engine/`

**Out:**
- SELF_DESTRUCT (no ability requirement, no stabilizer block — structural outlier; existing code at `order_processor.py:722-724` retained as-is)
- Component definitions (component data already carries the superweapon-ability bindings)
- UI / replay capture changes

## Key Files
| Component | File Path |
|-----------|-----------|
| Order processor (superweapon section) | `game/strategy/engine/superweapon_order_processor.py` |
| New registry | `game/strategy/services/superweapon_registry.py` (new) |
| Reference pattern | `game/strategy/services/stabilizer_registry.py:36-70` |
| Order processor dispatch | `game/strategy/engine/order_processor.py:704-730` |
| OrderType enum | `game/strategy/data/order_types.py` |
| EventType enum | (find via grep — likely `game/strategy/events/`) |
| Existing tests | `tests/unit/strategy/engine/test_superweapon_order_processor.py`, `test_superweapon_edge_cases.py`, `test_superweapon_order_processor_gaps.py`, `tests/integration/strategy/test_superweapon_integration.py` |
| New characterization tests | `tests/unit/strategy/engine/test_superweapon_order_pop_matrix.py` (new), `tests/unit/strategy/engine/test_superweapon_event_payloads.py` (new) |
| New registry test | `tests/unit/strategy/services/test_superweapon_registry_contract.py` (new) |

## Related Documents
- [design.md](design.md)
- [decisions.md](decisions.md)
- [findings/01_architecture.md](findings/01_architecture.md) - Per-superweapon table; common prologue/tail; spec shape
- [findings/02_dependencies.md](findings/02_dependencies.md) - Caller graph; ability-name → component bindings; stabilizer registry
- [findings/03_test_impact.md](findings/03_test_impact.md) - Current coverage matrix; gaps in order-pop semantics + event payloads

## Verification
- [ ] All phase checklists complete
- [ ] `pytest tests/unit/strategy/engine/test_superweapon* tests/integration/strategy/test_superweapon_integration.py tests/unit/strategy/services/test_superweapon_registry_contract.py -v` — green
- [ ] `pytest tests/unit/strategy/ tests/integration/strategy/ --testmon` — no regressions
- [ ] Audit passed
- [ ] User verified
