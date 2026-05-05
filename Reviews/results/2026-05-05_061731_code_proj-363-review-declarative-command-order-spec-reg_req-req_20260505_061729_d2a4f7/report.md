# Review Report: PROJ-363 Declarative Command/Order Spec Registry

**Review Type:** code
**Request ID:** req_20260505_061729_d2a4f7
**Review Mode:** normal
**Commit:** 579a097ec
**Scope:** 7 files (see scope.md)
**Reviewer:** OpenCode (single-agent)

---

## Summary

The PROJ-363 declarative spec registry is well-executed. All 35 COMMAND_SPECS entries correctly match the 35 declared Command DTOs; the `__getattr__`-based dispatch resolver produces correct closures; the OrderType frozenset import-cycle workaround is sound (contract test is sufficient); no layer violations found; facade dispatch surface is bit-identical (all 31 dispatch helpers remain callable); and the four Set*/SetBuildQueuePaused specs correctly use `facade_helper_name=None`. Two minor discrepancies were found: a stale `MOVEMENT_ORDER_TYPES` copy in `action_time_resolver.py` missing WARP, and the `__getattr__` resolver producing non-identical closures on repeated access (design-intentional, but worth noting).

**Findings:** 0 CRIT | 0 MAJ | 1 MIN | 3 NIT | 1 INFO

---

## Verification of Specific Instructions

### 1. All 35 COMMAND_SPECS entries — VERIFIED

Cross-checked against all Command DTOs in `game/strategy/engine/commands/__init__.py`. The contract tests `test_every_command_class_has_a_spec` and `test_no_orphan_specs` pass (and are well-written). All 35 classes are accounted for:

| # | Command Class | OrderType | Category | Execution Model | Facade Helper |
|---|---|---|---|---|---|
| 1 | IssueMoveCommand | MOVE | movement | action | dispatch_issue_move |
| 2 | IssueWarpCommand | WARP | movement | action | dispatch_issue_warp |
| 3 | IssueInterceptCommand | MOVE_TO_FLEET | movement | action | dispatch_issue_intercept |
| 4 | IssueJoinFleetCommand | JOIN_FLEET | movement | instant | dispatch_issue_join_fleet |
| 5 | IssueColonizeCommand | COLONIZE | action | action | dispatch_issue_colonize |
| 6 | IssueTransferCommand | TRANSFER | action | action | dispatch_issue_transfer |
| 7 | QueueColonizeMissionCommand | None | action | mission | dispatch_queue_colonize_mission |
| 8 | ClearOrdersCommand | None | fleet_management | instant | dispatch_clear_orders |
| 9 | SplitFleetCommand | None | fleet_management | instant | dispatch_split_fleet |
| 10 | DeleteOrderCommand | None | fleet_management | instant | dispatch_delete_order |
| 11 | ReorderOrderCommand | None | fleet_management | instant | dispatch_reorder_order |
| 12 | IssueImplodePlanetCommand | IMPLODE_PLANET | superweapon | action | dispatch_issue_implode_planet |
| 13 | IssueStellerateStarCommand | STELLERATE_STAR | superweapon | action | dispatch_issue_stellerate_star |
| 14 | IssueOpenWarpPointCommand | OPEN_WARP_POINT | superweapon | action | dispatch_issue_open_warp_point |
| 15 | IssueCloseWarpPointCommand | CLOSE_WARP_POINT | superweapon | action | dispatch_issue_close_warp_point |
| 16 | IssueCreateDysonSphereCommand | CREATE_DYSON_SPHERE | superweapon | action | dispatch_issue_create_dyson_sphere |
| 17 | IssueSelfDestructCommand | SELF_DESTRUCT | superweapon | action | dispatch_issue_self_destruct |
| 18 | QueueImplodePlanetMissionCommand | None | superweapon | mission | dispatch_queue_implode_planet_mission |
| 19 | QueueStellerateStarMissionCommand | None | superweapon | mission | dispatch_queue_stellerate_star_mission |
| 20 | QueueOpenWarpPointMissionCommand | None | superweapon | mission | dispatch_queue_open_warp_point_mission |
| 21 | QueueCloseWarpPointMissionCommand | None | superweapon | mission | dispatch_queue_close_warp_point_mission |
| 22 | QueueCreateDysonSphereMissionCommand | None | superweapon | mission | dispatch_queue_create_dyson_sphere_mission |
| 23 | IssueBuildOrderCommand | BUILD | build | production | dispatch_issue_build_order |
| 24 | RemoveBuildOrderCommand | None | build | instant | dispatch_remove_build_order |
| 25 | AddToConstructionQueueCommand | None | construction | instant | dispatch_add_to_construction_queue |
| 26 | RemoveFromConstructionQueueCommand | None | construction | instant | dispatch_remove_from_construction_queue |
| 27 | ReorderConstructionQueueCommand | None | construction | instant | dispatch_reorder_construction_queue |
| 28 | SetBuildQueuePausedCommand | None | construction | instant | **None** |
| 29 | IssuePlanetOrderCommand | None | planet | planet | dispatch_issue_planet_order |
| 30 | ClearPlanetOrdersCommand | None | planet | instant | dispatch_clear_planet_orders |
| 31 | DeletePlanetOrderCommand | None | planet | instant | dispatch_delete_planet_order |
| 32 | SetAtmosphereTargetCommand | None | planet | instant | dispatch_set_atmosphere_target |
| 33 | SetGravityTargetCommand | None | planet | instant | **None** |
| 34 | SetWaterTargetCommand | None | planet | instant | **None** |
| 35 | SetRadiationShieldTargetCommand | None | planet | instant | **None** |

