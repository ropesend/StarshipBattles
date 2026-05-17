"""Economy / demographics / race-registry slice (PROJ-309 sub-phase 3.7).

Owns the heaviest single read on the facade — `get_colony_demographic_view`,
~90 LOC — plus the lazy session-scoped race registry and the economy-config
resolver helper.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Optional

from game.strategy.facade.dto import ColonyDemographicView, SpeciesDemographicView

if TYPE_CHECKING:
    from game.core.protocols import IRaceRegistry
    from game.strategy.config.economy_config import EconomyConfig
    from game.strategy.facade.slices._facade_state import FacadeSessionState

logger = logging.getLogger(__name__)


class EconomySlice:
    """Demographics, economy config, and race registry."""

    __slots__ = ("_state",)

    def __init__(self, state: "FacadeSessionState") -> None:
        self._state = state

    # ------------------------------------------------------------------
    # Race registry (PROJ-287)
    # ------------------------------------------------------------------

    def get_race_registry(self) -> "IRaceRegistry":
        """Get the session-scoped race registry (PROJ-287).

        Returns a cached ``CachedRaceRegistry`` wrapping a ``RaceLibrary``.
        The registry is lazily constructed on first access and reused for
        the remainder of the session, so UI panels and formulas can resolve
        ``race_id -> RaceConfig`` without per-call filesystem reads.

        Callers that mutate races (e.g. the race editor on save) must call
        ``registry.invalidate(race_id)`` after a successful save to keep
        subsequent reads coherent.
        """
        if self._state.race_registry is None:
            from game.strategy.systems.race_library import (
                CachedRaceRegistry,
                RaceLibrary,
            )
            self._state.race_registry = CachedRaceRegistry(RaceLibrary())
        return self._state.race_registry

    # ------------------------------------------------------------------
    # Economy config
    # ------------------------------------------------------------------

    def resolve_economy_config(self) -> "EconomyConfig":
        """Pull the active EconomyConfig from the session, falling back to
        the module default.

        The session attribute is optional — older sessions may not carry it,
        in which case `get_default_economy_config` lazy-loads
        `data/economy.json`.
        """
        economy = getattr(self._state.session, "economy_config", None)
        if economy is not None:
            return economy
        # PROJ-292 m6: surface the silent fallback so a session that's
        # supposed to carry an explicit config but lost it (e.g. a
        # deserialization regression) generates a warning instead of
        # quietly swapping in defaults.
        logger.warning(
            "EconomySlice.resolve_economy_config: session has no economy_config; "
            "falling back to get_default_economy_config()",
        )
        from game.strategy.config.economy_config import get_default_economy_config
        return get_default_economy_config()

    # ------------------------------------------------------------------
    # Colony demographics (PROJ-288)
    # ------------------------------------------------------------------

    def get_colony_demographic_view(
        self, planet_id: int
    ) -> Optional[ColonyDemographicView]:
        """One-shot snapshot of a colony's per-species + per-resource state.

        Bundles everything a demographics-style UI panel needs (per-species
        habitability + happiness + projected growth + food slider state +
        per-resource harvest/upkeep/yard/net + total upkeep across the
        colony) into a single immutable DTO so consumers don't re-derive
        the math each frame.

        Returns ``None`` for unowned planets, missing planet ids, or
        species whose ``race_id`` cannot be resolved by the session
        ``IRaceRegistry`` (those species are silently dropped — UI can
        warn separately if it cares).

        See `docs/04_SERVICES.md` § PlanetEconomyProjector and PROJ-288
        design.md § 3 for the underlying contracts.
        """
        # Inline imports keep the facade's top-level import surface narrow,
        # mirroring the pattern used by the command-dispatch helpers and by
        # `get_race_registry` (PROJ-287).
        from game.strategy.formulas.colony_output import projected_growth_rate
        from game.strategy.formulas.habitability import calculate_habitability
        from game.strategy.services.planet_economy_projector import (
            PlanetEconomyProjector,
        )

        planet = self._state.get_planet_by_id(planet_id)
        if planet is None or planet.owner_id is None:
            return None

        race_registry = self.get_race_registry()
        economy = self.resolve_economy_config()
        registries = getattr(self._state.session, "registries", None)

        projector = PlanetEconomyProjector(
            registries=registries,
            economy_config=economy,
            race_registry=race_registry,
        )
        projections = projector.project(planet)

        species_views: list = []
        for pop in planet.populations:
            race_config = race_registry.get_race(pop.race_id)
            if race_config is None:
                # Save drift / typo: skip rather than crash. The projector's
                # habitability multiplier already excludes these species too.
                continue
            cfg = planet.get_species_config(pop.race_id)
            display_name = (
                getattr(race_config, "race_name", "")
                or getattr(race_config, "name", "")
                or pop.race_id
            )
            # FEAT-19 — pre-compute the surplus bonus on the DTO so the UI
            # formatter never needs an EconomyConfig in scope. Zero when
            # surplus <= 1.0 so callers can simply check `> 0` to decide
            # whether to render the conditional "Food surplus" line.
            surplus = cfg.last_food_surplus
            if surplus > 1.0:
                surplus_bonus = min(
                    economy.surplus_food_bonus_cap,
                    economy.surplus_food_bonus_per_x * (surplus - 1.0),
                )
            else:
                surplus_bonus = 0.0
            species_views.append(SpeciesDemographicView(
                race_id=pop.race_id,
                race_name=display_name,
                count=pop.count,
                habitability=calculate_habitability(planet, race_config),
                happiness=pop.happiness,
                growth_rate=projected_growth_rate(planet, pop, race_config, cfg),
                food_ratio=cfg.last_food_ratio,
                food_allocation=cfg.food_allocation,
                food_surplus=surplus,
                food_surplus_bonus=surplus_bonus,
            ))

        species_views.sort(key=lambda s: s.count, reverse=True)

        # Sum per-resource upkeep across species into the empire-aggregation
        # summary. Mirrors `OrganicsConsumptionEngine._process_colony` math.
        total_upkeep: dict = {}
        for pop in planet.populations:
            count = getattr(pop, "count", 0)
            if count <= 0:
                continue
            cfg = planet.get_species_config(pop.race_id)
            for resource_id, per_pop_rate in economy.population_consumption.items():
                total_upkeep[resource_id] = (
                    total_upkeep.get(resource_id, 0.0)
                    + count * cfg.food_allocation * per_pop_rate
                )

        return ColonyDemographicView(
            planet_id=planet.id,
            planet_name=planet.name,
            species=tuple(species_views),
            resource_projections=tuple(projections.values()),
            total_upkeep=total_upkeep,
        )
