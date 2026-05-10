# PROJ-351 Architecture Analysis

## 1. IRegistryProvider public signature
**File:** `game/core/protocols/registry.py:7-39` — runtime-checkable Protocol with four methods:
- `get_components() -> Dict[str, Any]`
- `get_modifiers() -> Dict[str, Any]`
- `get_vehicle_classes() -> Dict[str, Any]`
- `get_resources() -> Dict[str, Any]`

## 2. Existing GameRegistries → IRegistryProvider adapter
**No adapter class exists, and none is needed.** `GameRegistries` itself implements the protocol per PROJ-211 (`game/core/registry.py:66-112`), exposing the four methods as pass-throughs at lines 93-107. GameRegistries IS already an IRegistryProvider.

## 3. run_battle signature
**File:** `game/simulation/battle_runner.py:255-265`
```python
def run_battle(
    spec: BattleSpec,
    *,
    ai_factory: "IAIControllerFactory",
    ship_builder: Optional[Callable[[ShipSpec, int], "Ship"]] = None,
    registry_provider: Optional["IRegistryProvider"] = None,
    ...
) -> BattleOutcome:
```
Per docstring (lines 277-281): `registry_provider` is required when `ship_builder is None`.

## 4. Adaptation triviality
Trivial — zero wrapper. GameRegistries already implements IRegistryProvider duck-typed and structurally. Evidence: `compute_components_registry_hash()` at `game/simulation/replay/replay_serialization.py:582` calls `registries.get_components()` directly, and `simulation_adapter._build_capture_context` (line 386) passes `registries` straight through with no conversion.

## 5. Layer-boundary check
Strategy may import IRegistryProvider directly. Strategy already imports `get_default_registry_provider` (`simulation_adapter.py:245`) and `GameRegistries` (line 34) from `game.core`. `game.core.protocols.registry` is part of the public protocols API; no policy comments forbid it.

## 6. Reusable adapters
None needed. `game/simulation/entities/ship_component_manager.py` and `game/simulation/services/vehicle_design_service.py` already pass `GameRegistries` directly where IRegistryProvider is expected (PROJ-252).

## Recommendation
Replace line 258 of `simulation_adapter.py`:
```python
# Before
registry_provider=get_default_registry_provider(),
# After
registry_provider=registries if registries is not None else get_default_registry_provider(),
```
No wrapper class, no new module. The fix is one line plus a regression test.
