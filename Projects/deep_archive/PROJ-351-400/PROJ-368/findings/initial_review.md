# PROJ-368 Initial Review — Surprising facts

> Architect's notebook from reading every line of `game/strategy/engine/order_processor.py` (910 LOC), the existing handler-pattern reference at `game/strategy/engine/handlers/`, the spec-driven sibling at `game/strategy/engine/superweapon_order_processor.py`, and the four characterization test files at `tests/unit/strategy/engine/test_order_processor_*.py` (1268 LOC total).

## Top 5 surprises

### 1. The `handlers/` directory is already taken — by a different dispatch system

`game/strategy/engine/handlers/` (PROJ-309 sub-phase 3.5) is the **command handler** registry: UI Command DTO → Order creation. Its 7 modules (`base.py`, `build.py`, `construction_queue.py`, `movement.py`, `order_queue.py`, `transfer.py`, `registry_factory.py`) implement `ICommandHandler.execute(session, command) → ValidationResult`. PROJ-368 needs the **order handler** registry: Action tick → State mutation. Both layers are valid registry-based dispatchers but they sit at different points in the pipeline (command → order vs order → state).

Naming the new package `order_handlers/` (chosen) avoids collision; folding into `handlers/` would conflate two dispatchers operating on different inputs. The existing `engine/handlers/transfer.py` is the **command** side (creating a TRANSFER order); the new `order_handlers/transfer.py` is the **execution** side (mutating Planet/Fleet state when the tick fires the order). The two transfer files would parallel each other.

### 2. `process_join_fleet` (single-fleet variant) appears to be dead production code

`OrderProcessor.process_join_fleet` is a 40-LOC public method (lines 110-149) called from… nowhere in `game/`. Grep returns hits in:
- `game/strategy/interfaces/engines.py` — the `IOrderProcessor` ABC docstring (`process_join_fleet() - handle JOIN_FLEET orders` at line 69)
- `game/strategy/engine/order_processor.py` — the docstring + the implementation
- Nothing else under `game/`

The sole caller is `tests/unit/strategy/engine/test_order_processor_fleet_merge.py` (88 LOC, the entire file is dedicated to driving `process_join_fleet`). The actual production JOIN_FLEET path is `process_instant_orders` (the BUG-122 batch path). This is captured as Open Question Q3 — user resolves whether to delete or preserve.

### 3. SELF_DESTRUCT is the only superweapon NOT routed through the spec-driven dispatcher

PROJ-364 stabilized `SuperweaponOrderProcessor.execute_superweapon` (lines 137-319) — a 7-step dispatcher that handles every spec-driven superweapon: target shape resolution, stabilizer check, ability-ship lookup, effect, finalize. Five of the six superweapon `OrderType` values flow through it (`process_implode_planet`, `process_stellerate_star`, `process_open_warp_point`, `process_close_warp_point`, `process_create_dyson_sphere`).

The sixth, `process_self_destruct` (lines 664-740), is a 76-LOC standalone method that does NOT use `execute_superweapon`. It bypasses spec lookup entirely. The `SUPERWEAPON_SPECS` table at `game/strategy/services/superweapon_registry.py` does not contain a `SELF_DESTRUCT` entry. Yet the inline 6-lambda dict at `order_processor.py:706-725` treats SELF_DESTRUCT identically to the other 5 — same call shape, same return-type pattern.

PROJ-368's plan lifts `process_self_destruct` to its own `SelfDestructHandler` to surface the asymmetry rather than wrap it (Q2). Without this lift, the registry would have 5 `SuperweaponHandlerAdapter` entries plus an asymmetric 6th adapter that special-cases SELF_DESTRUCT. Lifting puts the 6th on equal footing with the other peer handlers.

### 4. `process_transfer` has 7 implicit branches, not 5

The review counted "5 branching paths" but careful reading reveals 7:

| # | Path | Method called | Sub-path |
|---|---|---|---|
| 1 | Planet target, `direction='load'`, `cargo_type='drop_pod'` | `_execute_load → _load_pod_from_staging_yard` | drop pod |
| 2 | Planet target, `direction='load'`, `cargo_type='passengers'` | `_execute_load` | passengers |
| 3 | Planet target, `direction='load'`, resource cargo | `_execute_load` | resource |
| 4 | Planet target, `direction='unload'`, `cargo_type='drop_pod'` | `_execute_unload → _unload_pod_to_staging_yard` | drop pod |
| 5 | Planet target, `direction='unload'`, `cargo_type='passengers'` | `_execute_unload` | passengers |
| 6 | Planet target, `direction='unload'`, resource cargo | `_execute_unload` | resource |
| 7 | Fleet target | `_execute_fleet_transfer` | (cargo type irrelevant — generic) |

Plus the BUG-70 LOAD_POPULATION pre-dispatch branch (auto-resolves a colony at fleet hex when no `planet_id` and no `target_fleet_id`), and the `target_fleet_id` resolution that searches `getattr(galaxy, 'empires', [])` then falls back to `empire.fleets` (PROJ-343 T1.1 fixed the related call-site, but the resolver brittleness persists).

PROJ-368 phase 3 makes all 7 dispatch branches explicit as `_dispatch_*` methods on `TransferHandler`. The architect counted while drafting and surfaces the corrected count in design.md § Phase 3.

### 5. `OrderProcessor` is stateless — no mutable instance attributes between calls

Reading `__init__` (lines 75-84) shows only two attributes set: `self._event_bus` and `self._superweapon_processor`. Both are constructed-once. There is no per-tick state, no progress trackers, no caches. The `process_*` methods receive everything they need as arguments (fleet, empire, galaxy) and mutate those arguments in place.

This matters for two PROJ-368 design questions:
1. **Replay determinism (R5):** decomposing a stateless class is safe — there's no state to checkpoint or migrate. PROJ-368 introduces a registry as a new instance attribute (`self._handler_registry`), but the registry is constructed once in `__init__` and is itself stateless w.r.t. game data.
2. **Handler instances:** each handler can be a singleton constructed at registry-build time. No need for per-tick handler instantiation. `TransferHandler(event_bus=...)` constructed once; called many times.

The implication is that the entire decomposition is **lateral structure change** — no semantics change, no state migration, no save format change. The pure architectural nature is exactly why PROJ-333's characterization tests can serve as the sole regression guard for all 5 phases.
