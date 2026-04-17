"""Ship materialization service (PROJ-274).

Protocol + two production implementations that consolidate the six-way
`ship_builder` closure proliferation catalogued in the combat-system
review (2026-04-16). Before PROJ-274, every caller of
`run_battle(spec, ship_builder=...)` rolled its own closure to turn a
`ShipSpec` into a `Ship`. This module consolidates that into a single
`IShipMaterializer` protocol with two implementations:

- `InstanceBackedMaterializer` — for Strategy, Battle Setup, and
  `game/app.py::start_battle`. Reads `ship_spec.instance_ref` (a
  `ShipInstance` from the strategy layer) and calls its `to_ship`
  method.
- `DesignOnlyMaterializer` — for Combat Lab scenarios. Loads a ship
  design JSON by `ship_spec.design_id` via an injected loader and
  constructs a `Ship` via `Ship.from_dict`.

The protocol is consumed by:
- `ApplicationContext` (PROJ-274 Phase 4) via
  `get_default_ship_materializer()` / `set_default_ship_materializer()`.
- `run_battle(spec, ship_builder=None)` (PROJ-274 Phase 5): when
  `ship_builder` is None, pull the default materializer from context.

Test-override escape hatch: the `ship_builder` kwarg stays on
`run_battle` / `BattleController.start_from_spec` so tests can inject
stubs without touching the ApplicationContext. Production code does
not pass a closure — it relies on the default materializer.

Layer note: `ShipSpec.instance_ref` is typed `Optional[Any]` because the
simulation layer cannot import `ShipInstance` from the strategy layer
(layer violation per `docs/01_ARCHITECTURE.md`). The
InstanceBackedMaterializer uses duck typing (`instance.to_ship(...)`).
"""
from __future__ import annotations

from typing import Any, Callable, Dict, Optional, Protocol, runtime_checkable, TYPE_CHECKING

if TYPE_CHECKING:
    from game.core.registry import GameRegistries
    from game.simulation.battle_spec import ShipSpec
    from game.simulation.entities.ship import Ship


# Type of a loader function: design_id (str) -> design dict (loaded JSON).
DesignLoader = Callable[[str], Dict[str, Any]]


@runtime_checkable
class IShipMaterializer(Protocol):
    """Protocol for turning a `ShipSpec` into a `Ship`.

    Implementations differ in HOW they construct the Ship — from a
    strategy `ShipInstance` (InstanceBackedMaterializer) or from a
    design JSON file (DesignOnlyMaterializer). `materialize_spec_ships`
    handles position/angle/velocity/instance_id/components application
    AFTER this returns, so implementations don't need to set pose.
    """

    def materialize(
        self,
        ship_spec: "ShipSpec",
        team_id: int,
        registries: "GameRegistries",
    ) -> "Ship":
        """Construct a Ship for the given spec and team_id.

        Args:
            ship_spec: The `ShipSpec` whose Ship should be built.
            team_id: Engine team_id (mirrored from the enclosing
                `TeamSpec.team_id`). Some implementations thread it
                into `ShipInstance.to_ship(team_id, ...)`.
            registries: GameRegistries bundle for construction.

        Returns:
            A live `Ship`. Pose application is the caller's job via
            `materialize_spec_ships` — this method only needs to
            return a Ship with the correct design/components/layers.
        """
        ...


class InstanceBackedMaterializer:
    """Materialize a Ship from a strategy-layer `ShipInstance`.

    Used by Strategy, Battle Setup, and `game/app.py::start_battle` —
    every caller that already has a `ShipInstance` populated with
    component HP, resource levels, and toggle state.

    The caller sets `ship_spec.instance_ref` to the `ShipInstance`
    before compiling. If `instance_ref` is None, `materialize` raises
    `ValueError` — this materializer is specifically for instance-backed
    flows; design-only callers should use `DesignOnlyMaterializer`.
    """

    def materialize(
        self,
        ship_spec: "ShipSpec",
        team_id: int,
        registries: "GameRegistries",
    ) -> "Ship":
        instance = getattr(ship_spec, "instance_ref", None)
        if instance is None:
            raise ValueError(
                "InstanceBackedMaterializer requires ship_spec.instance_ref. "
                f"ship_spec.design_id={ship_spec.design_id!r} "
                f"(design-only callers must use DesignOnlyMaterializer instead)."
            )
        # `materialize_spec_ships` (game/simulation/battle_runner.py:128-133)
        # overwrites pose/velocity/instance_id/components AFTER ship_builder
        # returns, so the position passed into `to_ship` is effectively
        # throwaway. Passing the spec position anyway keeps `to_ship`'s
        # contract happy and mirrors the existing app.py closure.
        position = (ship_spec.position.x, ship_spec.position.y)
        return instance.to_ship(
            position,
            team_id,
            registries=registries,
        )


