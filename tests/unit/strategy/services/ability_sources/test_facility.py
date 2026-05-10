"""Tests for FacilityAbilitySource (PROJ-300 Phase 3)."""
from dataclasses import dataclass, field
from types import SimpleNamespace
from typing import Any, Dict, List

from game.core.protocols import IAbilitySource, is_ability_source
from game.strategy.services.ability_sources import FacilityAbilitySource


@dataclass
class _MockFacility:
    instance_id: str = "fac-1"
    name: str = "Geologic Stabilizer"
    is_operational: bool = True
    design_data: Dict[str, Any] = field(default_factory=dict)
    activation_states: Dict[str, Any] = field(default_factory=dict)

    def get_activation_state(self, comp_key: str) -> Any:
        return self.activation_states.get(comp_key)


@dataclass
class _MockPlanet:
    name: str = "Tarsis IV"
    owner_id: int = 1


def _facility_with_components(components: List[Dict[str, Any]]) -> _MockFacility:
    """Construct a facility with one CORE layer holding the given component dicts."""
    return _MockFacility(design_data={
        "layers": {
            "CORE": components,
        },
    })


def test_source_kind_is_facility():
    fac = _facility_with_components([])
    src = FacilityAbilitySource(facility=fac, planet=_MockPlanet())
    assert src.source_kind == 'facility'


def test_source_label_combines_facility_and_planet_name():
    fac = _MockFacility(name="Geologic Stabilizer")
    src = FacilityAbilitySource(facility=fac, planet=_MockPlanet(name="Tarsis IV"))
    assert src.source_label == "Geologic Stabilizer (Tarsis IV)"


def test_source_id_uses_instance_id():
    fac = _MockFacility(instance_id="fac-uuid-42")
    src = FacilityAbilitySource(facility=fac, planet=_MockPlanet())
    assert src.source_id == "facility:fac-uuid-42"


def test_owner_id_from_planet():
    src = FacilityAbilitySource(
        facility=_MockFacility(), planet=_MockPlanet(owner_id=7)
    )
    assert src.owner_id == 7


def test_get_abilities_returns_empty_when_not_operational():
    fac = _facility_with_components([
        {"id": "geologic_stabilizer_system",
         "abilities": {"GeologicStabilizer": {"scope": "sector"}}},
    ])
    fac.is_operational = False
    src = FacilityAbilitySource(facility=fac, planet=_MockPlanet())
    assert src.get_abilities() == {}


def test_get_abilities_walks_components():
    fac = _facility_with_components([
        {"id": "geologic_stabilizer_system",
         "abilities": {"GeologicStabilizer": {"scope": "sector"}}},
        {"id": "harvest_booster_system",
         "abilities": {"ResourceHarvestBooster": {"multiplier": 1.5, "resource_type": "metals", "scope": "sector"}}},
    ])
    src = FacilityAbilitySource(facility=fac, planet=_MockPlanet())
    abilities = src.get_abilities()
    assert "GeologicStabilizer" in abilities
    assert "ResourceHarvestBooster" in abilities


def test_get_abilities_lists_collisions():
    """Two components both declaring ShieldModifier yield list-valued shape."""
    fac = _facility_with_components([
        {"id": "shield_a", "abilities": {"ShieldModifier": {"multiplier": 0.9, "scope": "sector"}}},
        {"id": "shield_b", "abilities": {"ShieldModifier": {"multiplier": 0.8, "scope": "sector"}}},
    ])
    src = FacilityAbilitySource(facility=fac, planet=_MockPlanet())
    abilities = src.get_abilities()
    assert isinstance(abilities["ShieldModifier"], list)
    assert len(abilities["ShieldModifier"]) == 2


def test_get_activation_state_returns_first_owning_component_state():
    fac = _facility_with_components([
        {"id": "booster", "abilities": {"ResourceHarvestBooster": {"multiplier": 1.5}}},
        {"id": "shield", "abilities": {"PlanetaryShield": {"capacity": 100}}},
    ])
    fac.activation_states["CORE:1:shield"] = {"active": True}

    src = FacilityAbilitySource(facility=fac, planet=_MockPlanet())

    assert src.get_activation_state("PlanetaryShield") == {"active": True}


def test_get_activation_state_returns_none_without_state_getter():
    facility = SimpleNamespace(
        design_data={
            "layers": {
                "CORE": [
                    {"id": "shield", "abilities": {"PlanetaryShield": {"capacity": 100}}},
                ],
            },
        }
    )
    src = FacilityAbilitySource(facility=facility, planet=_MockPlanet())

    assert src.get_activation_state("PlanetaryShield") is None


def test_get_activation_state_returns_none_when_ability_missing():
    fac = _facility_with_components([
        {"id": "booster", "abilities": {"ResourceHarvestBooster": {"multiplier": 1.5}}},
    ])
    src = FacilityAbilitySource(facility=fac, planet=_MockPlanet())

    assert src.get_activation_state("PlanetaryShield") is None


def test_satisfies_iability_source_protocol():
    fac = _facility_with_components([])
    src = FacilityAbilitySource(facility=fac, planet=_MockPlanet())
    assert isinstance(src, IAbilitySource)
    assert is_ability_source(src)
