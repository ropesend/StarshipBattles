# TD-03: Converge command/order metadata onto a single cycle-safe `OrderMetadataView`

**Status:** VERIFIED
**Priority (from report):** Priority 1, Wave 1 (alongside TD-01 and TD-05)
**Coupling:** Adjacent to TD-07 (ability metadata) and TD-08 (facade surface).

---

## Verification Findings

### File:line evidence

| Surface | Location | What it holds |
|--|--|--|
| Command DTO catalog | `game/strategy/engine/commands/__init__.py:1-587` | 41 `@dataclass` Command DTOs (Issue*, Queue*, Add/Remove/Reorder*, Set*, Clear*, Delete*). |
| Command spec registry | `game/strategy/engine/commands/registry.py:70-316` | `CommandSpec` dataclass + `CommandRegistry` with `register(..., replace=False)`, `unregister`, derivations: `movement_order_types()`, `action_order_types()`, `planet_action_order_types()`, `order_to_ability_map()`, `specs_by_facade_helper()`. Seeded via `seed_default_commands()` / `reset_command_registry()` (`registry.py:374-426`). |
| Hardcoded category frozensets | `game/strategy/data/order_types.py:52-108` | `MOVEMENT_ORDER_TYPES`, `ACTION_ORDER_TYPES`, `PLANET_ACTION_ORDER_TYPES` — plain module-level frozensets. Comment (lines 53-67) explicitly says these are kept hardcoded because runtime derivation would create a cycle. |
| Extra hardcoded frozenset | `game/strategy/data/order_types.py:110-121` | `PLANET_FMS_ACTION_ORDER_TYPES` — a fifth metadata surface NOT mentioned in the report; same fragmentation pattern. |
| Import-time snapshot map | `game/strategy/services/action_time_resolver.py:35-50` | `ORDER_TO_ABILITY_MAP: Dict[OrderType, str] = _build_order_to_ability_map()` — runs `seed_default_commands()` once at module import, then freezes the dict in a module-level constant. `action_time_resolver.py:101` reads `ORDER_TO_ABILITY_MAP.get(order.type)`. |
| Mutator semantics | `game/strategy/engine/commands/registry.py:182-223` | `register(spec, *, replace=True)` is supported (logs WARN) for mod overlays, but no consumer of the duplicated frozensets or `ORDER_TO_ABILITY_MAP` ever re-reads after the snapshot. |

### Cycle analysis

Claimed cycle in `order_types.py:53-67`:

```
order_types.py  -> commands/registry.py  -> seed_default_commands()
                                          -> handlers.{movement, transfer, lay_mines, ...}
                                          -> order_types.py  (handlers import Order, OrderType)
```

That cycle is **real** if `order_types.py` runs the seed eagerly at import time. The remediation must therefore be **lazy** (resolve only when a consumer asks). A separate `OrderMetadataView` module that defers the `seed_default_commands()` call until first read — and a thin proxy in `order_types.py` for back-compat during migration — breaks the cycle cleanly. The frozensets themselves are not imported by any handler module (`Grep` over `game/strategy/engine/handlers/*.py` shows only `Order, OrderType`), so the proxy can read through the view without re-triggering the cycle.

### Consumer inventory

**`MOVEMENT_ORDER_TYPES`** (production):
- `game/strategy/engine/action_execution_engine.py:24,169` (gate)
- `game/strategy/engine/fleet_movement_engine.py:21` (re-exported from `fleet`, used implicitly)
- `game/strategy/data/fleet.py:27` (re-export)
- `game/strategy/services/action_time_resolver.py:24,86`
- `game/strategy/services/fleet_path_projection.py:22,76`
- `game/strategy/services/fleet_navigation_service.py:21`
- `game/strategy/services/cargo_transfer_service.py:12,37`

**`ACTION_ORDER_TYPES`** (production):
- `game/strategy/engine/action_execution_engine.py:25,164`
- `game/strategy/engine/fleet_movement_engine.py:21,275`
- `game/strategy/data/fleet.py:28` (re-export)
- `game/strategy/services/fleet_navigation_service.py:21`

**`PLANET_ACTION_ORDER_TYPES`** (production):
- `game/strategy/engine/planet_action_engine.py:19,131`
- `game/strategy/services/action_time_resolver.py:26,110`

**`PLANET_FMS_ACTION_ORDER_TYPES`** (production):
- `game/strategy/engine/action_execution_engine.py:27`

