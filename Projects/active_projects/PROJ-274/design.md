# PROJ-274: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.

## Initial Analysis

`run_battle(spec, ai_factory, ship_builder, ...)` accepts a `ship_builder` closure that each caller supplies. Six production + test forks exist:

| Caller | Closure | Strategy |
|--------|---------|---------|
| `game/app.py::start_battle._ship_builder` | `ShipInstance.to_ship(position, team_id, registries)` | Instance-backed |
| `combat_lab/services/test_execution_service.py:83,95` | `scenario._load_ship(ship_spec.design_id)` | Design-only |
| `combat_lab/services/scenario_run_helper.py:67` | Same — `scenario._load_ship(design_id)` | Design-only |
| `combat_lab/scenarios/templates.py:844` (ComparisonScenario) | Rolls its own with role-keyed registry | Design-only + role tracking |
| `tests/integration/simulation/test_three_team_battle.py` | Minimal stub returning unarmed ships | Test stub |
| `tests/integration/simulation/test_boundary_retreat.py` | Test stub | Test stub |
| `tests/performance/test_telemetry_overhead.py` | Test stub | Test stub |

The [battle_runner.py docstring L105-110](../../../game/simulation/battle_runner.py) openly acknowledges this as a Phase-1 transitional design.

The split is on ONE axis: does the caller have a `ShipInstance`?
- **Strategy + Battle Setup + `game/app.py`** — yes, pass instance.
- **Combat Lab** — no, synthesize from JSON design.
- **Tests** — usually minimal stubs.

## Swarm Findings Summary

### Architecture
- `ApplicationContext` (PROJ-258) manages 10 services with `get_default_xxx()` / `set_default_xxx()` pattern. Natural extension point.
- `BattleSpec` is a frozen dataclass (`game/simulation/battle_spec.py:164`). Adding fields requires `field(default=...)`.
- `ShipSpec` can't import `ShipInstance` from strategy layer — layer violation per `docs/01_ARCHITECTURE.md`. Must use loose typing (`Optional[Any]`).

### Key Patterns to Reuse
- **ApplicationContext DI** (pattern 4 in `docs/02_PATTERNS.md`): matches how all other services register.
- **Protocol + TypeGuard** (pattern 5): `IShipMaterializer` as `@runtime_checkable` protocol for 1:1 language mapping.
- **`materialize_spec_ships` helper** at `game/simulation/battle_runner.py:557` — existing shared helper that takes `ship_builder` and iterates over `BattleSpec`. Materializer slots in here.

### Dependencies & Risks
1. **Risk: ShipSpec immutability.** Adding `instance_ref: Optional[Any] = None` with a default preserves backwards compat. Frozen dataclass enforces post-construction immutability. Safe.
2. **Risk: Import cycle.** `ShipSpec` (simulation) cannot know about `ShipInstance` (strategy). Using `Optional[Any]` resolves this. Strategy compiler passes an instance; simulation layer never introspects it.
3. **Dependency: ComparisonScenario refactor (PROJ-277).** ComparisonScenario's ship_builder tracks roles via `self._role_to_ship_instance_id`. PROJ-277 refactors it entirely. For now, ComparisonScenario continues to pass explicit `ship_builder` override.
4. **Risk: Test-fixture breakage.** Tests stubbing ship creation assume the kwarg keeps working. Explicit decision: override kwarg is PRESERVED.

### Opportunities Discovered
- Combat Lab can switch materializer at startup (`set_default_ship_materializer(DesignOnlyMaterializer())`) instead of passing per-call — simpler config.

## Design Decisions

See [decisions.md](decisions.md).

## Interface Sketch

```python
# game/simulation/services/ship_materializer.py

from typing import Protocol, runtime_checkable, Optional, Any
from game.simulation.battle_spec import ShipSpec
from game.simulation.entities.ship import Ship
from game.core.registries import GameRegistries

@runtime_checkable
class IShipMaterializer(Protocol):
    def materialize(
        self,
        ship_spec: ShipSpec,
        team_id: int,
        registries: GameRegistries,
    ) -> Ship: ...


class InstanceBackedMaterializer:
    """For Strategy, Battle Setup, and game/app.py entry.
    Expects ship_spec.instance_ref to be a ShipInstance."""
    def materialize(self, ship_spec, team_id, registries):
        instance = ship_spec.instance_ref
        if instance is None:
            raise ValueError(
                f"InstanceBackedMaterializer requires ship_spec.instance_ref. "
                f"ship_spec.design_id={ship_spec.design_id!r}"
            )
        return instance.to_ship(
            position=ship_spec.spawn_position,
            team_id=team_id,
            registries=registries,
        )


class DesignOnlyMaterializer:
    """For Combat Lab scenarios — loads design JSON, synthesizes Ship
    without ShipInstance."""
    def __init__(self, design_loader=None):
        self._design_loader = design_loader or _default_design_loader

    def materialize(self, ship_spec, team_id, registries):
        design = self._design_loader(ship_spec.design_id)
        return _build_ship_from_design(design, ship_spec, team_id, registries)
```

`ApplicationContext` accessors follow the existing pattern:

```python
# game/context.py additions

_default_ship_materializer: Optional[IShipMaterializer] = None

def get_default_ship_materializer() -> IShipMaterializer:
    global _default_ship_materializer
    if _default_ship_materializer is None:
        _default_ship_materializer = InstanceBackedMaterializer()
    return _default_ship_materializer

def set_default_ship_materializer(materializer: Optional[IShipMaterializer]) -> None:
    global _default_ship_materializer
    _default_ship_materializer = materializer
```

## `run_battle` Signature Evolution

```python
# Before
def run_battle(spec, *, ai_factory, ship_builder, per_tick_callback=None, ...):

# After
def run_battle(spec, *, ai_factory, ship_builder=None, per_tick_callback=None, ...):
    if ship_builder is None:
        materializer = get_default_ship_materializer()
        ship_builder = lambda ship_spec, team_id: materializer.materialize(
            ship_spec, team_id, registries
        )
    # ... existing implementation
```

## Caller Migrations

**`game/app.py::start_battle`:**
```python
# Before
def _ship_builder(ship_spec, team_id):
    return instance_ref.to_ship(ship_spec.spawn_position, team_id, registries)
controller.start_from_spec(spec, ai_factory=..., ship_builder=_ship_builder)

# After
controller.start_from_spec(spec, ai_factory=...)
# (ship_spec.instance_ref set by strategy compiler; materializer picks it up)
```

**Combat Lab:**
```python
# Once at service init:
set_default_ship_materializer(DesignOnlyMaterializer())

# Per test:
run_battle(spec, ai_factory=...)
```

**Tests:** keep explicit `ship_builder=...` overrides.
