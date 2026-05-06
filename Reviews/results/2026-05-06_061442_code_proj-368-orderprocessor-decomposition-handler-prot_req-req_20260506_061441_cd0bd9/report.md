# Review Report: PROJ-368 OrderProcessor Decomposition

**Request ID:** req_20260506_061441_cd0bd9
**Review mode:** code (full)
**Scope:** `game/strategy/engine/order_processor.py`, `game/strategy/engine/order_handlers/`, `game/strategy/engine/superweapon_order_processor.py`, plus associated tests and docs.
**Methodology:** Exhaustive read of all 8 handler source files (2261 LOC), all test files (AST guards, per-handler tests, registry completeness), all PROJ-368 design docs (plan, design, decisions, outcome), plus architecture/convention references.

---

## Findings

### CRITICAL

None.

---

### MAJOR

**MAJ-001** — `transfer.py` at 492 LOC approaches the 500-LOC ceiling.
- **File:** `game/strategy/engine/order_handlers/transfer.py`
- **Description:** The file is 492 lines (8 lines shy of the 500-LOC ceiling enforced by `docs/03_CONVENTIONS.md`). When PROJ-370 (data-layer mutator protocols) threads `IFleetMutator`/`IPlanetMutator` through the 7 dispatch branches, or any bugfix adds new logic, this file will exceed the ceiling. The file is the most complex handler — it contains the dispatch entry point (lines 59-201), target-fleet resolver (lines 207-236), and all 7 explicit `_dispatch_*` branches (lines 242-492).
- **Suggested remediation:** Split into `transfer.py` (dispatch entry + `_resolve_target_fleet_by_id`, ~250 LOC) and `transfer_branches.py` (7 `_dispatch_*` methods, ~240 LOC). This mirrors the split structure used for `engine/handlers/` sub-modules.

**MAJ-002** — AST guard has an `In`/`NotIn` comparison coverage gap.
- **File:** `tests/unit/strategy/engine/test_order_processor_no_legacy_helpers.py:55-83`
- **Description:** `test_no_order_type_branching_in_facade()` walks `ast.Compare` nodes but only checks for `ast.Eq` operator comparisons (line 74). The `process_transfer` shim in `order_processor.py:118-122` uses `order_type not in (OrderType.TRANSFER, OrderType.LOAD_POPULATION, OrderType.UNLOAD_POPULATION)`, which is an `ast.In`/`ast.NotIn` node — not matched by the current check. A future developer could introduce `if order.type in (OrderType.X, ...)` branching on the facade without this test failing. The Phase 5 reference-count cap (`test_order_processor_minimal_order_type_references`, ≤6 OrderType attr refs) provides indirect protection, but the branching test should be watertight in its own right.
- **Suggested remediation:** Extend the AST walk at line 70-81 to also match `ast.In` and `ast.NotIn` operators:
  ```python
  if isinstance(cmp_op, (ast.Eq, ast.In, ast.NotIn)):
  ```

**MAJ-003** — Stale `process_self_destruct` documentation in `superweapon_order_processor.py`.
- **File:** `game/strategy/engine/superweapon_order_processor.py:8,54`
- **Description:** The module docstring (line 8) states "Only stellerate_star and self_destruct consume the ship" and the class docstring (line 54) still lists `process_self_destruct()` as a method. `process_self_destruct` was deleted in PROJ-368 Phase 2 and moved to `SelfDestructHandler` at `order_handlers/self_destruct.py`. The deletion comment at line 664 is present, but the top-of-file docstrings were not updated.
- **Suggested remediation:** Update line 8 to remove the `self_destruct` reference. Update line 54 to remove or modify the `process_self_destruct()` bullet.

---

### MINOR

**MIN-001** — `OrderProcessor.process_transfer` facade shim is asymmetrical vs other facade methods.
- **File:** `game/strategy/engine/order_processor.py:109-130`
- **Description:** `process_transfer` reads the order at the facade level (`fleet.get_current_order()`, line 116) and validates the type is in the transfer family before delegating. By contrast, `process_join_fleet`, `process_colonize`, and `process_instant_orders` delegate immediately and let the handler validate the order type internally. The Transfer handler already validates the order type (transfer.py:71-78), making the facade-level gate partially redundant. The rationale is that `process_transfer` must return `TransferResult(success=..., amount_transferred=...)` which differs from the handler's `OrderExecutionResult` — but the same reshaping pattern is used by the other facade methods (e.g., `process_join_fleet` reshapes from `OrderExecutionResult` to `JoinFleetResult`).
- **Suggested remediation:** Either: (a) make `process_transfer` reshape `OrderExecutionResult` like the other shims, dropping the pre-check (handler already validates), or (b) add an inline comment at line 116 explaining why this shim reads the order directly.