**`ORDER_TO_ABILITY_MAP`** (production):
- `game/strategy/services/action_time_resolver.py:50,101` (only reader inside the module)

**Test surface (must move together):**
- `tests/unit/strategy/engine/test_command_registry_contract.py:25-36,89-100`
- `tests/unit/strategy/engine/test_command_specs_contract.py:14-28,164-181`
- `tests/unit/strategy/data/test_order_types_characterization.py`
- `tests/unit/strategy/services/test_action_time_resolver.py`
- `tests/unit/strategy/fleet_movement_engine/test_characterization.py`
- `tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py`
- `tests/unit/strategy/test_fleet_order_processor.py`

**Doc surface:**
- `docs/systems/orders_system.md`
- `docs/04_SERVICES.md`
- `docs/systems/satellites.md`

### Verdict

**VERIFIED.** Five distinct truth surfaces (41-DTO catalog, `CommandRegistry`, three hardcoded frozensets in `order_types.py`, `PLANET_FMS_ACTION_ORDER_TYPES` not in the report, and the import-time-frozen `ORDER_TO_ABILITY_MAP`) all encode overlapping order metadata. The contract test `test_command_specs_contract.py` pins equality at *test time* but does nothing about *runtime drift* if `command_registry.register(..., replace=True)` is called after import. The report's payoff approach — one cycle-safe lazy `OrderMetadataView` — is the right shape.

---

## Executor Guardrails

- Do not add magic proxy attributes to `game/strategy/data/order_types.py`. Keep the duplicated constants until every consumer is migrated, then delete them. The end state is explicit imports from `order_metadata_view.py`, not clever module tricks.
- Do not add caching or invalidation in the first implementation. `OrderMetadataView` should be a simple live, lazy reader over `command_registry`. Performance tuning is a later task if profiling proves it necessary.
- Derive `planet_fms_action_order_types()` from explicit `CommandSpec.subcategories={"planet_fms"}` tags on the five FMS handlers. Do **not** derive it from handler filenames or a hardcoded list in the registry.
- `game/strategy/engine/commands/__init__.py` remains the DTO catalog. This remediation is about metadata convergence, not DTO relocation.
- Before each phase, re-run:

```bash
rg -n "MOVEMENT_ORDER_TYPES|ACTION_ORDER_TYPES|PLANET_ACTION_ORDER_TYPES|PLANET_FMS_ACTION_ORDER_TYPES|ORDER_TO_ABILITY_MAP" game tests docs
rg -n "subcategories\s*=|@command_spec\(" game/strategy/engine/handlers game/strategy/engine/commands
```

The first command tells you which remaining consumers still depend on duplicated metadata. The second confirms whether any new command handlers were added while this plan was waiting.

---

## Affected Code

### Production files to edit

- `game/strategy/engine/commands/registry.py`
- `game/strategy/data/order_types.py`
- `game/strategy/data/fleet.py`
- `game/strategy/services/action_time_resolver.py`
- `game/strategy/engine/action_execution_engine.py`
- `game/strategy/engine/fleet_movement_engine.py`
- `game/strategy/engine/planet_action_engine.py`
- `game/strategy/services/fleet_navigation_service.py`
- `game/strategy/services/fleet_path_projection.py`
- `game/strategy/services/cargo_transfer_service.py`

### Handler files that must receive explicit `planet_fms` tags

- `game/strategy/engine/handlers/lay_mines.py`
- `game/strategy/engine/handlers/launch_fighters.py`
- `game/strategy/engine/handlers/launch_satellites.py`
- `game/strategy/engine/handlers/recover_fighters.py`
- `game/strategy/engine/handlers/recover_satellites.py`

### New production file to add

- `game/strategy/engine/commands/order_metadata_view.py`

### Existing tests that must be updated

- `tests/unit/strategy/engine/test_command_specs_contract.py`
- `tests/unit/strategy/engine/test_command_registry_contract.py`
- `tests/unit/strategy/engine/test_command_registry_thirdparty.py`
- `tests/unit/strategy/data/test_order_types_characterization.py`
- `tests/unit/strategy/services/test_action_time_resolver.py`
- `tests/unit/strategy/fleet_movement_engine/test_characterization.py`
- `tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py`
- `tests/unit/strategy/test_fleet_order_processor.py`

### New tests to add

- `tests/unit/strategy/engine/commands/test_order_metadata_view.py`
- `tests/unit/strategy/data/test_order_types_no_duplicated_metadata.py`

### Docs to update after code is green

