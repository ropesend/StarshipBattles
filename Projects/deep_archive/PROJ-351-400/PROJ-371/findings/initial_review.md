# PROJ-371 — Initial Review

> **Read-only finding pack.** Source-of-truth for the design.md inventory and the
> "8 edits per command" mapping. Pin file:line references; do not edit.

## Top 3 surprises (read these first)

1. **PROJ-363 already did most of the consolidation.** The "8 edits across 3-5
   files" claim from the strategy-layer review (`AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md:84`)
   pre-dates PROJ-363's landing. As of `commands/specs.py:537` (last `CommandSpec`
   row) the **only** mandatory production-side edit per new command today is one
   spec row in `specs.py` plus a new handler module. Six surfaces that *would*
   have been hand-edited are all derived (registry, action-time map, three
   OrderType frozensets — pinned by contract test — facade `__getattr__`).
   The remediation is therefore **not** "consolidate the scattered table"; it is
   "convert the consolidated tuple into a self-registering registry so commands
   own their own metadata."
2. **The facade still has 31 hand-written one-line `dispatch_*` forwarders.**
   `game/strategy/facade/strategy_session_facade.py:186-?` (37+ duplicates of
   `return self._command_slice.dispatch_<x>(**kwargs)`). The slice already uses
   `__getattr__` (`game/strategy/facade/slices/command_dispatch_slice.py:72`);
   the outer facade was missed by PROJ-363 Phase 4. Collapsing this is the
   easiest concrete win.
