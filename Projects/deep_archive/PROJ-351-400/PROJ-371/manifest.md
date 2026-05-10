# PROJ-371 File Manifest

> Generated during /proj-start. Used by /proj-parallel for conflict detection.
> Updated if implementation discovers additional files.

## Files modified or created

| File | Type | Phase | Notes |
|------|------|-------|-------|
| `game/strategy/engine/commands/registry.py` | Production (new) | 1 | `CommandSpec` dataclass moved from `specs.py`, `CommandRegistry` class, global `command_registry` singleton, `@command_spec(...)` decorator, `seed_default_commands()`, `reset_command_registry()` test helper, helper-function instance methods (`movement_order_types`, `action_order_types`, `planet_action_order_types`, `order_to_ability_map`, `specs_by_command_name`, `specs_by_facade_helper`, `order_types_for_category`). |
| `game/strategy/engine/commands/specs.py` | Production (modify Phase 1, delete Phase 2) | 1, 2 | Phase 1: keep tuple unchanged for bit-identical redundancy + back-compat imports. Phase 2: **delete** — every consumer reads `command_registry`. |
| `game/strategy/engine/commands/__init__.py` | Production (untouched) | — | DTO definitions; no changes. |
| `game/strategy/engine/handlers/base.py` | Production (untouched) | — | `ICommandHandler` Protocol, `BaseCommandHandler`, `CommandHandlerRegistry` (the runtime dispatch registry — different concept from `CommandRegistry`; no rename to avoid confusion). |
| `game/strategy/engine/handlers/build.py` | Production (modify) | 1 | Add `@command_spec(...)` decorator above `BuildOrderCommandHandler` and `RemoveBuildOrderCommandHandler`. |
| `game/strategy/engine/handlers/construction_queue.py` | Production (modify) | 1 | Add decorator above 4 handlers (Add/Remove/Reorder/SetBuildQueuePaused). |
| `game/strategy/engine/handlers/movement.py` | Production (modify) | 1 | Add decorator above 5 handlers (Move/Warp/Intercept/Join/Colonize). |
| `game/strategy/engine/handlers/order_queue.py` | Production (modify) | 1 | Add decorator above 5 handlers (ClearOrders/ColonizeMission/DeleteOrder/ReorderOrder/SplitFleet). |
| `game/strategy/engine/handlers/transfer.py` | Production (modify) | 1 | Add decorator above `TransferCommandHandler`. |
| `game/strategy/engine/planet_command_handlers.py` | Production (modify) | 1 | Add decorator above 7 handlers (IssuePlanetOrder/ClearPlanetOrders/DeletePlanetOrder/SetAtmosphere/Gravity/Water/RadiationShieldTarget). |
| `game/strategy/engine/superweapon_command_handlers.py` | Production (modify) | 1 | Add decorator above 11 handlers (5 immediate + 5 mission + StellerateStar). |
| `game/strategy/engine/handlers/registry_factory.py` | Production (modify) | 2 | Read from `command_registry.all()` instead of `COMMAND_SPECS`. ~5 LOC. |
| `game/strategy/services/action_time_resolver.py` | Production (modify) | 2 | Read from `command_registry.order_to_ability_map()`. **Delete** local `MOVEMENT_ORDER_TYPES` frozenset at line 48 (redundant + drift-vulnerable; pinned set lives in `data/order_types.py`). |
| `game/strategy/facade/slices/command_dispatch_slice.py` | Production (modify) | 2 | `__getattr__` reads from `command_registry.specs_by_facade_helper()`. ~5 LOC. |
| `game/strategy/facade/strategy_session_facade.py` | Production (modify) | 2 | Collapse 31 hand-written `dispatch_*` forwarders (lines 186-end) into a single `__getattr__` that proxies to `self._command_slice.dispatch_*`. ~150 LOC removed, ~10 LOC added. |
| `game/strategy/data/order_types.py` | Production (untouched) | — | Frozensets stay as leaf-layer constants (import-graph constraint). Pinned by Phase 2-updated contract test. |
| `tests/unit/strategy/engine/test_command_specs_contract.py` | Test (modify) | 2 | Migrate imports from `commands.specs` to `commands.registry`. Test names + assertions unchanged structurally. |
| `tests/unit/strategy/engine/test_command_registry_contract.py` | Test (untouched) | — | Tests the surface (registry factory output, OrderType frozensets, ORDER_TO_ABILITY_MAP), not the spec module. Already passes. |
| `tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py` | Test (modify) | 2 | Update import (`commands.specs` → `commands.registry`). Add `test_facade_dispatch_proxies_to_slice` for the new outer-facade `__getattr__`. |
| `tests/unit/strategy/services/test_superweapon_registry_contract.py` | Test (modify) | 2 | PROJ-364 cross-link reads `command_registry.all()` instead of `COMMAND_SPECS`. |
| `tests/unit/strategy/engine/test_command_registry_seeding.py` | Test (new) | 1 | Bit-identity contract: `COMMAND_SPECS` (tuple) and `command_registry.all()` enumerate the same set of `CommandSpec` rows, field-for-field. Pinned at Phase 1 close; deleted (or migrated) at Phase 2 along with `specs.py`. |
| `tests/unit/strategy/engine/test_command_registry_thirdparty.py` | Test (new) | 3 | End-to-end smoke: register `FakeModCommand` + `FakeModCommandHandler` via decorator, dispatch through facade, assert handler ran, unregister cleanly via test fixture (`tests/fixtures/command_registry.py`). |
| `tests/unit/strategy/engine/test_no_specs_tuple_literal.py` | Test (new) | 3 | AST regression: walk `game/`, parse each `.py` file, assert no module-level `Assign` with a tuple-literal RHS containing `Call(func=Name('CommandSpec'))` elements. Allowed in `tests/`. |
| `tests/fixtures/command_registry.py` | Test fixture (new) | 3 | `register_test_command(spec)` + `unregister_test_command(name)` helpers backed by a context manager that snapshots the registry before the test and restores it after. Used only by `test_command_registry_thirdparty.py`. |
| `docs/systems/strategy_layer.md` | Documentation (modify) | 3 | New "Adding a new command" authoring-rule section with the canonical `@command_spec(...)` decorator pattern. Update `> **Last verified:**` blockquote. |
| `docs/02_PATTERNS.md` | Documentation (modify) | 3 | Cross-reference PROJ-273, PROJ-278, PROJ-371 in the spec-driven registry pattern entry (or add a new "Pattern N: Self-Registering Command Registry"). Update `> **Last verified:**` blockquote. |
