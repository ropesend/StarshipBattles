# PROJ-363: Declarative command/order spec registry

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-363`
> - Open the phase checklist file for your current phase

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Contract tests (TDD baseline) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Define CommandSpec + spec table | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Generate registry / category sets / ORDER_TO_ABILITY_MAP from specs | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Collapse facade dispatch helpers via `__getattr__` | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Planning (awaiting user approval)
**Last Action:** Plan drafted from review finding #4. Renumbered from PROJ-353 to PROJ-363.
**Next Action:** User approval, then begin Phase 1.
**Blockers:** None

## Overview
Adding a strategy command currently requires editing ~7 files (~45 LOC scattered): command DTO, OrderType enum + category sets, registry_factory.py register call, handler module, action_time_resolver map, order_processor dispatch, facade dispatch helper. The runtime registry is fine — the **metadata is scattered**. PROJ-363 introduces a single `CommandSpec` table that drives every other surface.

## Goals
- Define `CommandSpec` dataclass with all metadata needed (command class, order type, handler, category, action ability, execution model, facade-helper name, serializer codec).
- Populate `COMMAND_SPECS` table for the existing 31 commands.
- Generate `CommandHandlerRegistry` contents, frozen category sets (`MOVEMENT_ORDER_TYPES` etc.), and `ORDER_TO_ABILITY_MAP` from `COMMAND_SPECS` at module import time.
- Replace the 31 hand-written `dispatch_*_command` methods on `command_dispatch_slice.py` with a single `__getattr__` that resolves against the spec table.
- Add a contract test that asserts every spec has a registered handler, an action-time entry (where applicable), and a serializer codec round-trip path.

## Scope
**In:**
- `game/strategy/engine/commands/specs.py` (new)
- `game/strategy/engine/handlers/registry_factory.py` (slim down to spec-driven)
- `game/strategy/data/order_types.py` (category frozensets become spec-derived)
- `game/strategy/services/action_time_resolver.py` (ORDER_TO_ABILITY_MAP becomes spec-derived)
- `game/strategy/facade/slices/command_dispatch_slice.py` (collapse 31 helpers via `__getattr__`)
- New contract tests under `tests/unit/strategy/engine/`

**Out:**
- `game/strategy/engine/order_processor.py` dispatch logic (PROJ-364 covers superweapons specifically)
- Save/load OrderSerializer changes (commands aren't serialized, only Orders are)
- UI changes — facade dispatch surface area is preserved (every existing `dispatch_*` method continues to work)

## Key Files
| Component | File Path |
|-----------|-----------|
| Spec module (new) | `game/strategy/engine/commands/specs.py` |
| Registry factory | `game/strategy/engine/handlers/registry_factory.py` |
| OrderType + categories | `game/strategy/data/order_types.py` |
| Action-time resolver | `game/strategy/services/action_time_resolver.py` |
| Facade dispatch slice | `game/strategy/facade/slices/command_dispatch_slice.py` |
| Command DTOs | `game/strategy/engine/commands.py` |
| Handler base + leaves | `game/strategy/engine/handlers/` |
| New contract tests | `tests/unit/strategy/engine/test_command_registry_contract.py` |
| Existing tests | `tests/unit/strategy/test_command_handlers.py`, `tests/unit/strategy/services/test_action_time_resolver.py`, `tests/unit/strategy/data/test_order_serializer.py` |

## Related Documents
- [design.md](design.md)
- [decisions.md](decisions.md)
- [findings/01_architecture.md](findings/01_architecture.md) - 31 commands, 7-file edit footprint, proposed spec shape, import-order analysis
- [findings/02_dependencies.md](findings/02_dependencies.md) - OrderType importers, category-set consumers, no external `register()` calls
- [findings/03_test_impact.md](findings/03_test_impact.md) - Coverage gaps; recommended contract tests

## Verification
- [ ] All phase checklists complete
- [ ] `pytest tests/unit/strategy/ tests/integration/strategy/ --testmon` — all green
- [ ] Adding a new fake command via spec only (not editing 7 files) is demonstrated by a test
- [ ] Audit passed
- [ ] User verified
