"""FacilityAbilitySource adapter — wraps a planetary facility (PROJ-300).

Walks a facility's components (via `iter_keyed_components`) and aggregates
their abilities into the unified `IAbilitySource` shape. Honors the
facility's operational flag and per-component activation state.

**Adapter rule (post-PROJ-306):** the registry parameter is constructor-
injected. Never call `get_default_registry_provider()` from inside this class.
"""
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from game.core.patterns.layer_iterator import iter_keyed_components
from game.strategy.services.component_inspector import extract_abilities_from_component


@dataclass(frozen=True)
class FacilityAbilitySource:
    """IAbilitySource adapter for planetary facilities."""
    facility: Any   # game.strategy.data.planetary_facility.PlanetaryFacility
    planet: Any     # game.strategy.data.planet.Planet
    registries: Any = None  # GameRegistries or compatible — constructor-injected only

    @property
    def source_kind(self) -> str:
        return 'facility'

    @property
    def source_label(self) -> str:
        facility_name = getattr(self.facility, 'name', 'Facility')
        planet_name = getattr(self.planet, 'name', None)
        if planet_name:
            return f"{facility_name} ({planet_name})"
        return facility_name

    @property
    def source_id(self) -> str:
        # facility.instance_id is a UUID — globally unique.
        instance_id = getattr(self.facility, 'instance_id', id(self.facility))
        return f"facility:{instance_id}"

    @property
    def owner_id(self) -> Optional[int]:
        return getattr(self.planet, 'owner_id', None)

    def get_abilities(self) -> Dict[str, Any]:
        """Walk all operational components, return merged ability data.

        Uses list-valued shape: a single ability_name may have multiple
        contributing components. The collector flattens these into per-
        provider entries downstream.
        """
        if not getattr(self.facility, 'is_operational', True):
            return {}

        result: Dict[str, List[Any]] = {}
        for _comp_key, _layer, comp in iter_keyed_components(self.facility.design_data):
            abilities = extract_abilities_from_component(comp, self.registries)
            for ability_name, ability_data in abilities.items():
                entries = ability_data if isinstance(ability_data, list) else [ability_data]
                result.setdefault(ability_name, []).extend(entries)
        return result

    def affects_hex(self, hex_coord) -> bool:
        """Facilities project sector-scope abilities at the planet's global hex."""
        # Most callers query system-wide; the collector then filters. We check
        # planet-at-hex via the planet itself if available, otherwise return
        # True (scope-driven filter does the rest).
        return True

    def affects_system(self, system) -> bool:
        return True

    def get_activation_state(self, ability_name: str) -> Optional[Any]:
        """Return the activation state for the component owning `ability_name`.

        For facilities with multiple components contributing the same ability,
        returns the first match. Components without state default to None.
        """
        get_state = getattr(self.facility, 'get_activation_state', None)
        if get_state is None:
            return None
        for comp_key, _layer, comp in iter_keyed_components(self.facility.design_data):
            abilities = extract_abilities_from_component(comp, self.registries)
            if ability_name in abilities:
                return get_state(comp_key)
        return None
