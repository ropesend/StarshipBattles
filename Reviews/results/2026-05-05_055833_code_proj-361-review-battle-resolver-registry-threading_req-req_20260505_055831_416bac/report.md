# PROJ-361 Review: Battle Resolver Registry Threading

**Request ID:** req_20260505_055831_416bac
**Review Type:** code (delegated by Claude Code)
**Review Mode:** normal
**Scope:**
- `game/strategy/adapters/simulation_adapter.py` (around line 258)
- `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py` (new)
- `Projects/active_projects/PROJ-361/plan.md`
**Requested By:** claude-code
**Completed:** 2026-05-05T06:01:00Z

---

## Executive Summary

**Total Findings: 9** | **Critical: 0** | **Major: 4** | **Minor: 3** | **Info: 2**

The PROJ-361 fix at line 258 is **correct and verified** — injected `registries` flows to `run_battle.registry_provider` when present, and the PROJ-306 fallback (`get_default_registry_provider()`) activates when `registries is None`. No layer violations were found. Three pre-existing defects were identified: `_instances_to_ships` lacks the same fallback guard (CQ-01), a type mismatch between `_build_spec` and `build_strategy_battle_spec` (CQ-02), and two test coverage gaps in the regression test (TC-01, TC-02). These are not regressions from PROJ-361 but represent incomplete coverage of the injection path.

**Overall Assessment:** The fix is sound. The remaining issues are pre-existing defense-in-depth gaps — no active production crash paths. Recommend addressing in a follow-up project.

---

## Verification Matrix

### Primary Verification

| Claim | Status | Evidence |
|-------|--------|----------|
| Registry threading to `run_battle.registry_provider` works | Verified | `simulation_adapter.py:258` — ternary correctly selects `registries` when non-None |
| PROJ-306 fallback preserved (`get_default_registry_provider()`) | Verified | `simulation_adapter.py:259` — fallback triggers when `registries is None` |
| `GameRegistries` implements `IRegistryProvider` | Verified | `game/core/registry.py:92-111` — all 4 required methods + `get_resource_catalog()` |
| No layer violations | Verified | All imports within allowed dependency graph (Strategy → Simulation / Core) |

### Call Site Audit

| Method | Line(s) | Threads `registries`? | Fallback Guard? | Notes |
|--------|---------|----------------------|-----------------|-------|
| `_build_spec()` | 311-338 | Yes | No (type mismatch) | Passes `Optional[GameRegistries]` to non-optional param (CQ-02) |
| `_build_capture_context()` | 340-417 | Yes | Yes | `None` guard at line 392-395 |
| `_instances_to_ships()` | 439-454 | Yes | **No** | Passes raw `registries` — crashes if `None` (CQ-01) |
| Shortcut `sole_survivor` | 142 | Yes | **No** | Same `_instances_to_ships` crash risk |
| Shortcut `no_ships` | 155-165 | N/A | N/A | Returns empty dicts, no `to_ship` call |
| `_run_simulated_battle()` → `run_battle` | 258-266 | Yes | **Yes** | PROJ-361 fix — correct |

---

## Findings

### Top Priority Issues

1. **CQ-01 (MAJOR):** `_instances_to_ships` passes `None` to `ShipInstance.to_ship()` when caller omits registries — pre-existing crash path
2. **TC-01 (MAJOR):** Regression test does not verify registries threading through `_instances_to_ships`
3. **TC-02 (MAJOR):** Mock `to_ship()` signature masks non-optional registries contract
4. **CQ-02 (MAJOR):** `_build_spec` passes `Optional[GameRegistries]` to function requiring non-optional

---

#### MAJOR: `_instances_to_ships` has no fallback when `registries=None`, unlike `registry_provider` path
**ID:** CQ-01
**Location:** `game/strategy/adapters/simulation_adapter.py:142` and `:270` (callers of `:439-454`)
**Issue:** `_instances_to_ships` passes the raw `registries` parameter (which defaults to `None`) directly to `inst.to_ship(..., registries=registries)`. The real call chain is:
```
inst.to_ship(..., registries=None)
  → ShipInstanceBridge.to_ship(..., registries=None)
    → ShipSerializer.from_dict(design_data, registries=None)  # CRASH
```
The PROJ-361 fix applied the fallback pattern (`registries if registries is not None else get_default_registry_provider()`) only to the `run_battle.registry_provider` path (line 258). `_instances_to_ships` was not given the same treatment. This is a **pre-existing defect** — PROJ-361 did not introduce it, nor did it fix it.

