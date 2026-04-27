# Decomposition Design: command_handlers.py

**Current size:** 1076 lines (verified via `wc -l` on 2026-04-27, post-PROJ-298)
**Target post-split:** every resulting module <500 lines

> **Naming note (post-PROJ-298 verification):** The file uses the renamed `Order`/`OrderType` symbols throughout (imported from `game.strategy.data.order_types`). All `Order(OrderType.MOVE, target=...)` / `Order(OrderType.COLONIZE, ...)` / etc. constructors confirmed against the file at HEAD. There are no stale `FleetOrder*` references remaining in this module.

---

## Current responsibilities

The module currently mixes **infrastructure** (the registry + protocol + base mixin + free helper) with **17 concrete handler classes** spanning four cohesive domains plus a dispatcher factory that pulls in handlers from two other modules (`superweapon_command_handlers`, `planet_command_handlers`).

### Infrastructure (lines 1–314)
| Symbol | Lines | Role |
|---|---|---|
| `add_move_order_if_needed` (free fn) | 42–91 | Shared helper for chain-aware MOVE auto-queue |
| `ICommandHandler` (Protocol) | 95–109 | Public typing protocol |
| `BaseCommandHandler` | 112–281 | Mixin: `_resolve_fleet`, `_resolve_fleet_required`, `_resolve_planet`, `_resolve_planet_optional`, `_resolve_build_entity`, `_resolve_queue`, `_build_colonize_target` |
| `CommandHandlerRegistry` | 284–313 | Dispatch table |

### Domain 1: Fleet movement & navigation (lines 316–453, 623–663)
| Handler | Command | Lines |
|---|---|---|
| `ColonizeCommandHandler` | `IssueColonizeCommand` | 316–351 |
| `MoveCommandHandler` | `IssueMoveCommand` | 354–381 |
| `InterceptCommandHandler` | `IssueInterceptCommand` | 388–415 |
| `JoinCommandHandler` | `IssueJoinFleetCommand` | 418–453 |
| `WarpCommandHandler` | `IssueWarpCommand` | 623–663 |

### Domain 2: Order-queue management (lines 456–510, 670–793)
| Handler | Command | Lines |
|---|---|---|
| `ColonizeMissionCommandHandler` | `QueueColonizeMissionCommand` | 456–493 |
| `ClearOrdersCommandHandler` | `ClearOrdersCommand` | 496–510 |
| `SplitFleetCommandHandler` | `SplitFleetCommand` | 670–731 |
| `DeleteOrderCommandHandler` | `DeleteOrderCommand` | 734–755 |
| `ReorderOrderCommandHandler` | `ReorderOrderCommand` | 758–793 |

### Domain 3: Cargo transfer (lines 513–578)
| Handler | Command | Lines |
|---|---|---|
| `TransferCommandHandler` | `IssueTransferCommand` | 513–578 |

### Domain 4: Build orders & construction queue (lines 581–620, 800–993)
| Handler | Command | Lines |
|---|---|---|
| `BuildOrderCommandHandler` | `IssueBuildOrderCommand` | 581–603 |
| `RemoveBuildOrderCommandHandler` | `RemoveBuildOrderCommand` | 606–620 |
| `AddToConstructionQueueCommandHandler` | `AddToConstructionQueueCommand` | 800–924 (largest single handler — 124 lines incl. two private helpers `_check_design_valid` and `_load_design_cost`) |
| `RemoveFromConstructionQueueCommandHandler` | `RemoveFromConstructionQueueCommand` | 926–957 |
| `ReorderConstructionQueueCommandHandler` | `ReorderConstructionQueueCommand` | 960–993 |

### Factory (lines 996–1076)
- `create_default_registry()` — wires up all 25 commands (17 from this file + 11 superweapon + 7 planet-order). Imports from `superweapon_command_handlers` and `planet_command_handlers` are deferred (function-scope) to keep import-time light.

---

## Proposed sub-modules

Create a new package `game/strategy/engine/handlers/`. Group handlers by **domain cohesion**, not one-file-per-handler (that would yield 17 tiny files and make the registry factory hard to read).

