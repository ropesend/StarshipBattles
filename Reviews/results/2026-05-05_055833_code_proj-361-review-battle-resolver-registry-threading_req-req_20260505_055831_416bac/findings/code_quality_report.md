# PROJ-361 Code Quality & Architecture Review: Battle Resolver Registry Threading

**Reviewed files:**
1. `game/strategy/adapters/simulation_adapter.py` (455 lines)
2. `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py` (132 lines)
3. `Projects/active_projects/PROJ-361/plan.md` (64 lines)

**Scope:** Registry threading correctness, layer violations, IRegistryProvider conformance, test quality, type consistency, and pre-existing issues.

---

## Summary

| Severity | Count |
|----------|-------|
| CRITICAL | 1 |
| MAJOR    | 3 |
| MINOR    | 4 |
| INFO     | 1 |
| **Total** | **9** |

---

## Top Priority Issues

1. **CQ-01 (CRITICAL):** `_instances_to_ships` passes `None` to `inst.to_ship(registries=...)` when caller provides `registries=None` — will crash at `ShipSerializer.from_dict`. No fallback exists unlike the `registry_provider` path that was fixed.
2. **CQ-02 (MAJOR):** Type signature mismatch: `_build_spec` accepts `Optional[GameRegistries]` but passes it to `build_strategy_battle_spec(registries=...)` which requires non-optional.
3. **TC-01 (MAJOR):** Regression test does not verify registries threading through `_instances_to_ships`; only the `run_battle.registry_provider` path is covered.

---

## Findings

#### CRITICAL: `_instances_to_ships` has no fallback when registries=None, unlike `registry_provider` path
**ID:** CQ-01
**Location:** `game/strategy/adapters/simulation_adapter.py:270`, also `:142`
**Issue:** At line 270, `_instances_to_ships(fleet.ships, tid, registries)` passes the raw `registries` parameter (which may be `None`) directly to `ShipInstance.to_ship((0.0, 0.0), team_id=team_id, registries=registries)` (line 453). `ShipInstance.to_ship()` requires `registries: GameRegistries` (non-optional, confirmed at `game/strategy/data/ship_instance.py:684`). The call chain: `to_ship()` → `ShipInstanceBridge.to_ship()` → `ShipSerializer.from_dict(design_data, registries=registries)`. When `registries` is `None`, this crashes with `AttributeError: 'NoneType' object has no attribute 'get_components'`. Compare with the `run_battle.registry_provider` path at line 258 which correctly applies the `registries if registries is not None else get_default_registry_provider()` fallback. The same gap exists on the shortcut path at line 142 (`sole_survivor` branch).

**Impact:** Any caller that follows the `IBattleResolver` interface contract and passes `registries=None` (the default) will hit a runtime crash. Currently mitigated in practice because `ConflictResolutionEngine` always passes non-None registries, but the interface permits `None` and the code does not defend against it.

**Recommendation:** Apply the same fallback pattern as line 258 inside `_instances_to_ships`:
```python
def _instances_to_ships(self, instances, team_id, registries):
    _regs = registries if registries is not None else get_default_registry_provider()
    return [inst.to_ship((0.0, 0.0), team_id=team_id, registries=_regs) for inst in instances]
```
Or, if `GameRegistries` (dataclass) is required rather than `IRegistryProvider`, construct it from the fallback provider. This should also be applied to the shortcut-path call at line 142.

**Effort:** Simple

---

#### MAJOR: `_build_spec` passes `Optional[GameRegistries]` to function requiring non-optional
**ID:** CQ-02
**Location:** `game/strategy/adapters/simulation_adapter.py:311-338` → `game/strategy/combat/spec_compiler.py:78-83`
**Issue:** `_build_spec()` declares `registries: Optional['GameRegistries']` but passes it directly to `build_strategy_battle_spec(..., registries=registries, ...)`, which has the signature `registries: "GameRegistries"` (non-optional, no default). This means `None` can flow to a function whose type contract says it must be present. Currently benign because `build_strategy_battle_spec` immediately discards it with `_ = registries` (line 138), but any future use of the parameter would crash.

**Impact:** Latent type-safety hole. If `build_strategy_battle_spec` ever actually uses `registries`, passing `None` will cause runtime failure. Static type checkers (mypy strict) would flag this mismatch.

**Recommendation:** Either make `_build_spec` require non-optional `registries`, or add a precondition check / fallback to a default `GameRegistries` inside `_build_spec` before passing it forward. The former is preferred — if the caller always has registries, the type should reflect that.

**Effort:** Simple

---

#### MAJOR: Regression test does not cover `_instances_to_ships` registries threading
**ID:** TC-01
**Location:** `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py:71-107`, `simulation_adapter.py:269-271`
**Issue:** The regression test `test_resolve_battle_threads_injected_registries` verifies that `fresh_registries` reaches `run_battle.registry_provider` (identity check at line 104), but does NOT verify that the same registries flow through `_instances_to_ships` (line 270). The test mocks `run_battle` entirely, returning a pre-built outcome, which means `_instances_to_ships` is called with `_MockShipInstance.to_ship(..., registries=...)` but the registries value passed to it is never asserted. A future change that threads registries to `run_battle` but not to `_instances_to_ships` would pass this test.