class DesignOnlyMaterializer:
    """Materialize a Ship from a design JSON without a ShipInstance.

    Used by Combat Lab scenarios — each scenario selects a design by
    filename (stored on `ShipSpec.design_id`), and the loader turns
    that into a parsed dict that `Ship.from_dict` consumes.

    The loader is injected so that tests + Combat Lab can set their
    own roots (simulation layer cannot import from combat_lab). Combat
    Lab's service startup configures this via
    `set_default_ship_materializer(DesignOnlyMaterializer(loader=...))`
    before running any test.

    Construction without a loader is allowed (so a default instance
    can exist in context); invoking `materialize` without one raises
    `RuntimeError` with guidance.
    """

    def __init__(self, design_loader: Optional[DesignLoader] = None) -> None:
        self._design_loader = design_loader

    def materialize(
        self,
        ship_spec: "ShipSpec",
        team_id: int,
        registries: "GameRegistries",
    ) -> "Ship":
        if self._design_loader is None:
            raise RuntimeError(
                "DesignOnlyMaterializer has no design_loader configured. "
                "Inject one at construction: "
                "`DesignOnlyMaterializer(design_loader=my_loader)`. "
                "Combat Lab normally sets this via "
                "`set_default_ship_materializer(DesignOnlyMaterializer(loader=...))` "
                "at service init."
            )
        data = self._design_loader(ship_spec.design_id)
        # Late import avoids an import-time cycle: ship_materializer
        # lives in simulation.services; Ship imports from simulation.entities.
        from game.simulation.entities.ship import Ship
        ship = Ship.from_dict(data, registries=registries)
        ship.recalculate_stats()
        return ship


# ---------------------------------------------------------------------------
# Module-level default (PROJ-258 context pattern)
# ---------------------------------------------------------------------------

# The default materializer for production. `run_battle` and
# `BattleController.start_from_spec` pull from this when no explicit
# `ship_builder` kwarg is provided (PROJ-274 Phase 5). Combat Lab calls
# `set_default_ship_materializer(DesignOnlyMaterializer(loader=...))`
# at service init to override (PROJ-274 Phase 6). Tests that need
# isolation can `set_default_ship_materializer(None)` or inject a
# custom instance.
_default_ship_materializer: Optional[IShipMaterializer] = None


def get_default_ship_materializer() -> IShipMaterializer:
    """Get the module-level default ship materializer.

    Lazy-initializes to `InstanceBackedMaterializer()` on first access
    if no override has been set — production default, used by Strategy,
    Battle Setup, and `game/app.py`.
    """
    global _default_ship_materializer
    if _default_ship_materializer is None:
        _default_ship_materializer = InstanceBackedMaterializer()
    return _default_ship_materializer


def set_default_ship_materializer(
    materializer: Optional[IShipMaterializer],
) -> None:
    """Set the module-level default ship materializer.

    Passing `None` clears the override — the next `get_default_ship_materializer()`
    call will lazy-init a fresh `InstanceBackedMaterializer`. Useful for
    Combat Lab cleanup (restoring production default on exit) and for
    tests that need a clean slate.
    """
    global _default_ship_materializer
    _default_ship_materializer = materializer


__all__ = [
    "DesignLoader",
    "IShipMaterializer",
    "InstanceBackedMaterializer",
    "DesignOnlyMaterializer",
    "get_default_ship_materializer",
    "set_default_ship_materializer",
]