**Impact:** If any caller follows `IBattleResolver.resolve_battle()`'s default contract (`registries=None`), a runtime crash occurs when converting ships back after the battle. Current production callers (`ConflictResolutionEngine`) always supply non-None registries, so this is not an active crash in production. However, it violates the interface contract and will bite future callers.

**Recommendation:** Apply the same fallback pattern as line 258:
```python
def _instances_to_ships(self, instances, team_id, registries):
    from game.core.registry import get_default_registry_provider
    _regs = registries if registries is not None else get_default_registry_provider()
    return [inst.to_ship((0.0, 0.0), team_id=team_id, registries=_regs) for inst in instances]
```
**Effort:** Simple

---

#### MAJOR: Regression test does not cover `_instances_to_ships` registries threading
**ID:** TC-01
**Location:** `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py:71-107`, `simulation_adapter.py:269-271`
**Issue:** The regression test `test_resolve_battle_threads_injected_registries` verifies that `fresh_registries` reaches `run_battle.registry_provider` (identity check at line 104), but does NOT verify that the same registries reach `_instances_to_ships` (line 270). The test mocks `run_battle` entirely, returning a pre-built outcome — so `_instances_to_ships` is called during the test but its `registries` argument is never asserted. A future change that routes registries to `run_battle` but drops them for post-battle ship conversion would pass this test.

**Impact:** The regression test gives false confidence. CQ-01 could reoccur (or a new variant introduced) without test detection.

**Recommendation:** Have `_MockShipInstance.to_ship()` capture the registries it receives:
```python
def to_ship(self, pos, team_id=0, *, registries):
    self._last_registries = registries
    ship = MagicMock()
    ship.instance_id = self.instance_id
    return ship
```
Then assert after the resolver call:
```python
for ship_instance in fleet1.ships + fleet2.ships:
    assert ship_instance._last_registries is fresh_registries
```
**Effort:** Simple

---

#### MAJOR: `_MockShipInstance.to_ship()` signature masks non-optional registries contract
**ID:** TC-02
**Location:** `tests/unit/strategy/adapters/test_simulation_adapter_registry_threading.py:31`
**Issue:** The mock method `to_ship(self, pos, team_id=0, registries=None)` declares `registries` as optional with a `None` default. The real `ShipInstance.to_ship()` at `game/strategy/data/ship_instance.py:684` declares `registries: 'GameRegistries'` (required, keyword-only, no default, no Optional). The mock's permissive signature means tests never catch `None`-passing bugs like CQ-01.

**Impact:** Test-fidelity gap. Tests verify behavior against a mock that is more lenient than the real implementation. This masks the crash risk identified in CQ-01.

**Recommendation:** Match the real signature: `to_ship(self, pos, team_id=0, *, registries)` (keyword-only, no default). Use `MagicMock()` for the registries value in tests where registries content doesn't matter. This also requires updating the test's `_make_outcome` to not trigger `to_ship` for the non-tested path, or providing valid registries.
**Effort:** Simple

---

#### MAJOR: `_build_spec` passes `Optional[GameRegistries]` to function requiring non-optional
**ID:** CQ-02
**Location:** `game/strategy/adapters/simulation_adapter.py:316-338` → `game/strategy/combat/spec_compiler.py:83`
**Issue:** `_build_spec()` declares `registries: Optional['GameRegistries']` (line 316) but passes it directly to `build_strategy_battle_spec(..., registries=registries, ...)` which has `registries: "GameRegistries"` (required, no default, line 83 of `spec_compiler.py`). Currently benign because the spec compiler discards it (`_ = registries` at line 138 — placeholder for Phase 2). Once Phase 2 activates, passing `None` will crash.

**Impact:** Latent type hole. If `build_strategy_battle_spec` ever actually uses `registries` (planned for Phase 2), callers passing `None` will experience runtime failure. Static type checkers flag this mismatch.

**Recommendation:** Either make `_build_spec` require non-optional `registries` (preferred — all current callers supply it), or add a precondition guard in `_build_spec`. Making it non-optional aligns the types with reality and prevents future callers from making the wrong assumption.
**Effort:** Simple