### 2. `__getattr__` closures and facade introspection — VERIFIED (with notes)

- **Correctness**: The `__getattr__` in `command_dispatch_slice.py:72-100` correctly captures `command_class` and `handle_command`, generates closures that instantiate the right Command via `command_class(**kwargs)`, and forwards to `handle_command`.
- **`hasattr`**: Works on both the facade (explicit methods) and the slice (`__getattr__` resolves). Tested in `test_command_dispatch_slice_getattr.py:90-94`.
- **`dir()`**: Works on the facade (explicit methods listed). Does NOT list dispatch helpers on the slice — see NIT-001.
- **Identity**: Each `__getattr__` access produces a fresh closure — see NIT-002.
- **Test coverage**: `tests/unit/strategy/facade/test_command_dispatch_slice_getattr.py` covers resolution, forwarding, unknown-name error, and `hasattr`. `tests/unit/strategy/engine/test_command_registry_contract.py:236-271` covers slice-class-level reachability for all 31 helpers. `tests/unit/strategy/facade/test_facade_dispatch.py` covers facade dispatch correctness end-to-end.

### 3. OrderType frozenset import-cycle workaround — SUFFICIENT

The contract test at `tests/unit/strategy/engine/test_command_specs_contract.py:135-147` pins exact equality between:
- `order_types.py` hardcoded `MOVEMENT_ORDER_TYPES` vs `specs.movement_order_types()`
- `order_types.py` hardcoded `ACTION_ORDER_TYPES` vs `specs.action_order_types()`
- `order_types.py` hardcoded `PLANET_ACTION_ORDER_TYPES` vs `specs.planet_action_order_types()`

Adding a new OrderType without updating both the spec and the frozenset will fail the contract test. The design is an intentional trade-off (two-source duplication to avoid import cycles), clearly documented in `order_types.py:40-55`. Sufficient for regression prevention.

However, a subtlety: `action_time_resolver.py` has its own local `MOVEMENT_ORDER_TYPES` that does NOT match either source — see MIN-001.

### 4. Layer violations — NONE FOUND

All imports respect the strategy-layer boundaries:
- `specs.py` imports from `game.strategy.engine.commands` (same sub-package) and `game.strategy.engine.handlers.*` (same layer) — fine.
- `order_types.py` only imports from `game.core.hex_math` and `game.strategy.data.*` (sibling) — fine.
- `registry_factory.py`, `action_time_resolver.py`, `command_dispatch_slice.py` all use deferred (function-local) imports of `specs.py` to avoid cycles at module-load time — clean, idiomatic.
- No imports from AI, Simulation, or UI layers into strategy.

### 5. Facade dispatch surface bit-identical — CONFIRMED

`StrategySessionFacade` retains all 31 dispatch methods (lines 186-308) as explicit one-line forwarders to `self._command_slice`. Each dispatches the same Command type. Existing tests (`test_facade_dispatch.py`, `test_strategy_session_facade_public_api.py`, `test_command_registry_contract.py`) all verify dispatch reachability and correctness.

### 6. SetGravity/SetWater/SetRadiationShield/SetBuildQueuePaused with facade_helper_name=None — CORRECT

All four have `facade_helper_name=None` in `specs.py`:
- `SetBuildQueuePausedCommand` (line 476): documented as "FEAT-17 wires through other paths"
- `SetGravityTargetCommand` (line 519)
- `SetWaterTargetCommand` (line 527)
- `SetRadiationShieldTargetCommand` (line 535)

None of these four commands appear in the facade dispatch surface (no corresponding `dispatch_set_*` method on `StrategySessionFacade`). They also don't appear in `EXISTING_FACADE_DISPATCH_HELPERS` in the contract test or in `PUBLIC_METHODS` in the public API test. This is consistent: these are environment-modification commands that are routed through planet-panel UI paths, not the generic command dispatch pipeline.

---

## Findings

### MIN-001: Stale MOVEMENT_ORDER_TYPES copy in action_time_resolver.py missing WARP

**File:** `game/strategy/services/action_time_resolver.py:48`
**Severity:** MIN

The module-level `MOVEMENT_ORDER_TYPES` in `action_time_resolver.py` is:
```python
MOVEMENT_ORDER_TYPES: frozenset = frozenset({OrderType.MOVE, OrderType.MOVE_TO_FLEET})
```

