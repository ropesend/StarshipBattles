"""Contract test for the public API of game.core.protocols (PROJ-309 sub-phase 3.4).

The protocols module was decomposed from a single 1087-line file into a
package of domain-grouped sub-modules. This test asserts every public symbol
remains importable from `game.core.protocols` so callers — 132 imports across
80 files — keep working without churn.

The frozen golden list below was generated from the pre-split file. It is the
exhaustive public surface; do NOT trim it. Adding a new protocol to a sub-module
should also add it here AND to the package `__init__.py` re-exports.
"""

import pytest


PUBLIC_PROTOCOL_SYMBOLS = (
    # Registry (1)
    "IRegistryProvider",
    # Common base mixins (3)
    "ILocatable",
    "INamed",
    "IOwnable",
    # Strategy entities — protocol classes (10)
    "IStarSystem",
    "IStar",
    "IPlanet",
    "IOrderable",
    "IZoneOccupant",
    "IFleet",
    "IWarpPoint",
    "ISectorEnvironment",
    "IStorm",
    "IAbilitySource",  # PROJ-300
    # Strategy entities — TypeGuards (9)
    "is_star_system",
    "is_star",
    "is_planet",
    "is_fleet",
    "is_warp_point",
    "is_sector_environment",
    "is_storm",
    "is_zone_occupant",
    "is_ability_source",  # PROJ-300
    # Strategy domain — protocol classes (4)
    "IEmpire",
    "IFacility",
    "IRaceRegistry",
    "IShipInstance",
    # Strategy domain — TypeGuards (3)
    "is_empire",
    "is_facility",
    "is_ship_instance",
    # Combat — protocol classes (3)
    "ICombatant",
    "IDamageable",
    "ICombatShip",
    # Combat — TypeGuards (2)
    "is_combatant",
    "is_combat_ship",
    # UI — protocol classes (2)
    "IScene",
    "ICamera",
    # UI — TypeGuards (1)
    "is_camera",
    # Strategy↔Simulation boundary — protocol classes (3)
    "IResourceReader",
    "IPostBattleShip",
    "IResourceHolder",
    # Boundary — TypeGuards (3)
    "is_post_battle_ship",
    "is_resource_reader",
    "is_resource_holder",
    # Persistence (1)
    "ISerializable",
    # Strategy mutator protocols (PROJ-370) (4)
    "IFleetMutator",
    "IPlanetMutator",
    "IEmpireMutator",
    "IShipInstanceMutator",
)


PRIVATE_BUT_PUBLICLY_IMPORTED = (
    # Imported by simulation/interfaces and ai/protocols despite leading underscore.
    # See core_protocols_decomposition.md §"Public API surface" — must remain importable.
    "_has_attrs",
)


@pytest.mark.parametrize("symbol", PUBLIC_PROTOCOL_SYMBOLS)
def test_public_symbol_importable_from_package(symbol: str) -> None:
    """Every public Protocol/TypeGuard remains importable as `from game.core.protocols import X`."""
    import game.core.protocols as protocols

    assert hasattr(protocols, symbol), (
        f"Public symbol {symbol!r} is no longer exported from game.core.protocols. "
        "If you renamed or deleted it, callers will break — update PUBLIC_PROTOCOL_SYMBOLS "
        "and migrate every caller in the same commit."
    )


@pytest.mark.parametrize("symbol", PRIVATE_BUT_PUBLICLY_IMPORTED)
def test_private_but_imported_symbol_importable(symbol: str) -> None:
    """Leading-underscore helpers with cross-module callers must still re-export."""
    import game.core.protocols as protocols

    assert hasattr(protocols, symbol), (
        f"{symbol!r} is imported by simulation and ai code despite the underscore. "
        "It must remain importable from game.core.protocols."
    )


def test_full_count_matches_decomposition_design() -> None:
    """Symbol count matches the design doc (49 public + 1 private-but-public = 50 total).

    PROJ-300 added IAbilitySource + is_ability_source (45 = original 43 + 2).
    PROJ-370 added IFleetMutator/IPlanetMutator/IEmpireMutator/IShipInstanceMutator
    (49 = 45 + 4).
    """
    assert len(PUBLIC_PROTOCOL_SYMBOLS) == 49, (
        "If you added a new protocol or TypeGuard, update PUBLIC_PROTOCOL_SYMBOLS "
        "and the count here. PROJ-370 brought the count to 49."
    )
    assert len(PRIVATE_BUT_PUBLICLY_IMPORTED) == 1


def test_no_unexpected_protocol_symbols_leak() -> None:
    """Catch silent additions: anything starting with `I` or `is_` at module level
    should be in PUBLIC_PROTOCOL_SYMBOLS or be an internal helper.
    """
    import game.core.protocols as protocols

    surface = {
        name for name in dir(protocols)
        if (name.startswith("I") and name[1:2].isupper()) or name.startswith("is_")
    }
    expected = set(PUBLIC_PROTOCOL_SYMBOLS)
    leaked = surface - expected
    assert not leaked, (
        f"Found protocol-shaped symbols not declared in PUBLIC_PROTOCOL_SYMBOLS: {leaked}. "
        "Either add them to the golden list (intentional new public API) or move them "
        "to a private helper name (accidental leak)."
    )
