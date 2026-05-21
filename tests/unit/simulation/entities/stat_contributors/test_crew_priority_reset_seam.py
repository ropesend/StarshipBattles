"""PROJ-471 Task 3.4 -- reset seam for CREW_PRIORITY_REGISTRY.

Mirrors the sibling ``reset_stat_contributor_registry()`` test seam so tests
that register/unregister crew priorities can restore the canonical defaults.
"""

from game.simulation.entities.stat_contributors import registry as reg


def test_reset_restores_default_entries():
    reg.register_crew_priority("Proj471ProbeAbility", 5)
    assert any(
        e.ability_name == "Proj471ProbeAbility" for e in reg.CREW_PRIORITY_REGISTRY
    )

    reg.reset_crew_priority_registry()

    names = [e.ability_name for e in reg.CREW_PRIORITY_REGISTRY]
    assert "Proj471ProbeAbility" not in names
    # Canonical defaults restored.
    assert names == [
        "CommandAndControl",
        "CombatPropulsion",
        "ManeuveringThruster",
        "WeaponAbility",
    ]


def test_reset_recovers_from_unregister():
    reg.unregister_crew_priority("WeaponAbility")
    assert all(e.ability_name != "WeaponAbility" for e in reg.CREW_PRIORITY_REGISTRY)

    reg.reset_crew_priority_registry()

    assert any(e.ability_name == "WeaponAbility" for e in reg.CREW_PRIORITY_REGISTRY)
