from dataclasses import FrozenInstanceError
from types import SimpleNamespace

import pytest

from game.strategy.facade.dto.build_queue_dto import BuildQueueSourceDTO


def _source(owner: object) -> SimpleNamespace:
    return SimpleNamespace(
        queue_id="planet_7_base",
        display_name="Rigel - Planetary Yard",
        owner_entity=owner,
        construction_queue=[
            {
                "design_id": "mining_complex",
                "total_cost": {"metals": 50},
                "resources_consumed": {"metals": 10},
            }
        ],
        can_build_ships=False,
        can_build_complexes=True,
        context_type="planet",
        build_rate={"metals": 2000.0},
        planet_id=7,
    )


def test_from_domain_copies_source_fields_and_owner_metadata() -> None:
    source = _source(SimpleNamespace(id=7, owner_id=2))

    dto = BuildQueueSourceDTO.from_domain(source)

    assert dto.queue_id == "planet_7_base"
    assert dto.display_name == "Rigel - Planetary Yard"
    assert dto.entity_id == 7
    assert dto.can_build_ships is False
    assert dto.can_build_complexes is True
    assert dto.context_type == "planet"
    assert dto.planet_id == 7
    assert dto.empire_id == 2


def test_from_domain_detaches_queue_items_and_build_rate() -> None:
    source = _source(SimpleNamespace(id=7, owner_id=2))

    dto = BuildQueueSourceDTO.from_domain(source)
    source.construction_queue[0]["resources_consumed"]["metals"] = 49
    source.build_rate["metals"] = 1.0

    assert dto.construction_queue == [
        {
            "design_id": "mining_complex",
            "total_cost": {"metals": 50},
            "resources_consumed": {"metals": 10},
        }
    ]
    assert dto.build_rate == {"metals": 2000.0}


def test_from_domain_defaults_missing_owner_metadata() -> None:
    dto = BuildQueueSourceDTO.from_domain(_source(SimpleNamespace()))

    assert dto.entity_id == 0
    assert dto.empire_id is None


def test_build_queue_source_dto_is_frozen() -> None:
    dto = BuildQueueSourceDTO.from_domain(_source(SimpleNamespace(id=7)))

    with pytest.raises(FrozenInstanceError):
        dto.queue_id = "changed"