**Impact:** The regression test gives false confidence. The injected `GameRegistries` could be silently dropped for the post-battle ship conversion (`_instances_to_ships`) while the test still passes.

**Recommendation:** Add an assertion that `_MockShipInstance.to_ship` was called with the injected registries, e.g.:
```python
def to_ship(self, pos, team_id=0, registries=None):
    self._last_registries = registries  # capture for assertion
    ...
# then assert all instances received the correct registries
```
Or patch `_instances_to_ships` separately and verify its `registries` argument. The mock `_MockShipInstance` should also note that the real `ShipInstance.to_ship` requires non-optional registries — the mock's default of `None` masks a type mismatch.

**Effort:** Simple

---

#### MAJOR: `_MockShipInstance.to_ship()` signature does not match real `ShipInstance.to_ship()`
**ID:** TC-02
**Location:** `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py:31`
**Issue:** The mock method `to_ship(self, pos, team_id=0, registries=None)` has `registries` as optional with a `None` default. The real `ShipInstance.to_ship()` at `game/strategy/data/ship_instance.py:684` declares `registries: 'GameRegistries'` (required, no default, no Optional). The mock is more permissive than the real signature, meaning tests won't catch `None`-passing bugs.

**Impact:** The test mock masks the CQ-01 issue — tests that pass `registries=None` to the resolver will never see the crash that would occur in production with the same input.

**Recommendation:** Update the mock signature to match the real one: `to_ship(self, pos, team_id=0, *, registries)` (no default). Use a `MagicMock()` or sentinel for tests where `registries` is not being tested. This aligns test-fidelity with the real contract and would have surfaced CQ-01 earlier.

**Effort:** Simple

---

#### MINOR: Late import of private constant `_BRIEF_RUN_TICK_BUDGET` violates encapsulation
**ID:** CQ-03
**Location:** `game/strategy/adapters/simulation_adapter.py:172`
**Issue:** Line 172 imports `_BRIEF_RUN_TICK_BUDGET` from `game.strategy.combat.spec_compiler`. The leading underscore marks this as a module-private name. Importing private names from other modules is an encapsulation break — the constant's owner may rename or delete it without considering external consumers. Both files are in the `game.strategy` layer, so no architectural boundary is crossed, but the encapsulation contract is weak.

**Impact:** A future refactor of `spec_compiler.py` that renames `_BRIEF_RUN_TICK_BUDGET` would break `simulation_adapter.py` with no warning (private names have no stability contract).

