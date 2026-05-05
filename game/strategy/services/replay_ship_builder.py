"""PROJ-354B audit remediation (AR-001) — Replay ship-builder factory.

Moved out of ``game/simulation/replay/replay_player.py`` because the
materializer needs ``ShipInstanceSerializer`` (Strategy layer), and a
Simulation-layer module must not import from Strategy. The builder
factory legitimately lives in Strategy because:

  * It bridges the persisted ``ShipInstance`` snapshot (Strategy data)
    to a live ``Ship`` (Simulation entity).
  * The coordinator (also Strategy) is the only production caller; it
    passes the resulting builder closure into Simulation's
    ``run_replay_headless`` via DI.

The closure executes during a Simulation ``run_battle`` call, but at
construction time the dependency direction is Strategy → Simulation,
which respects the layer rules in ``docs/01_ARCHITECTURE.md``.

The Simulation-side ``run_replay_headless`` and ``replay_record_to_spec``
remain in their original location.
"""
from __future__ import annotations

from typing import Callable, Optional, TYPE_CHECKING

from game.core.math import Vector2
from game.core.registry import GameRegistries
from game.simulation.battle_spec import ShipSpec
from game.simulation.replay.replay_record import ReplayRecord
from game.strategy.data.ship_instance_serializer import ShipInstanceSerializer

if TYPE_CHECKING:
    from game.core.protocols import IRegistryProvider
    from game.simulation.entities.ship import Ship


def build_replay_ship_builder(
    record: ReplayRecord,
    *,
    registry_provider: "IRegistryProvider",
    fallback_builder: Optional[Callable[[ShipSpec, int], "Ship"]] = None,
) -> Callable[[ShipSpec, int], "Ship"]:
    """Build a ``ship_builder`` closure that materializes ships from the
    captured ``ShipInstance`` snapshots in the record.

    For each ``ShipSpec`` (matched by ``instance_id``), looks up the
    corresponding ``instance_snapshot`` blob in the record and rebuilds a
    live ``ShipInstance`` via ``ShipInstanceSerializer.from_dict``, then
    converts it to a ``Ship`` via the strategy bridge.

    ``registry_provider`` is REQUIRED (PROJ-306 / PROJ-252: simulation
    code never resolves the registry provider via global lookup —
    callers in the strategy / UI / Combat Lab layers supply it).

    When a snapshot is unavailable (Combat Lab / synthetic captures) and a
    ``fallback_builder`` is supplied, the fallback is used. If neither
    is available, a ``ValueError`` is raised.
    """
    snapshots = dict(record.spec.iter_ship_snapshots())
    # PROJ-366 Phase 0 (CRIT, Codex r001): the IRegistryProvider protocol
    # has no `get_registries()` method — only individual getters. Mirror
    # `build_context_ship_builder` (battle_runner.py:240-247) and construct
    # the GameRegistries DTO from the protocol's individual getters.
    registries = GameRegistries(
        components=registry_provider.get_components(),
        modifiers=registry_provider.get_modifiers(),
        vehicle_classes=registry_provider.get_vehicle_classes(),
        resources=registry_provider.get_resources(),
        resource_catalog=registry_provider.get_resource_catalog(),
    )

    def _builder(ship_spec: ShipSpec, team_id: int) -> "Ship":
        snapshot = snapshots.get(ship_spec.instance_id)
        if snapshot is not None:
            instance = ShipInstanceSerializer.from_dict(snapshot)
            position = Vector2(ship_spec.position.x, ship_spec.position.y)
            return instance.to_ship(position, team_id, registries)
        if fallback_builder is not None:
            return fallback_builder(ship_spec, team_id)
        raise ValueError(
            f"replay ship_builder: no instance snapshot for {ship_spec.instance_id} "
            "and no fallback_builder supplied"
        )

    return _builder


__all__ = ["build_replay_ship_builder"]