**MIN-002** — Non-canonical import ordering in `order_processor.py`.
- **File:** `game/strategy/engine/order_processor.py:29`
- **Description:** Line 29 places `logger = logging.getLogger(__name__)` between `from game.strategy.interfaces.engines import IOrderProcessor` (line 27) and `from game.strategy.data.fleet import Fleet` (line 30). The logger assignment interrupts the import block. The `import typing` listing at the top (lines 23-24) also uses deprecated `Optional, List, Tuple, Dict, Any` from `typing` rather than the Python 3.14-native `| None`, `list`, `tuple`, `dict` syntax.
- **Suggested remediation:** Move `logger = logging.getLogger(__name__)` after all imports (before the class definition). Optionally upgrade typing imports to 3.14 syntax (PEP 604).

**MIN-003** — LOC counter in `test_order_processor_facade_under_200_loc` uses strict `<` but the plan target was `≤ 200`.
- **File:** `tests/unit/strategy/engine/test_order_processor_no_legacy_helpers.py:49`
- **Description:** The test asserts `loc < 200` (strict less-than). The plan.md target (lines 46, 200, 386) says `≤ 200` (less-than-or-equal). At 168 LOC the test passes, but if a future minor addition pushes the file to exactly 200 LOC, the test would fail despite being within the plan's stated ceiling.
- **Suggested remediation:** Change to `loc <= 200` to match the plan specification. Or update plan.md to match the stricter `< 200`.

---

### INFO (Verified Clean)

**Phase 4 Atomicity Correctness:**
- `order_processor.py` is 168 LOC. All 6 public methods (`process_join_fleet`, `process_colonize`, `process_transfer`, `process_instant_orders`, `execute_action_order`, `__init__`) delegate to the registry.
- AST guard `test_no_legacy_private_helpers_on_order_processor` (test_order_processor_no_legacy_helpers.py:22-43) bans exactly the 9 deleted private method names plus any `_process_*` prefix — no overly-broad allowlist; the forbidden set is exhaustive. Test is sound.
- AST guard `test_order_processor_facade_under_200_loc` (line 47-52) asserts LOC < 200. Passes at 168 LOC.
- Registry-completeness test `test_every_action_order_type_has_a_handler` (test_handler_registry_completeness.py:23-32) imports `ACTION_ORDER_TYPES` and `PLANET_ACTION_ORDER_TYPES` directly from `order_types.py` — the canonical source. Subtracts planet-only types, adds `JOIN_FLEET`. The `test_planet_action_orders_NOT_registered` (line 78-82) verifies `ACTIVATE_ABILITY`/`DEACTIVATE_ABILITY` are excluded. Stub handlers cannot bypass this because it asserts set-superset (`missing = expected - registered`).

**Handler Semantic Equivalence — Per-Handler Verdict:**
- **JoinFleetHandler** (`join_fleet.py`): The 3-phase pipeline (Phase A collect, Phase B mutual-pair canonicalize via `_elect_canonical_merges`, Phase C aliveness re-validate) is preserved verbatim. Most-ships-wins with smaller-id tiebreak correctly implemented (lines 237-243 using `str(source.id) < str(target.id)` — deterministic for tests). `process_instant_orders` is handler-specific (not on Protocol), called via `registry.get(OrderType.JOIN_FLEET).process_instant_orders(...)`.
- **ColonizeHandler** (`colonize.py`): Port of `process_colonize` + `_deploy_drop_pod`. `fleet_consumed=True` at line 134 mirrors the legacy `result.colonized` semantics (documented in the line 128-131 comment). Q1 resolution preserved: missing `component_registry` logs, pops, returns `False` (line 54-58).
- **SelfDestructHandler** (`self_destruct.py`): Lifted from `superweapon_order_processor.py`'s former `process_self_destruct`. The deleted method is confirmed absent (`grep` finds no `def process_self_destruct` in the engine layer; only docstring references in `superweapon_order_processor.py` lines 8, 54, and a deletion marker at line 664). SG-003 empty-fleet cleanup contract preserved (lines 92-93). `fleet_consumed` only True when fleet emptied, never as precondition.
- **TransferHandler** (`transfer.py`): 7 explicit `_dispatch_*` branches cover all cargo-type sub-branches (verified by reading each method). BUG-70 LOAD_POPULATION auto-resolve at fleet hex preserved (lines 99-127). PROJ-343 T1.1 `target_fleet_id` resolution brittleness preserved verbatim (lines 207-236). Dispatch decision logic matches the deleted `process_transfer` switch ladder.
- **SuperweaponHandlerAdapter × 5** (`superweapons.py`): All 5 adapters follow the identical pattern: `getattr(self._processor, f"process_{self._spec.order_type.name.lower()}")` at line 70, called with uniform 5-arg signature, result reshaped to `OrderExecutionResult`. Defensive skip-guard at line 94 prevents accidental `SELF_DESTRUCT` registration. `build_superweapon_handlers` yields exactly 5 adapters (`test_build_superweapon_handlers_yields_5_adapters` verifies).