3. **`MOVEMENT_ORDER_TYPES` exists in three files** (PROJ-363 review FIND #4):
   - `game/strategy/data/order_types.py:58-62` — module-level frozenset
   - `game/strategy/engine/commands/specs.py::movement_order_types()` — derived
   - `game/strategy/services/action_time_resolver.py:48` — local frozenset
   Today the contract test at `tests/unit/strategy/engine/test_command_specs_contract.py:135-137`
   pins (1) == (2). (3) is unpinned and silently drifted (it lacks `WARP`).

## Spec inventory

**Total CommandSpec rows: 35** at `game/strategy/engine/commands/specs.py:219-537`.
Breakdown by `category`:

| Category          | Count | Specs (Command DTO names)                                                                                                                  |
|-------------------|-------|--------------------------------------------------------------------------------------------------------------------------------------------|
| `movement`        | 5     | IssueMove, IssueWarp, IssueIntercept, IssueJoinFleet, IssueColonize (NB: IssueColonize is `category='action'`; corrected below)            |
| `action`          | 3     | IssueColonize, IssueTransfer, QueueColonizeMission                                                                                          |
| `superweapon`     | 11    | IssueImplodePlanet, IssueStellerateStar, IssueOpenWarpPoint, IssueCloseWarpPoint, IssueCreateDysonSphere, IssueSelfDestruct + 5 mission variants |
| `fleet_management`| 4     | ClearOrders, SplitFleet, DeleteOrder, ReorderOrder                                                                                         |
| `build`           | 2     | IssueBuildOrder, RemoveBuildOrder                                                                                                          |
| `construction`    | 4     | AddToConstructionQueue, RemoveFromConstructionQueue, ReorderConstructionQueue, SetBuildQueuePaused                                         |
| `planet`          | 7     | IssuePlanetOrder, ClearPlanetOrders, DeletePlanetOrder, SetAtmosphere/Gravity/Water/RadiationShieldTarget                                  |
| **Total**         | **35**|                                                                                                                                            |

Movement has 4 specs (corrected count): IssueMove, IssueWarp, IssueIntercept,
IssueJoinFleet. IssueColonize is category=`action`, not `movement`
(`specs.py:257-266`).

By `execution_model`:
- `action`: 7 specs (Move, Warp, Intercept, Colonize, Transfer + 6 immediate
  superweapons except SelfDestruct which is `action`)
- `mission`: 6 specs (Colonize + 5 superweapon variants — `order_type=None`)
- `instant`: 17 specs
- `production`: 1 spec (IssueBuildOrder)
- `planet`: 1 spec (IssuePlanetOrder)

By `order_type=None` (commands with no concrete OrderType, dispatched directly
by handler): **22 specs** (all missions, all queue-management commands, all
planet ability-toggle controllers, all set-target commands, RemoveBuildOrder).
By `facade_helper_name=None`: **4 specs** — SetGravityTarget, SetWaterTarget,
SetRadiationShieldTarget, SetBuildQueuePaused (`specs.py:476, 519, 527, 535`).

## "8 edits across 3-5 files" — concrete mapping

The review report (`AgentCoordination/Scratchpad/reviews/strategy_layer_tech_debt_2026-05-05.md:84`) lists
"DTO, handler, spec row, order-type, action-time, facade-helper, codec, tests"
as 8 edits. **As-of PROJ-363 (the spec table landed)**, this is the actual
edit list to add a 36th command:

| # | Edit | File | Line region | Status                                                                                |
|---|------|------|-------------|---------------------------------------------------------------------------------------|
| 1 | DTO `@dataclass class FooCommand(Command)` | `game/strategy/engine/commands/__init__.py` | append, ~10-15 LOC | **Required** |
| 2 | Handler class implementing `ICommandHandler` | `game/strategy/engine/handlers/<domain>.py` (new or existing) | ~30-80 LOC | **Required** |
| 3 | `CommandSpec(...)` row | `game/strategy/engine/commands/specs.py:219-537` | ~10 LOC | **Required** — the consolidation point |
| 4 | OrderType enum entry (only if the command emits a NEW OrderType) | `game/strategy/data/order_types.py:18-37` | 1 LOC | **Required for new OrderType only** |
| 5 | OrderType frozenset entry (`MOVEMENT_/ACTION_/PLANET_ACTION_ORDER_TYPES`) | `game/strategy/data/order_types.py:58-86` | 1 LOC | **Required for new OrderType only**; pinned to specs by `test_command_specs_contract.py:135,140,145` |
| 6 | Action-time map | `game/strategy/services/action_time_resolver.py:40` | 0 LOC — derived | **Eliminated by PROJ-363 Phase 3** (`order_to_ability_map()`) |
| 7 | Facade helper | `game/strategy/facade/slices/command_dispatch_slice.py:72-100` | 0 LOC — `__getattr__` | **Eliminated by PROJ-363 Phase 4** (slice level) |
| 7b| Facade helper forwarder | `game/strategy/facade/strategy_session_facade.py:186-300` | ~3 LOC | **STILL REQUIRED** — facade-level `dispatch_*` was not collapsed |
| 8 | Test coverage | `tests/unit/strategy/...` | ~50-200 LOC | **Required** |

**Net edits in 2026-05-05 reality:** 4 required production edits (DTO, handler,
spec row, facade forwarder) + 1 conditional (new OrderType + frozenset entry,
pinned). The facade forwarder is the **only remaining structural duplication**.

After PROJ-371: **1 file edit** (new handler module that self-registers via
decorator). Spec row, facade forwarder, and OrderType enum entry are all
either auto-derived or live next to the handler.

## Consumer surfaces of `COMMAND_SPECS` (production)

| File                                                                  | Consumes                                            | Lines        |
|-----------------------------------------------------------------------|-----------------------------------------------------|--------------|
| `game/strategy/engine/handlers/registry_factory.py`                   | `COMMAND_SPECS` → instantiate handlers              | 32, 35       |
| `game/strategy/services/action_time_resolver.py`                      | `order_to_ability_map()` → `ORDER_TO_ABILITY_MAP`   | 36, 40       |
| `game/strategy/facade/slices/command_dispatch_slice.py`               | `specs_by_facade_helper()` → `__getattr__` resolver | 80, 82       |
| `game/strategy/data/order_types.py`                                   | (Pin-only — frozensets pinned by contract test)     | 40-55, 58-86 |
| `game/strategy/facade/strategy_session_facade.py`                     | (Indirect via slice; 31 hand-written forwarders)    | 186-end      |

**Three direct production consumers**, plus one pin-only test contract
(`order_types.py`). Total migration surface: 3 files.

## Consumer surfaces of `COMMAND_SPECS` (tests)

| File                                                                       | Imports                                                  |
|----------------------------------------------------------------------------|----------------------------------------------------------|
| `tests/unit/strategy/engine/test_command_specs_contract.py`                | Full table inspection; 14 distinct + 2 parametrized tests |
| `tests/unit/strategy/engine/test_command_registry_contract.py`             | Indirect via `create_default_registry()` and `ORDER_TO_ABILITY_MAP` |
| `tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py`        | `COMMAND_SPECS` for parametrize ids                      |
| `tests/unit/strategy/services/test_superweapon_registry_contract.py`       | `COMMAND_SPECS` for cross-link assertions (PROJ-364)     |

## Pattern source

**PROJ-273** (Ability-Stat Registry, archived `Projects/deep_archive/PROJ-251-300/PROJ-273/`):
- Module + frozen-dataclass DTO + dict registry at module scope
- Glob-driven coverage test that auto-discovers new content (`tests/unit/simulation/combat/test_ability_stat_registry.py`)
- Once-per-source WARN logging on unknown keys (`FleetAuraManager._log_unknown_stat_key_once`)
- 6 phases: registry-module → migrate-consumer-A → migrate-consumer-B → glob-coverage → runtime-warn → docs

**PROJ-278** (Role Registry, archived `Projects/deep_archive/PROJ-251-300/PROJ-278/`):
- Generic `RoleRegistry` class shared by two registry instances
- `RegistrationConflictPolicy` enum + `RegistrationHandle` dataclass
- `allow_runtime_add` flag distinguishing the two instances
- Invalidation callbacks with re-entrance guard
- AST static-guard test forbidding the old (substring-parsing) idiom
- 6 phases: registry-module → instance-1 → instance-2 → ShipSpec field → callbacks → docs

**What transfers:**
- Frozen-dataclass spec shape (already done by PROJ-363).
- Decorator + global registry instance (PROJ-273 used a dict; PROJ-371 wants a class).
- Glob-driven / AST-static contract test forbidding tuple reintroduction.
- Once-per-source WARN log on unknown command names from save/wire data
  (defensive for save-drift, although today commands aren't persisted).

**What's command-specific:**
- Dispatch ordering matters less than for stat contributors (commands fan out
  one-to-one), so `phase_order` is unnecessary.
- `RegistrationConflictPolicy` is unnecessary at first — commands are unique by
  DTO class. Mods that want to *replace* a built-in command can do it via the
  decorator's optional `replace=True` flag.
- Commands ARE NOT persisted in save files (verified — `Order` objects are
  persisted, not `Command` objects; `game/strategy/data/order_types.py:108-181`).
  This removes the determinism / non-reuse concern entirely.

## Decision points raised by the inventory

1. **Decorator vs explicit register call?** PROJ-273 used a module-level dict
   literal; PROJ-278 used `register_invalidation_callback` after construction.
   For PROJ-371, decorator (`@command_spec(...)`) is the natural fit — colocates
   metadata with the handler.
2. **Registry singleton vs registry-on-context?** PROJ-273 used a module-level
   dict; PROJ-278 has two instances, threaded via `ApplicationContext`. For
   PROJ-371, ONE module-level instance is correct (commands are global).
3. **Where does the handler live?** Today: handler in `engine/handlers/<domain>.py`
   imported by `specs.py`. Target: handler in same module, decorated, and
   `specs.py` becomes "import every handler module to trigger registration."
4. **Naming.** `CommandRegistry`, `command_registry`, `register_command(spec)` —
   parallels `STAT_CONTRIBUTOR_REGISTRY` from PROJ-360 / PROJ-367.
5. **AST regression.** Forbid reintroduction of the literal tuple
   `COMMAND_SPECS: tuple[CommandSpec, ...] = (...)` — the registry must own the
   data.

## Consumer migration size estimate

- `registry_factory.py`: ~10 LOC change (loop over registry vs tuple).
- `action_time_resolver.py`: ~5 LOC change (pull from registry).
- `command_dispatch_slice.py::__getattr__`: ~5 LOC change.
- `strategy_session_facade.py`: collapse 31 dispatchers → `__getattr__` (~150 LOC removed).
- Total: ~150 LOC removed, ~30 LOC added in registry module.

## Test-baseline assumptions to verify pre-Phase-1

- Sharded suite green at HEAD before any work begins; pin pass count.
- `tests/unit/strategy/engine/test_command_specs_contract.py` passes today.
- `tests/unit/strategy/engine/test_command_registry_contract.py` passes today.
- `tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py` passes
  today.
- The "every Command DTO has a CommandSpec" guard test at
  `test_command_specs_contract.py:51` is the prior-art template for the new
  "every Command DTO uses the registry" guard.