---

#### MINOR: Late import of private constant `_BRIEF_RUN_TICK_BUDGET` violates encapsulation
**ID:** CQ-03
**Location:** `game/strategy/adapters/simulation_adapter.py:172`
**Issue:** Imports the private name `_BRIEF_RUN_TICK_BUDGET` from `game.strategy.combat.spec_compiler`. Private names have no stability contract — the owner may rename or delete without considering external consumers.

**Impact:** A future refactor of `spec_compiler.py` that renames `_BRIEF_RUN_TICK_BUDGET` would break `simulation_adapter.py` with no warning.

**Recommendation:** Make the constant public (`BRIEF_RUN_TICK_BUDGET`) in `spec_compiler.py`, or duplicate it in the adapter (it is `_DEFAULT_ABSOLUTE_MAX_TICKS // 10` — trivially reproducible).
**Effort:** Simple

---

#### MINOR: `_instances_to_ships` return type uses `List[Any]` where `List['Ship']` is knowable
**ID:** CQ-04
**Location:** `game/strategy/adapters/simulation_adapter.py:444`
**Issue:** Method returns `-> List[Any]`, but always returns `Ship` objects (from `ShipInstance.to_ship()`). The `Any` annotation weakens downstream type checking for `BattleResult.team_survivors`.

**Impact:** Callers working with `BattleResult.team_survivors` lose type safety. Mypy strict-mode won't catch type misuse of returned ships.

**Recommendation:** Change return type to `List['Ship']` and add `from game.simulation.entities.ship import Ship` in the `TYPE_CHECKING` block.
**Effort:** Simple

---

#### MINOR: `IRegistryProvider` protocol missing `get_resource_catalog()` method
**ID:** AR-01
**Location:** `game/core/protocols/registry.py:7-37` (protocol), `game/simulation/battle_runner.py:??` (consumer calls `registry_provider.get_resource_catalog()`)
**Issue:** Code in `build_context_ship_builder` (battle_runner.py) calls `registry_provider.get_resource_catalog()`, but `IRegistryProvider` only defines 4 methods (`get_components`, `get_modifiers`, `get_vehicle_classes`, `get_resources`). `GameRegistries` adds `get_resource_catalog` as a 5th method (PROJ-211), so `IRegistryProvider` type narrowing cannot express this requirement. A strict protocol implementation would fail at runtime.

**Impact:** Low. All known implementations (`GameRegistries`, `DefaultRegistryProvider`, `TestRegistryProvider`) already have `get_resource_catalog()` via duck typing. The gap only affects hypothetical new implementations that strictly follow the written protocol.

**Recommendation:** Add `get_resource_catalog() -> Optional[ResourceCatalog]` to `IRegistryProvider` in `game/core/protocols/registry.py`.
**Effort:** Simple

---

#### INFO: `get_default_registry_provider()` import executes on every `_run_simulated_battle` call
**ID:** CQ-05
**Location:** `game/strategy/adapters/simulation_adapter.py:248`
**Issue:** `from game.core.registry import get_default_registry_provider` at line 248 is unconditional, adding a small fixed overhead to every battle. Could be moved inside the fallback branch.

**Impact:** Trivial. Module-level imports are cached after first execution. This is a micro-optimization opportunity, not a real concern.

**Recommendation:** Optionally defer the import to the fallback branch for conceptual clarity (imports only what's needed). Very low priority.
**Effort:** Simple

---

#### INFO: Architecture documentation cross-reference verified
**ID:** AR-02
**Location:** `game/strategy/adapters/simulation_adapter.py:26`
**Issue:** Observation only. `run_battle` import from `game.simulation.battle_runner` at line 26 is architecturally correct per the allowed dependency matrix (Strategy → Simulation). The module-level import is appropriate for a Strategy-layer adapter. PROJ-252's rule against `get_default_registry_provider()` in simulation code is not violated — the adapter is in the strategy layer, and PROJ-306 explicitly permits the boundary call.

**Impact:** None.
**Recommendation:** None needed.

---

## Agent Reports

- [Code Quality & Architecture Report](findings/code_quality_report.md)

## Scope Details

See [scope.md](scope.md) for the full scope definition.
