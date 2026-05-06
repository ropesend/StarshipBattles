# PROJ-363: Declarative command/order spec registry

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-363`
> - Open the phase checklist file for your current phase

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Contract tests (TDD baseline) | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Define CommandSpec + spec table | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Generate registry / category sets / ORDER_TO_ABILITY_MAP from specs | Complete | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. Collapse facade dispatch helpers via `__getattr__` | Complete | [phase_4_checklist.md](phase_4_checklist.md) |

## Current State
**Last Updated:** 2026-05-04
**Active Phase:** Awaiting user verification (all four phases complete)
**Last Action:** Phase 4 complete. `CommandDispatchSlice` collapsed from 31 hand-written `dispatch_*` helpers to a single spec-driven `__getattr__` resolver. Full sharded suite green (17,586 / 17,586 passing tests; 4 skipped).
**Next Action:** User verification.
**Blockers:** None

## Phase Outcome Notes
- Phase 1: Contract tests added under `tests/unit/strategy/engine/test_command_registry_contract.py` as **characterization tests** (per user instruction, must PASS on current code) — they pin every command's registered handler, action-time entry, and order serializer round-trip path. They continue to pass after Phases 2-4 land. 30 distinct tests + parametrized variants = 54 cases, all green.
- Phase 2: `game/strategy/engine/commands/` is now a package (was a single `commands.py` module). The DTO module became `commands/__init__.py` (preserving every existing import) and `commands/specs.py` defines the `CommandSpec` dataclass and the `COMMAND_SPECS` tuple of 35 entries. Added `tests/unit/strategy/engine/test_command_specs_contract.py` with 17 distinct + parametrized tests pinning the spec table's self-consistency and parity with existing surfaces.
- Phase 3: `registry_factory.py:create_default_registry()` now loops over `COMMAND_SPECS`. `ORDER_TO_ABILITY_MAP` in `action_time_resolver.py` is computed from `specs.order_to_ability_map()`. The three OrderType frozensets (`MOVEMENT_ORDER_TYPES`, `ACTION_ORDER_TYPES`, `PLANET_ACTION_ORDER_TYPES`) are kept as plain constants in `order_types.py` rather than runtime-derived — runtime derivation creates an unbreakable import cycle (specs.py imports OrderType; OrderType module → specs → handlers → services → cargo_transfer_service → order_types.MOVEMENT_ORDER_TYPES). Their equality with `specs.{movement,action,planet_action}_order_types()` is pinned by the contract test, so the spec table remains the **declarative** source of truth even though the constants are still hardcoded at runtime.
- Phase 4: `CommandDispatchSlice` shrank from ~220 LOC to ~95 LOC. The 31 `dispatch_*_command(...)` helpers collapsed to one `__getattr__` that consults `specs_by_facade_helper()`. Added `test_command_dispatch_slice_getattr.py` with 35 parametrized + 4 named smoke tests.

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
- [x] All phase checklists complete
- [x] `pytest tests/unit/strategy/ tests/integration/strategy/` — all green (4262 passed, 1 skipped)
- [x] Full sharded suite green: `python Tools/test_sharded/test_sharded.py` (17,586 passed, 0 failed, 0 errors, 4 skipped)
- [x] Adding a new command spec entry is the single edit point — pinned by `test_every_command_class_has_a_spec` and `test_spec_table_handler_set_matches_registry` (both fail if a Command DTO ships without a spec entry, and any spec entry without a Command DTO is also flagged)
- [ ] Audit passed
- [ ] User verified