Both `order_types.py:58-62` and `specs.movement_order_types()` include `OrderType.WARP`. The `action_time_resolver` uses this set at line 79 for an early-action-time-0 return. If `ActionExecutionEngine` ever routes a WARP order through the resolver (it shouldn't, since WARP goes through `FleetMovementEngine`), the resolver would look up `ORDER_TO_ABILITY_MAP[OrderType.WARP]` → get `None` → return 1 instead of 0.

**Risk:** Low. WARP is not routed through `ActionExecutionEngine`. This is a maintenance hazard — three copies of `MOVEMENT_ORDER_TYPES` exist (order_types.py, specs.py derivation, action_time_resolver.py local), and they can silently diverge.

**Recommendation:** Either delete the local `MOVEMENT_ORDER_TYPES` and use the import from `order_types.py` (the module already imports from order_types at line 23), or add a contract test asserting its equality to the canonical set. Line 23 already imports `PLANET_ACTION_ORDER_TYPES` from `order_types.py`; extending it to import `MOVEMENT_ORDER_TYPES` too would consolidate to a single source.

---

### NIT-001: `dir()` on CommandDispatchSlice does not list dispatch helpers

**File:** `game/strategy/facade/slices/command_dispatch_slice.py:72`
**Severity:** NIT

`Python`'s builtin `dir()` does not invoke `__getattr__`. Hence `dir(slice_instance)` won't show `dispatch_issue_move` or any other resolved helper. This matters only for debugging/introspection of the slice directly (the facade remains unaffected since it has explicit methods listed in `dir()`).

**Recommendation:** Add a `__dir__` override on `CommandDispatchSlice` that merges `specs_by_facade_helper().keys()` into the inherited `dir()` result. Example:
```python
def __dir__(self):
    from game.strategy.engine.commands.specs import specs_by_facade_helper
    return sorted(set(super().__dir__()) | set(specs_by_facade_helper().keys()))
```
This is low priority but improves developer ergonomics for interactive debugging.

---

### NIT-002: `__getattr__` produces non-identity closures on repeated access

**File:** `game/strategy/facade/slices/command_dispatch_slice.py:91-100`
**Severity:** NIT

Each `getattr(slice_instance, "dispatch_issue_move")` call produces a new function object:
```python
assert getattr(slice, "dispatch_issue_move") is not getattr(slice, "dispatch_issue_move")
```
This is intentional and documented in the module-level comment (line 60-62: "returns a fresh closure on every call — there's no caching needed"). It has no practical impact because dispatch helpers are resolved once per UI action. However, any code that relies on function-identity comparison (e.g., `func is some_stored_ref`) would break. No such code exists in the current test suite.

**Recommendation:** No action needed. If caching is ever desired, a `_dispatch_cache: dict` could be stored as a `__slots__` member and populated lazily, but the current "fresh-per-call" design is simpler and prevents stale-closure bugs if `_handle_command` were ever replaced.

---

### NIT-003: Missing test coverage for WARP in `movement_order_types` derivation

**File:** `tests/unit/strategy/engine/test_command_specs_contract.py:135-137`
**Severity:** NIT

`test_movement_order_types_derivation_matches_constant` verifies `movement_order_types() == MOVEMENT_ORDER_TYPES`, which covers all three (MOVE, MOVE_TO_FLEET, WARP) since both agree. However, if WARP were accidentally deleted from the hardcoded set but left in the spec table, the test would catch it. The concern in MIN-001 (missing WARP in `action_time_resolver.py`'s local copy) is not caught because that copy is tested nowhere. A separate contract test for that module's `MOVEMENT_ORDER_TYPES` would close this gap.

**Recommendation:** Add a test in the contract suite that asserts `action_time_resolver.MOVEMENT_ORDER_TYPES == order_types.MOVEMENT_ORDER_TYPES`, or better, make `action_time_resolver.py` import the constant rather than maintain its own copy.

---

### INFO-001: Redundant facade forwarders post-Phase-4

**File:** `game/strategy/facade/strategy_session_facade.py:186-308`
**Severity:** INFO

The facade retains 31 explicit `dispatch_*` methods, each a one-line forwarder to `self._command_slice`. After the Phase 4 `__getattr__` collapse on the slice, these facade forwarders could also be collapsed into a `__getattr__` resolver. This would remove ~120 lines of boilerplate. However, keeping them preserves `dir()` and `hasattr()` on the public facade without needing a `__dir__` override, and the verbatim method signatures make the API self-documenting in Sphinx/pydoc.

**Recommendation:** No action required. The current design is correct and test-passing. If facade LOC ever needs trimming, a `__getattr__` on `StrategySessionFacade` that delegates to the slice's resolver directly would be a drop-in replacement.

---

## Verification Matrix

Not applicable (not a follow-up review).

## Conclusion

PROJ-363's spec registry is production-ready. The single-source-of-truth COMMAND_SPECS table is exhaustive (35/35), the `__getattr__` dispatch resolver is correct, the import-cycle workaround has adequate test coverage, and the facade surface is bit-identical. The only actionable finding (MIN-001 — stale MOVEMENT_ORDER_TYPES copy) is a maintenance hazard with trivial fix (import the canonical constant).
