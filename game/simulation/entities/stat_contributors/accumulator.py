"""
Typed Phase-3 stat accumulator (PROJ-367 Phase 3, closes EXT-13).

Replaces the legacy ``acc: Dict[str, Any]`` accumulator with a
``StatAccumulator`` dataclass of 10 scalar fields + 4 named map fields = 14
total. Misspelled scalar/map field names raise ``AttributeError`` at runtime
(``slots=True`` semantics — Python 3.13+ enforces this).

Dynamic resource keys (``max_<resource>``, ``gen_<resource>``) live INSIDE
the ``resource_storage`` / ``resource_generation`` map fields because
resource types are data-driven (``ship_stats.py:_aggregate_resource_abilities``
discovers them at runtime). Promoting them to flat dataclass fields would
contradict the data-driven invariant.

This module is a SIBLING of ``registry.py`` so that ``registry.py`` does
not push past the 500 LOC ceiling. Production contributors import the
class directly from
``game.simulation.entities.stat_contributors.accumulator`` (or from the
package via ``from stat_contributors import accumulator``).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict


@dataclass(slots=True)
class StatAccumulator:
    """Typed mutation surface for Phase-3 stat contributors.

    Field roles:

    - ``thrust`` — sum of CombatPropulsion.thrust_force across operational
      components (movement domain, written by
      ``movement.contribute_combat_propulsion``).
    - ``strategic_movement`` — sum of StrategicMovement.movement_points
      (movement domain).
    - ``turn_speed`` — sum of ManeuveringThruster.turn_rate; the calculator
      divides by ``mass^1.5`` in Phase 4 (movement domain).
    - ``maneuver_points`` — sum of ManeuveringThruster.turn_rate, untouched
      by physics (raw turning capability).
    - ``max_shields`` — sum of ShieldProjection.capacity (defense domain).
    - ``shield_regen`` — sum of ShieldRegeneration.rate (defense domain).
    - ``shield_cost`` — first-match ResourceConsumption(energy).amount on a
      ShieldRegeneration-bearing component (defense domain).
    - ``warp_max_tonnage`` — max over WarpJump.max_tonnage (movement domain).
    - ``warp_energy_cost`` — sum of WarpJump.energy_cost (movement domain).
    - ``pod_storage_mass`` — sum of PodStorageAbility.capacity_mass (read in
      ``ship_stats._aggregate_cargo_and_pod_abilities``).
    - ``warp_resource_costs`` — per-resource costs read from
      ResourceConsumption(trigger='warp_jump') instances.
    - ``cargo_storage`` — per-cargo-type capacity from CargoStorage.
    - ``resource_storage`` — per-resource maximum capacity from
      ResourceStorage instances. Replaces synthetic ``max_<resource>`` keys.
    - ``resource_generation`` — per-resource generation rate from
      ResourceGeneration instances. Replaces synthetic ``gen_<resource>`` keys.

    Modder contract:

    A modder-registered contributor receives a live ``StatAccumulator``
    instance and may read/write the 14 named fields. Misspelled scalar/map
    field names raise ``AttributeError`` at the modder's first test run.
    Resource-type strings inside ``resource_storage`` /
    ``resource_generation`` still flow through dicts; misspelled types
    produce zero (same as today, but the surface area for typos is
    much smaller).
    """

    # Scalar fields (10) — direct attribute access, defaults are
    # zero-of-the-correct-type.
    thrust: float = 0.0
    strategic_movement: int = 0
    turn_speed: float = 0.0
    maneuver_points: float = 0.0
    max_shields: float = 0.0
    shield_regen: float = 0.0
    shield_cost: float = 0.0
    warp_max_tonnage: float = 0.0
    warp_energy_cost: float = 0.0
    pod_storage_mass: float = 0.0

    # Named map fields (4) — value-level dict access for data-driven keys.
    warp_resource_costs: Dict[str, float] = field(default_factory=dict)
    cargo_storage: Dict[str, float] = field(default_factory=dict)
    resource_storage: Dict[str, float] = field(default_factory=dict)
    resource_generation: Dict[str, float] = field(default_factory=dict)


__all__ = ["StatAccumulator"]