**Test Migration Soundness (spot-checked 3 migrations):**
1. Original `test_order_processor_fleet_merge.py` → handler-level `test_execute_action_order_co_located_merges()` (test_join_fleet_handler.py:77-89): Exercises same `JoinFleetHandler.execute_action_order` path; uses `_real_fleet` with `trigger_speed_recalculation` patch (equivalent to the original `MagicMock(spec=Fleet)` approach). Event-bus capture verifies `FLEET_JOINED`.
2. Original `test_order_processor_instant.py`'s BUG-122 mutual-pair test → `test_process_instant_orders_mutual_pair_canonicalization_most_ships_wins()` (test_join_fleet_handler.py:136-152): Same election rule (most ships wins). Assertions verify loser removed from empire, winner preserved. Patch targets `trigger_speed_recalculation` on fleet types, same as original.
3. Original `test_order_processor_transfer.py`'s staging-yard test → `test_dispatch_drop_pod_load_reverse_iteration()` (test_transfer_handler.py:177-217): Same reverse-iteration pattern; Mock `remove_from_staging_yard` with `side_effect=lambda i: planet.staging_yard.pop(i)` mirrors original behavior. Assertions verify specific pod loaded, other preserved.

**Public Surface Preservation:**
- External callers verified: `turn_phase_registry.py:228` calls `e.order_processor.process_instant_orders`; `action_execution_engine.py:215` calls `self._order_processor.execute_action_order`; `turn_engine.py:339-341` lazily constructs `OrderProcessor`. All 3 call sites reference methods that exist on the facade.
- `process_instant_orders` is a `JoinFleetHandler`-only method, correctly NOT on the `IOrderHandler` Protocol (resolution: `decisions.md` row 8, Option B). The facade at `order_processor.py:141-142` accesses it via `registry.get(OrderType.JOIN_FLEET).process_instant_orders(empires)` — no `isinstance` check needed.

**PROJ-370 Readiness:**
- Handler files exist at exact paths: `game/strategy/engine/order_handlers/colonize.py`, `game/strategy/engine/order_handlers/transfer.py`.
- ColonizeHandler mutation seams: `empire.add_colony(planet)` (line 97), `fleets.pop_order()` (line 98), `ship.carried_items.pop(item_index)` (line 156), `planet.facilities.append(facility)` (line 166), `planet.add_to_stockpile(resource, amount)` (line 171). All concentrated in `execute_action_order` and `_deploy_drop_pod` — single file, small surface.
- TransferHandler mutation seams: `planet.consume_from_stockpile` (line 265), `fleet.resources.load_cargo_to_fleet` (line 267), `pop.count -= to_load` (line 302), `planet.add_to_stockpile` (line 382), `fleet.resources.unload_cargo_from_fleet` (line 381), `planet.populations.append` (line 426), `species_pop.count += actual_unloaded` (line 428), `planet.remove_from_staging_yard` (line 359), `planet.add_to_staging_yard` (line 456). Spread across 7 dispatch branches — each branch is a single, clean mutation target for PROJ-370 to intercept.

**General Quality:**
- No layering violations: zero imports from `game.ui/` in any handler file.
- No broad `except Exception` (with or without rationale comment) in any handler file.
- All public methods have return-type annotations (`-> OrderExecutionResult`, `-> Tuple[OrderType, ...]`, etc.).
- No `print()` debug leakage.
- Documentation updates: `docs/systems/strategy_layer.md` § 3 "Order Handlers (PROJ-368)" subsection present (lines 350-396) with handler table, AST guards, parallel-registry reference. `docs/02_PATTERNS.md` Pattern #7 "Parallel Order-Handler Registry" subsection cross-references the two registry systems.

**Line counts (LOC):**
| File | LOC | Status |
|------|-----|--------|
| `order_processor.py` | 168 | < 200 ✓ |
| `superweapon_order_processor.py` | 708 | unchanged, out of scope |
| `order_handlers/base.py` | 155 | ✓ |
| `order_handlers/registry_factory.py` | 70 | ✓ |
| `order_handlers/join_fleet.py` | 283 | ✓ |
| `order_handlers/colonize.py` | 173 | ✓ |
| `order_handlers/self_destruct.py` | 111 | ✓ |
| `order_handlers/transfer.py` | 492 | Near ceiling (MAJ-001) |
| `order_handlers/superweapons.py` | 101 | ✓ |

---

## Verification Matrix

N/A — this is a primary review, not a follow-up. No parent request.