- `docs/systems/orders_system.md`
- `docs/04_SERVICES.md`
- `docs/systems/satellites.md`

---

## Goal / End State

All production consumers read order metadata through one cycle-safe, lazy view.

### Required architecture outcomes

1. `game/strategy/data/order_types.py` keeps `OrderType`, `Order`, and serialization helpers only. No metadata frozensets remain there.
2. `CommandRegistry` owns all metadata derivations: movement, action, planet-action, planet-FMS, and order-to-ability.
3. `order_metadata_view.py` is the only read facade used by engines and services.
4. `action_time_resolver.py` no longer snapshots `ORDER_TO_ABILITY_MAP` at import time.
5. The five FMS handlers carry an explicit `subcategories={"planet_fms"}` tag.

### `OrderMetadataView` contract

```python
class OrderMetadataView:
    @staticmethod
    def _registry():
        from game.strategy.engine.commands.registry import (
            command_registry,
            seed_default_commands,
        )
        if len(command_registry) == 0:
            seed_default_commands(command_registry)
        return command_registry

    @property
    def movement_order_types(self) -> frozenset[OrderType]: ...

    @property
    def action_order_types(self) -> frozenset[OrderType]: ...

    @property
    def planet_action_order_types(self) -> frozenset[OrderType]: ...

    @property
    def planet_fms_action_order_types(self) -> frozenset[OrderType]: ...

    @property
    def order_to_ability_map(self) -> dict[OrderType, str]: ...
```

### Explicit non-goals

- No caching layer.
- No invalidation API.
- No attempt to eliminate `command_registry.register(..., replace=True)`.
- No module-level compatibility aliases in `order_types.py`.

---

## Remediation Plan

Strict TDD throughout. Do not delete the duplicated constants until all production consumers and tests are off them.

### Phase 0 — Preflight and remaining-consumer inventory

**Purpose:** identify every place still coupled to duplicated metadata.

**Touch list:** none.

**Actions:**

1. Run the two `rg` commands from **Executor Guardrails**.
2. Confirm that `PLANET_FMS_ACTION_ORDER_TYPES` still has exactly one production consumer (`action_execution_engine.py`) and no registry derivation.
3. Record every test file that imports the constants directly. These must be updated before Phase 4.

**Exit criteria:**

- You have a current consumer list.
- You know which handlers need the new `planet_fms` tag.

### Phase 1 — Add explicit `planet_fms` metadata and registry derivation

**Purpose:** close the fifth duplicated surface before introducing the shared view.

**Touch list:**

- Edit `game/strategy/engine/handlers/lay_mines.py`
- Edit `game/strategy/engine/handlers/launch_fighters.py`
- Edit `game/strategy/engine/handlers/launch_satellites.py`
- Edit `game/strategy/engine/handlers/recover_fighters.py`
- Edit `game/strategy/engine/handlers/recover_satellites.py`
- Edit `game/strategy/engine/commands/registry.py`
- Edit `tests/unit/strategy/engine/test_command_specs_contract.py`

**Red tests first:**

- `test_planet_fms_action_order_types_derivation_matches_constant`
- `test_exactly_five_specs_carry_planet_fms_subcategory`

**Implementation rules:**

1. Add `subcategories=frozenset({"planet_fms"})` to the five FMS `@command_spec(...)` declarations.
2. Add `CommandRegistry.planet_fms_action_order_types()`.
3. Derive that method from the `subcategories` tag, not from handler paths or hardcoded order names.

**Validation:**

```bash
pytest tests/unit/strategy/engine/test_command_specs_contract.py -k planet_fms -x
pytest tests/unit/strategy/engine/test_command_registry_contract.py -x
```

**Exit criteria:**

- Registry exposes `planet_fms_action_order_types()`.
- Exactly five command specs carry the `planet_fms` tag.

### Phase 2 — Add `OrderMetadataView`

**Purpose:** create the single live read path without changing consumers yet.

**Touch list:**

- Add `game/strategy/engine/commands/order_metadata_view.py`
- Add `tests/unit/strategy/engine/commands/test_order_metadata_view.py`

**Red tests first:**

- `test_view_movement_matches_registry`
- `test_view_action_matches_registry`
- `test_view_planet_action_matches_registry`
- `test_view_planet_fms_matches_registry`
- `test_view_order_to_ability_matches_registry`
- `test_view_is_lazy_at_import_time`
- `test_view_reflects_replace_overlay`

**Implementation rules:**