| Path | Responsibility | Handler classes | Est. LOC |
|---|---|---|---|
| `game/strategy/engine/handlers/__init__.py` | Package facade — re-exports every handler symbol so callers can keep `from game.strategy.engine.handlers import XCommandHandler` | (re-exports only) | ~40 |
| `game/strategy/engine/handlers/base.py` | Infrastructure: `ICommandHandler` Protocol, `BaseCommandHandler` mixin, `add_move_order_if_needed` helper, `CommandHandlerRegistry` | (no handlers) | ~210 |
| `game/strategy/engine/handlers/movement.py` | Fleet navigation handlers — pathfinding-related commands | `ColonizeCommandHandler`, `MoveCommandHandler`, `InterceptCommandHandler`, `JoinCommandHandler`, `WarpCommandHandler` | ~230 |
| `game/strategy/engine/handlers/order_queue.py` | Order-list manipulation — queueing, clearing, splitting fleets, reorder/delete | `ColonizeMissionCommandHandler`, `ClearOrdersCommandHandler`, `SplitFleetCommandHandler`, `DeleteOrderCommandHandler`, `ReorderOrderCommandHandler` | ~210 |
| `game/strategy/engine/handlers/transfer.py` | Cargo/population transfers (single handler, large enough to deserve its own module given logging volume + `FleetCargoProjector` dependency) | `TransferCommandHandler` | ~95 |
| `game/strategy/engine/handlers/build.py` | Fleet BUILD-order toggling (in-fleet construction) | `BuildOrderCommandHandler`, `RemoveBuildOrderCommandHandler` | ~60 |
| `game/strategy/engine/handlers/construction_queue.py` | Planet/facility/fleet construction-queue CRUD (the largest handler in the file lives here) | `AddToConstructionQueueCommandHandler`, `RemoveFromConstructionQueueCommandHandler`, `ReorderConstructionQueueCommandHandler` | ~225 |
| `game/strategy/engine/handlers/registry_factory.py` | `create_default_registry()` — composes all handlers from this package + `superweapon_command_handlers` + `planet_command_handlers` | (factory only) | ~95 |
| `game/strategy/engine/command_handlers.py` (kept as Option-A shim) | Re-exports every public symbol from `handlers/*` so existing imports keep working | (no logic) | ~50 |

### Why this grouping (vs. one-file-per-handler)

1. **Cohesion over fragmentation.** Movement handlers all share pathfinding concerns and `add_move_order_if_needed`. Construction-queue handlers all share `_resolve_build_entity` + `_resolve_queue`. Splitting them apart would scatter related code across 17 trivially small files.
2. **Each proposed file is ≤ ~230 LOC** — well under the 500-LOC target.
3. **Domain boundaries already exist in the source** — the current file uses banner comments (`# Fleet Management Command Handlers`, `# Construction Queue Command Handlers`) that confirm these natural groupings.
4. **The factory needs a home.** `registry_factory.py` is small but separating it prevents `create_default_registry()` from drifting back into the same file as the handlers (which would re-grow the file as new commands are added).

---

## Public API surface

Confirmed via grep `from game.strategy.engine.command_handlers import`. Symbols actually imported by callers today:

| Symbol | Imported by |
|---|---|
| `BaseCommandHandler` | `superweapon_command_handlers.py`, `planet_command_handlers.py` (×7 deferred imports), `tests/unit/strategy/engine/test_command_ownership.py`, `tests/unit/strategy/engine/test_base_command_handler.py`, `tests/unit/strategy/test_command_handlers.py` (×6 deferred) |
| `add_move_order_if_needed` | `superweapon_command_handlers.py`, `tests/unit/strategy/test_command_handlers.py` (×3) |
| `create_default_registry` | `game/strategy/engine/game_session.py`, `tests/unit/strategy/engine/test_superweapon_command_handlers.py`, `tests/unit/strategy/engine/test_build_order_command_handler.py` |
| `CommandHandlerRegistry` | `tests/unit/strategy/test_command_handlers.py` |
| `ColonizeCommandHandler` | `tests/integration/colonization/test_explicit_orders.py`, `tests/unit/strategy/test_command_handlers.py` |
| `ColonizeMissionCommandHandler` | `tests/integration/colonization/test_explicit_orders.py`, `tests/unit/strategy/engine/test_colonize_mission_handler.py`, `tests/unit/strategy/test_command_handlers.py` |
| `MoveCommandHandler` | `tests/unit/strategy/test_command_handlers.py` |
| `InterceptCommandHandler` | `tests/unit/strategy/test_command_handlers.py` |
| `JoinCommandHandler` | `tests/unit/strategy/test_command_handlers.py`, `tests/integration/strategy/test_fleet_join_redirect.py` (×2 deferred) |
| `WarpCommandHandler` | `tests/integration/strategy/test_warp_orders.py`, `tests/unit/strategy/test_command_handlers.py` |
| `ClearOrdersCommandHandler` | `tests/unit/strategy/test_command_handlers.py` |
| `TransferCommandHandler` | `tests/repro_load_cargo_bug.py`, `tests/unit/strategy/test_command_handlers.py` |
| `SplitFleetCommandHandler` | `tests/unit/strategy/test_command_handlers.py` |
| `DeleteOrderCommandHandler` | `tests/unit/strategy/test_command_handlers.py` |
| `ReorderOrderCommandHandler` | `tests/unit/strategy/test_command_handlers.py` |
| `AddToConstructionQueueCommandHandler` | `tests/unit/strategy/test_command_handlers.py` |
| `RemoveFromConstructionQueueCommandHandler` | `tests/unit/strategy/test_command_handlers.py` |
| `ReorderConstructionQueueCommandHandler` | `tests/unit/strategy/test_command_handlers.py` |
| `BuildOrderCommandHandler` | `tests/unit/strategy/engine/test_build_order_command_handler.py` |
| `RemoveBuildOrderCommandHandler` | `tests/unit/strategy/engine/test_build_order_command_handler.py` (×2 deferred), `tests/unit/strategy/test_command_handlers.py` |
| `ICommandHandler` | (no external imports — used only inside the file's type hints) |

**Public-API count: 21 symbols.** Every one must remain importable from `game.strategy.engine.command_handlers` post-split if Option A is chosen.

---

## Caller-update strategy

**Choice: Option A (re-export shim).**

### Justification

1. **Caller count is high but lopsided.** ~30 import sites across production + tests. Of these, **only one is production code** (`game_session.py` imports `create_default_registry`); the rest are tests and 2 sibling handler modules.
2. **Sibling handler modules use `BaseCommandHandler` defensively.** `superweapon_command_handlers.py` (top-level import) and `planet_command_handlers.py` (×7 *deferred* imports — likely an old circular-dep workaround) both pull `BaseCommandHandler` from this module. Updating those is fine, but they should switch to importing from `game.strategy.engine.handlers.base` for clarity. *That part is Option-B-style migration internal to the package; the public shim still re-exports for external callers.*
3. **The public shim is cheap (~50 LOC of re-exports)** and matches the precedent set by `commands.py` (PROJ-298) and `formula_system.py` (PROJ-297) — both deleted after re-export shims served their purpose.
4. **The dispatcher (`create_default_registry`) is the most-imported symbol** and the one most likely to be called by future code. Keeping it importable via the canonical path (`game.strategy.engine.command_handlers`) avoids forcing every future caller to learn the new layout.
5. **Per the System Migration Policy**, the shim is transitional. Schedule its removal in a follow-up PROJ once tests + sibling modules migrate to the new package paths. Do NOT keep it indefinitely.

### Dispatcher wiring

`create_default_registry()` is the only place that knows the full handler set. After the split, it lives in `handlers/registry_factory.py` and imports each handler from its new domain module. The deferred imports of `superweapon_command_handlers` and `planet_command_handlers` are preserved (they're function-scoped to keep import-time light — that pattern is unchanged).

---

## Test plan

### Existing tests (must remain green)
- `tests/unit/strategy/test_command_handlers.py` — registry + per-handler unit tests (the canonical test module; bulk of coverage)
- `tests/unit/strategy/engine/test_base_command_handler.py` — `BaseCommandHandler` mixin tests
- `tests/unit/strategy/engine/test_command_ownership.py` — ownership-validation tests on the mixin
- `tests/unit/strategy/engine/test_colonize_mission_handler.py`
- `tests/unit/strategy/engine/test_build_order_command_handler.py`
- `tests/unit/strategy/engine/test_superweapon_command_handlers.py` (touches `create_default_registry`)
- `tests/integration/strategy/test_command_handlers.py`
- `tests/integration/strategy/test_warp_orders.py`
- `tests/integration/strategy/test_fleet_join_redirect.py`
- `tests/integration/colonization/test_explicit_orders.py`

### New tests added by this decomposition
1. **Public-API contract test** — `tests/unit/strategy/engine/test_command_handlers_public_api.py` (new): asserts every symbol in the documented public-API list above is importable from `game.strategy.engine.command_handlers` (the shim) AND from its canonical new home in `handlers/*`. This pins the shim contract and catches accidental deletions.
2. **Registry completeness test** — assert `create_default_registry()` returns a registry that dispatches every command class declared in `game.strategy.engine.commands`. Catches the case where a handler is moved to a new module but its `registry.register(...)` call is dropped during the move.
3. **No-cycle import test** — import each new module in isolation (fresh subprocess or `importlib.reload`) to confirm the split didn't introduce a circular import. Particularly important because `planet_command_handlers.py` currently uses 7 deferred imports of `BaseCommandHandler` — reasoning required to confirm whether those become eager imports post-split.

### Phase verification
Run the full sharded suite (`python Tools/test_sharded/test_sharded.py`) at the end of the file's sub-phase. Baseline must remain 15405 passed / 2 skipped.

---

## Risks

### 1. Shared helper home
**Where do `BaseCommandHandler`, `ICommandHandler`, `CommandHandlerRegistry`, and `add_move_order_if_needed` live?**

These four are imported by every handler module and by the two sibling modules (`superweapon_command_handlers`, `planet_command_handlers`). Putting them in `handlers/base.py` is the natural home, but two questions:
- (a) Does `superweapon_command_handlers.py` move into the new package (`handlers/superweapon.py`) or stay where it is? **Recommendation: keep where it is for this PROJ; a follow-up PROJ can fold it in. PROJ-309 is about decomposing the 1076-line file, not reorganizing the wider engine package.**
- (b) Same for `planet_command_handlers.py`. **Same recommendation.**

If either sibling module stays put, it just updates its `from game.strategy.engine.command_handlers import BaseCommandHandler` to `from game.strategy.engine.handlers.base import BaseCommandHandler`. That's a one-line change per import.

### 2. Cross-handler dependencies
**None observed.** No handler in the file calls another handler. Each handler is self-contained — it resolves entities via `BaseCommandHandler` helpers, validates, and mutates the session. The split is clean along the proposed seams.

### 3. `AddToConstructionQueueCommandHandler` carries private helper methods
This handler has `_check_design_valid` (lines 862–897) and `_load_design_cost` (lines 899–924) as instance methods. They are **only used by this handler**. They stay attached to the class in `handlers/construction_queue.py`. **No issue — flagged for awareness only.**

### 4. `planet_command_handlers.py`'s deferred-import pattern
That module imports `BaseCommandHandler` 7 times via deferred (function-local) imports. This is suspicious — it suggests a historical circular-dependency workaround. After the split, the import target becomes `game.strategy.engine.handlers.base`, which is leaf-level (no back-edges to the engine), so the deferred imports can almost certainly become a single top-level import. **Investigate during implementation; if cycle is gone, hoist to top-level. Don't preserve dead workarounds (Rule 3, clean-sheet).**

### 5. Order-sensitive registration
`create_default_registry()` registers handlers in a specific order. Reading the code, **the order is purely cosmetic** — `dict.__setitem__` doesn't care about insertion order for dispatch correctness, and there are no two handlers registered under the same key. **No risk; the order can be preserved verbatim or alphabetized — author's call.**

### 6. Test-file import block (line 10–27 of `test_command_handlers.py`)
Imports 14 symbols in one block. Stays valid via the shim. Nothing to change in tests for Option A.

---

## Open questions

1. **Should `superweapon_command_handlers.py` and `planet_command_handlers.py` be moved into `handlers/` in this same PROJ?** Recommendation above is "no, defer" — but if the user prefers a clean one-shot reorganization, those two modules also belong here and would naturally become `handlers/superweapon.py` and `handlers/planet_orders.py`. They would each grow this PROJ by ~600 LOC of touched code.
2. **Shim deletion timeline.** Should we open a follow-up ticket the moment the shim is created, or wait for organic caller migration? Precedent (PROJ-297, PROJ-298) is to do an explicit follow-up so the shim doesn't become permanent.
3. **Should `BaseCommandHandler` instance helpers become module-level functions instead of static methods on a mixin?** The methods are all `@staticmethod` — they don't use `self`. A clean-sheet design would make them module-level functions in `handlers/base.py` and skip the mixin entirely. **Out of scope for PROJ-309 — flag for a follow-up cleanup.** PROJ-309 is about size, not API surgery.
4. **Are there any unannotated functions remaining in the moved code?** Per PROJ-311 the entire `game/` tree is at 100% return-type coverage. Verify post-move — splitting code doesn't typically lose annotations, but a contract test against the audit script (`Projects/active_projects/PROJ-311/findings/annotation_audit.py`) would catch any regression.