**Recommendation:** Either:
- Make the constant public (`BRIEF_RUN_TICK_BUDGET`) in `spec_compiler.py`, or
- Move it to a shared location (e.g. a `_constants.py` in the combat module), or
- Duplicate the constant in the adapter (it's only called from the adapter). Given it's `_DEFAULT_ABSOLUTE_MAX_TICKS // 10`, duplication is trivially safe.

**Effort:** Simple

---

#### MINOR: `_instances_to_ships` return-type annotation uses `List[Any]` where `List['Ship']` is knowable
**ID:** CQ-04
**Location:** `game/strategy/adapters/simulation_adapter.py:444`
**Issue:** The method returns `-> List[Any]`, but its sole purpose is to convert `ShipInstance` objects to simulation `Ship` objects. The return type could be `List['Ship']` (with `Ship` in `TYPE_CHECKING`). The `Any` annotation weakens type checking and loses downstream type information for `BattleResult.team_survivors`, which accepts `List[IPostBattleShip]` (both `Ship` and `ShipOutcome` implement this).

**Impact:** Callers working with `BattleResult.team_survivors` lose type safety. Mypy strict-mode would not catch misuse of the returned list.

**Recommendation:** Change return type to `List['Ship']` and add `from game.simulation.entities.ship import Ship` in the `TYPE_CHECKING` block.

**Effort:** Simple

---

#### MINOR: `get_resource_catalog()` called in `build_context_ship_builder` is not on `IRegistryProvider`
**ID:** AR-01
**Location:** `game/simulation/battle_runner.py:246` (consumer), `game/core/protocols/registry.py:24-37` (protocol)
**Issue:** `build_context_ship_builder` calls `registry_provider.get_resource_catalog()` but `IRegistryProvider` only defines 4 methods: `get_components`, `get_modifiers`, `get_vehicle_classes`, `get_resources`. `GameRegistries` has `get_resource_catalog` as a 5th method (PROJ-211 addition at `game/core/registry.py:109`), meaning the code relies on duck-typing beyond the protocol. This falls back gracefully because `TestRegistryProvider` and `DefaultRegistryProvider` both implement `get_resource_catalog()` (returning `None` and a lazy catalog respectively), and `GameRegistries.__post_init__` handles `None` by creating an empty catalog.

**Impact:** A custom `IRegistryProvider` implementation that strictly follows the protocol definition (4 methods) would fail with `AttributeError` when used with `build_context_ship_builder`. Low practical impact since the 3 known implementations all have the method.

**Recommendation:** Add `get_resource_catalog() -> Optional[ResourceCatalog]` to the `IRegistryProvider` protocol in `game/core/protocols/registry.py`. This formalizes the existing duck-typed contract.

**Effort:** Simple

---

#### MINOR: `run_battle` import from `game.simulation` is at module level but violates PROJ-252 spirit
**ID:** AR-02
**Location:** `game/strategy/adapters/simulation_adapter.py:26`
**Issue:** Line 26 imports `run_battle` from `game.simulation.battle_runner`. This is architecturally correct (Strategy → Simulation is allowed), but `run_battle`'s own docstring and `battle_runner.py` state that callers must supply `registry_provider` because simulation code cannot resolve it globally (PROJ-252). The strategy adapter correctly supplies it. No actual violation — just noting the documentation cross-reference is accurate.

**Impact:** None. Documentation is correct.

**Recommendation:** None needed. Observed for completeness.

**Effort:** N/A

---

#### INFO: `get_default_registry_provider()` import at runtime is correct per PROJ-306 but redundant on happy path
**ID:** CQ-05
**Location:** `game/strategy/adapters/simulation_adapter.py:248`
**Issue:** The import `from game.core.registry import get_default_registry_provider` at line 248 executes unconditionally (not inside a block), adding a small fixed overhead even when `registries is not None` (the common production case). PROJ-306 explicitly permits this import in the strategy layer.

**Impact:** Trivial. The import is a module-level cached call after the first invocation. No runtime concern.

**Recommendation:** Consider moving the import inside the fallback conditional at line 259:
```python
if registries is not None:
    registry_provider = registries
else:
    from game.core.registry import get_default_registry_provider
    registry_provider = get_default_registry_provider()
```
This defers the import cost to the fallback path only. Very minor optimization.

**Effort:** Simple

---

## Verification Summary

### Registry Threading Correctness (line 258)
**VERIFIED.** The fix at line 258 correctly threads `registries` to `run_battle.registry_provider` when non-None, and falls back to `get_default_registry_provider()` when `None`. This matches PROJ-306's policy (strategy layer IS the boundary for calling `get_default_registry_provider()`) and matches the PROJ-361 design.

### Call Site Audit

| Method | Line(s) | Threads `registries`? | Notes |
|--------|---------|----------------------|-------|
| `_build_spec()` | 311-338 | Yes | Passes `registries` to `build_strategy_battle_spec()` — but type mismatch (see CQ-02) |
| `_build_capture_context()` | 340-417 | Yes | Uses `registries` for `compute_components_registry_hash` with correct None guard |
| `_instances_to_ships()` | 439-454 | Yes — BUT no fallback | Passes `registries` to `inst.to_ship()`. When `registries=None`, this CRASHES (see CQ-01) |
| Shortcut `sole_survivor` | 142 | Yes — same issue as above | Same `_instances_to_ships` call, same None-crash risk |
| Shortcut `no_ships` | 155-165 | N/A | No `_instances_to_ships` call, returns empty dicts |
| `_run_simulated_battle()` → `run_battle` | 258-266 | Correctly threaded | The fixed path, correct |

### Layer Violations
**NONE FOUND.** Import audit of `game/strategy/adapters/simulation_adapter.py`:
- Imports from `game.simulation.*` (allowed: strategy → simulation)
- Imports from `game.strategy.*` (same layer)
- Imports from `game.core.registry` (allowed: strategy → core)
- No imports from `game.ui`, `game.ai`
- The late import at line 172 imports from `game.strategy.combat.spec_compiler` (same strategy layer — allowed)

### GameRegistries / IRegistryProvider Conformance
**VERIFIED.** `GameRegistries` at `game/core/registry.py:58-111` implements all 4 required `IRegistryProvider` methods (`get_components`, `get_modifiers`, `get_vehicle_classes`, `get_resources`) plus a 5th (`get_resource_catalog`). It passes `@runtime_checkable` conformance via `isinstance()`. See AR-01 for the `get_resource_catalog` protocol gap.

### Type Consistency
**ISSUE FOUND.** `_instances_to_ships` (line 443) accepts `registries: Optional['GameRegistries']` but passes it to `ShipInstance.to_ship()` (line 684 of `ship_instance.py`) which requires `registries: 'GameRegistries'` (non-optional). This is a documented finding above (CQ-01). Both `ShipInstance.to_ship()` and `ShipInstanceBridge.to_ship()` (line 51 of `ship_instance_bridge.py`) have consistent non-optional signatures.