1. Import `command_registry` only inside `_registry()`.
2. If the registry is empty, call `seed_default_commands(command_registry)` there.
3. Do not add caching or `invalidate()`.

**Validation:**

```bash
pytest tests/unit/strategy/engine/commands/test_order_metadata_view.py -x
```

**Exit criteria:**

- A live, lazy metadata view exists and is covered by dedicated tests.

### Phase 3 — Migrate the snapshot consumer first: `action_time_resolver.py`

**Purpose:** remove the most dangerous stale-snapshot behavior before broader constant deletion.

**Touch list:**

- Edit `game/strategy/services/action_time_resolver.py`
- Edit `tests/unit/strategy/services/test_action_time_resolver.py`
- Edit `tests/unit/strategy/engine/test_command_specs_contract.py`

**Red tests first:**

- `test_resolve_action_time_reflects_registry_replace`
- update the contract test to assert against `order_metadata.order_to_ability_map`

**Implementation rules:**

1. Delete `_build_order_to_ability_map` and `ORDER_TO_ABILITY_MAP`.
2. Replace `MOVEMENT_ORDER_TYPES` / `PLANET_ACTION_ORDER_TYPES` imports with `order_metadata`.
3. `resolve_action_time(...)` must read `order_metadata.order_to_ability_map` at call time, not import time.

**Validation:**

```bash
pytest tests/unit/strategy/services/test_action_time_resolver.py -x
pytest tests/unit/strategy/engine/test_command_specs_contract.py -k order_to_ability -x
```

**Exit criteria:**

- No import-time order-to-ability snapshot remains.

### Phase 4 — Migrate all remaining production consumers to `order_metadata`

**Purpose:** move production code off duplicated constants before deleting them.

**Touch list:**

- `game/strategy/engine/action_execution_engine.py`
- `game/strategy/engine/fleet_movement_engine.py`
- `game/strategy/engine/planet_action_engine.py`
- `game/strategy/services/fleet_navigation_service.py`
- `game/strategy/services/fleet_path_projection.py`
- `game/strategy/services/cargo_transfer_service.py`
- related characterization/contract tests

**Red tests first:**

- update related tests so they fail unless imports move to `order_metadata`

**Implementation rules:**

1. Replace direct constant imports with `from game.strategy.engine.commands.order_metadata_view import order_metadata`.
2. Update each file to read `order_metadata.<property>` at the point of use.
3. Do not touch `order_types.py` constants yet. Production should be clean first.

**Validation:**

```bash
pytest tests/unit/strategy/fleet_movement_engine/test_characterization.py -x
pytest tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py -x
pytest tests/unit/strategy/engine/test_command_registry_contract.py -x
pytest tests/unit/strategy/ -k "order or action or movement" -x
```

**Exit criteria:**

- No production file under `game/strategy/` still imports the duplicated metadata constants.

### Phase 5 — Delete duplicated constants and `fleet.py` re-exports

**Purpose:** remove the redundant truth surfaces after all consumers are migrated.

**Touch list:**

- Edit `game/strategy/data/order_types.py`
- Edit `game/strategy/data/fleet.py`
- Add `tests/unit/strategy/data/test_order_types_no_duplicated_metadata.py`
- Update any remaining tests still importing the constants

**Red tests first:**

- `test_order_types_module_no_longer_exports_metadata_constants`
- `test_fleet_module_no_longer_re_exports_metadata_constants`

**Implementation rules:**

1. Delete `MOVEMENT_ORDER_TYPES`, `ACTION_ORDER_TYPES`, `PLANET_ACTION_ORDER_TYPES`, and `PLANET_FMS_ACTION_ORDER_TYPES` from `order_types.py`.
2. Delete the `fleet.py` re-exports.
3. Update remaining tests to use `order_metadata`.
4. Do not add compatibility aliases.

**Validation:**

```bash
pytest tests/unit/strategy/data/test_order_types_no_duplicated_metadata.py -x
pytest tests/unit/strategy/data/test_order_types_characterization.py -x
python Tools/test_sharded/test_sharded.py
```

**Exit criteria:**

- The duplicated constants are gone from production code.
- Full sharded suite passes once at this boundary.

### Phase 6 — Docs convergence and final grep gate

**Touch list:**

- `docs/systems/orders_system.md`
- `docs/04_SERVICES.md`
- `docs/systems/satellites.md`

**Implementation rules:**

1. Update docs to reference `order_metadata` as the single read path.
2. Remove instructions that tell contributors to edit `ORDER_TO_ABILITY_MAP` or frozensets manually.
3. Document the `planet_fms` subcategory and the lazy-view cycle break.

