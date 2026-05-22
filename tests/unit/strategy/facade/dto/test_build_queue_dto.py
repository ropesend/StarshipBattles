from dataclasses import FrozenInstanceError
from types import SimpleNamespace

import pytest

from game.core.hex_math import HexCoord
from game.strategy.facade.dto.build_queue_dto import BuildQueueSourceDTO


def _source(owner: object, *, is_paused: bool = False) -> SimpleNamespace:
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
        is_paused=is_paused,
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


# --- PROJ-472 1B.1: enriched owner-derived scalars + is_paused ---


def test_from_domain_carries_is_paused() -> None:
    paused = BuildQueueSourceDTO.from_domain(
        _source(SimpleNamespace(id=7, owner_id=2), is_paused=True)
    )
    unpaused = BuildQueueSourceDTO.from_domain(
        _source(SimpleNamespace(id=7, owner_id=2), is_paused=False)
    )

    assert paused.is_paused is True
    assert unpaused.is_paused is False


def test_from_domain_defaults_owner_scalars_to_none() -> None:
    dto = BuildQueueSourceDTO.from_domain(_source(SimpleNamespace(id=7, owner_id=2)))

    assert dto.owner_global_hex is None
    assert dto.owner_system_name is None


def test_from_domain_accepts_resolved_owner_scalars() -> None:
    hex_coord = HexCoord(4, 5)
    dto = BuildQueueSourceDTO.from_domain(
        _source(SimpleNamespace(id=7, owner_id=2)),
        owner_global_hex=hex_coord,
        owner_system_name="Rigel",
    )

    assert dto.owner_global_hex == hex_coord
    assert dto.owner_system_name == "Rigel"


def test_owner_scalars_are_immutable_value_types() -> None:
    dto = BuildQueueSourceDTO.from_domain(
        _source(SimpleNamespace(id=7, owner_id=2)),
        owner_global_hex=HexCoord(1, 1),
        owner_system_name="Sol",
    )

    with pytest.raises(FrozenInstanceError):
        dto.owner_global_hex = HexCoord(9, 9)
    with pytest.raises(FrozenInstanceError):
        dto.owner_system_name = "Other"