**Validation:**

```bash
rg -n "MOVEMENT_ORDER_TYPES|ACTION_ORDER_TYPES|PLANET_ACTION_ORDER_TYPES|PLANET_FMS_ACTION_ORDER_TYPES|ORDER_TO_ABILITY_MAP" game docs tests
pytest tests/unit/strategy/engine/commands/test_order_metadata_view.py tests/unit/strategy/engine/test_command_registry_contract.py tests/unit/strategy/services/test_action_time_resolver.py -x
python Tools/test_sharded/test_sharded.py
```

Expected grep result after this phase:

- production code: only `registry.py` derivation methods and `order_metadata_view.py`
- docs/tests: only current explanatory text or updated assertions; no stale “edit the constant” guidance

---

## Test Strategy

### New focused tests

```text
tests/unit/strategy/engine/commands/test_order_metadata_view.py
tests/unit/strategy/data/test_order_types_no_duplicated_metadata.py
```

### Core regression commands

```bash
pytest tests/unit/strategy/engine/test_command_specs_contract.py -x
pytest tests/unit/strategy/engine/test_command_registry_contract.py -x
pytest tests/unit/strategy/services/test_action_time_resolver.py -x
pytest tests/unit/strategy/data/test_order_types_characterization.py -x
pytest tests/unit/strategy/fleet_movement_engine/test_characterization.py -x
pytest tests/unit/strategy/engine/order_handlers/test_handler_registry_completeness.py -x
pytest tests/unit/strategy/test_fleet_order_processor.py -x
```

### Full gates

- After phase 5: `python Tools/test_sharded/test_sharded.py`
- After phase 6: `python Tools/test_sharded/test_sharded.py`

---

## Risks & Mitigations

| Risk | Likelihood | Required mitigation |
|------|------------|---------------------|
| Reintroducing the import cycle by importing the registry at module load time | High | Keep the import inside `OrderMetadataView._registry()` and pin it with a lazy-import test. |
| A weak executor adds a second hardcoded FMS list in the registry | High | Require `subcategories={"planet_fms"}` on the five command specs and derive from that tag only. |
| Deleting constants before production consumers are migrated | High | Phase 4 finishes production migration first; Phase 5 deletes the constants only after focused tests pass. |
| Replacing the live view with cached module-level snapshots | Medium | Explicit non-goal: no caching and no module-level copies of view output. |
| Missing a direct test import of the old constants | Medium | Use the phase-0 grep and keep `test_order_types_no_duplicated_metadata.py` as the final guard. |

---

## Dependencies / Order

### Verified cross-plan constraints

- **TD-03 should stay before TD-07.** TD-07 can mirror this live-view pattern for ability metadata.
- **TD-03 is independent of TD-01 and TD-02.**
- **TD-03 is independent of TD-08.** The facade already reads live registry state; this plan just narrows the metadata path.

### Impact on `EXECUTION_ORDER.md`

No required change. The current order document already places TD-03 before TD-07 and does not rely on TD-01 or TD-02 for this work.

---

## Estimated Scope (LLM-time)

| Phase | Primary work | Validation cost |
|------|--------------|-----------------|
| 0 | grep baseline only | negligible |
| 1 | tag FMS specs + add derivation | focused unit tests |
| 2 | add `order_metadata_view.py` | focused unit tests |
| 3 | migrate `action_time_resolver.py` | focused unit tests |
| 4 | migrate remaining production consumers | focused unit suite |
| 5 | delete duplicated constants | one sharded run |
| 6 | docs + final grep | one sharded run |

Expected wall-clock remains under one hour, dominated by the two sharded runs after phases 5 and 6.

---

## Completion Criteria

- [ ] `game/strategy/engine/commands/order_metadata_view.py` exists and imports the registry only inside `_registry()`
- [ ] the five FMS handler specs carry `subcategories={"planet_fms"}`
- [ ] `CommandRegistry` exposes `planet_fms_action_order_types()`
- [ ] `game/strategy/services/action_time_resolver.py` has no `ORDER_TO_ABILITY_MAP`
- [ ] `game/strategy/data/order_types.py` exports no metadata frozensets
- [ ] `game/strategy/data/fleet.py` no longer re-exports order-metadata constants
- [ ] production consumers read metadata through `order_metadata`
- [ ] `python Tools/test_sharded/test_sharded.py` passes after phase 5 and again after phase 6
