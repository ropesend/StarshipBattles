"""Unified ability-source iterator (PROJ-300).

Yields `IAbilitySource` adapters for the queried hex/system. Source providers
register themselves via `register_source_provider`; PROJ-301..305 plug in by
adding one provider function each. The iterator is the integration seam —
adding a new source kind requires no central edits.

**Adapter rule (post-PROJ-306):** providers and adapters that touch ship/
component data take `registries` (or equivalent) via parameter injection.
Never call `get_default_registry_provider()` from inside a provider — see
PROJ-300 design.md task 4.5.
"""
from typing import Any, Callable, Iterable, List, Optional

from game.strategy.services.ability_sources import (
    FacilityAbilitySource,
    StormAbilitySource,
    PlanetIntrinsicAbilitySource,  # PROJ-301
    StarAbilitySource,  # PROJ-302
    WarpPointAbilitySource,  # PROJ-303
    SystemAbilitySource,  # PROJ-304
    FleetAbilitySource,  # PROJ-305
)


# Provider signature: callable taking (system, hex_coord, registries) and yielding
# IAbilitySource instances. hex_coord is None for system-wide queries.
ProviderFn = Callable[[Any, Any, Any], Iterable[Any]]


_HEX_PROVIDERS: List[ProviderFn] = []
_SYSTEM_PROVIDERS: List[ProviderFn] = []


def register_source_provider_at_hex(fn: ProviderFn) -> None:
    """Register a provider that yields sources affecting a specific hex."""
    if fn not in _HEX_PROVIDERS:
        _HEX_PROVIDERS.append(fn)


def register_source_provider_in_system(fn: ProviderFn) -> None:
    """Register a provider that yields sources affecting a system as a whole."""
    if fn not in _SYSTEM_PROVIDERS:
        _SYSTEM_PROVIDERS.append(fn)


def unregister_source_provider(fn: ProviderFn) -> None:
    """Remove a provider from BOTH hex and system lists (test-isolation helper)."""
    if fn in _HEX_PROVIDERS:
        _HEX_PROVIDERS.remove(fn)
    if fn in _SYSTEM_PROVIDERS:
        _SYSTEM_PROVIDERS.remove(fn)


def iter_ability_sources_at_hex(
    system: Any,
    hex_coord: Any,
    *,
    registries: Any = None,
    include_system_sources: bool = True,
) -> Iterable[Any]:
    """Yield every ability source whose abilities apply to the queried hex.

    Includes hex-located sources (storms here; planets/warp points/fleets in
    later projects) AND system-scope sources (facilities; later: stars,
    system archetype) when `include_system_sources=True`. Callers filter
    further by scope via `_SECTOR_SCOPES` / `_SYSTEM_SCOPES`.
    """
    seen_ids = set()
    for fn in _HEX_PROVIDERS:
        for source in fn(system, hex_coord, registries):
            sid = getattr(source, 'source_id', id(source))
            if sid in seen_ids:
                continue
            seen_ids.add(sid)
            yield source

    if include_system_sources:
        for fn in _SYSTEM_PROVIDERS:
            for source in fn(system, None, registries):
                sid = getattr(source, 'source_id', id(source))
                if sid in seen_ids:
                    continue
                seen_ids.add(sid)
                yield source


def iter_ability_sources_in_system(
    system: Any,
    *,
    registries: Any = None,
) -> Iterable[Any]:
    """Yield every ability source within the star system, regardless of hex."""
    seen_ids = set()
    for fn in _SYSTEM_PROVIDERS:
        for source in fn(system, None, registries):
            sid = getattr(source, 'source_id', id(source))
            if sid in seen_ids:
                continue
            seen_ids.add(sid)
            yield source
    # Hex providers also walk system-wide for system-effect collection: a star
    # at hex H projects system-scope abilities that apply at every hex of the
    # system. PROJ-302 will exercise this path.
    for fn in _HEX_PROVIDERS:
        for source in fn(system, None, registries):
            sid = getattr(source, 'source_id', id(source))
            if sid in seen_ids:
                continue
            seen_ids.add(sid)
            yield source


# ---------------------------------------------------------------------------
# Built-in providers (PROJ-300): facilities + storms.
# PROJ-301..305 add their own providers by importing the registration API
# from this module.
# ---------------------------------------------------------------------------


def _facility_provider(system: Any, hex_coord: Any, registries: Any) -> Iterable[Any]:
    """Yield FacilityAbilitySource for every operational facility in the system.

    `hex_coord=None` (system-wide query): yields every facility.
    `hex_coord=<HexCoord>` (hex query): yields facilities whose planet is at
    that hex. The collector then filters by scope.
    """
    if system is None:
        return
    planets = getattr(system, 'planets', None) or []
    for planet in planets:
        # Hex filter — when a specific hex is requested, only yield facilities
        # whose planet sits there. System-wide query: yield all.
        if hex_coord is not None:
            planet_hex = _planet_global_hex(planet, system)
            if planet_hex is None or planet_hex != hex_coord:
                continue
        facilities = getattr(planet, 'facilities', None) or []
        for facility in facilities:
            if not getattr(facility, 'is_operational', True):
                continue
            yield FacilityAbilitySource(
                facility=facility, planet=planet, registries=registries,
            )


def _storm_provider(system: Any, hex_coord: Any, registries: Any) -> Iterable[Any]:
    """Yield StormAbilitySource for every storm in the system that affects the hex.

    `hex_coord=None` (system-wide): yields all storms in the system.
    `hex_coord=<HexCoord>`: yields only storms covering it. The adapter
    translates local `storm.location + hex_offsets` into global coords via
    `system.global_location` so the GLOBAL hex passed by callers (UI sector
    panel) matches correctly. (BUG-119 regression — pre-fix the storm
    adapter compared frames naively and never matched.)
    """
    if system is None:
        return
    storms = getattr(system, 'storms', None) or []
    for storm in storms:
        adapter = StormAbilitySource(storm=storm, system=system)
        if hex_coord is None or adapter.affects_hex(hex_coord):
            yield adapter


def _planet_global_hex(planet: Any, system: Any) -> Optional[Any]:
    """Compute the global hex of a planet by adding its system's offset.

    Falls back to None if either side lacks the expected attributes; the
    caller treats None as "skip hex match".
    """
    planet_loc = getattr(planet, 'location', None)
    system_loc = getattr(system, 'global_location', None) or getattr(system, 'location', None)
    if planet_loc is None or system_loc is None:
        return None
    try:
        return system_loc + planet_loc
    except TypeError:
        return None


def _star_provider(system: Any, hex_coord: Any, registries: Any) -> Iterable[Any]:
    """PROJ-302: yield StarAbilitySource for stars with intrinsic abilities.

    For hex queries (hex_coord != None), yields a star source if EITHER the
    star is at the queried hex (sector-scope abilities can fire) OR the star
    declares system-scope abilities that apply at every hex of the system.
    The collector's scope filter narrows from there.
    """
    if system is None:
        return
    stars = getattr(system, 'stars', None) or []
    for star in stars:
        abilities = getattr(star, 'intrinsic_abilities', None)
        if not abilities:
            continue
        adapter = StarAbilitySource(star=star, system=system)
        if hex_coord is None:
            yield adapter
            continue
        # Sector-scope: star must be at the queried hex.
        if adapter.affects_hex(hex_coord):
            yield adapter
            continue
        # System-scope abilities: yield even when star isn't at this hex —
        # `_SECTOR_SCOPES` filtering at the collector still hides them from
        # sector queries, but `_SYSTEM_SCOPES` queries (or hex queries with
        # `include_system_sources=True`) need access to the source.
        for entry in abilities.values():
            entries = entry if isinstance(entry, list) else [entry]
            if any(e.get('scope') in {'system', 'allied_system', 'player_system', 'enemy_system'}
                   for e in entries if isinstance(e, dict)):
                yield adapter
                break


def _planet_intrinsic_provider(system: Any, hex_coord: Any, registries: Any) -> Iterable[Any]:
    """PROJ-301: yield PlanetIntrinsicAbilitySource for planets with abilities.

    `hex_coord=None` (system-wide query): every planet with intrinsic abilities.
    `hex_coord=<HexCoord>` (hex query): only planets whose global hex matches.
    """
    if system is None:
        return
    planets = getattr(system, 'planets', None) or []
    for planet in planets:
        if not getattr(planet, 'intrinsic_abilities', None):
            continue
        adapter = PlanetIntrinsicAbilitySource(planet=planet, system=system)
        if hex_coord is None or adapter.affects_hex(hex_coord):
            yield adapter


# PROJ-305 fleet lookup hook — set by the strategy session to provide
# fleets-at-hex / fleets-in-system queries. When None, the fleet provider
# yields nothing (safe no-op for tests + non-strategic contexts).
_FLEETS_AT_HEX_LOOKUP: Optional[Any] = None  # Callable[[system, hex_coord], Iterable[Fleet]]
_FLEETS_IN_SYSTEM_LOOKUP: Optional[Any] = None  # Callable[[system], Iterable[Fleet]]


def set_fleet_lookups(at_hex=None, in_system=None) -> None:
    """Configure the PROJ-305 fleet-lookup callbacks.

    The strategy session calls this at startup so the iterator can yield
    FleetAbilitySource for fleets at a queried hex / in a queried system.
    Without these callbacks, fleets are not surfaced (the rest of the
    framework keeps working).
    """
    global _FLEETS_AT_HEX_LOOKUP, _FLEETS_IN_SYSTEM_LOOKUP
    _FLEETS_AT_HEX_LOOKUP = at_hex
    _FLEETS_IN_SYSTEM_LOOKUP = in_system


def _fleet_provider(system: Any, hex_coord: Any, registries: Any) -> Iterable[Any]:
    """PROJ-305: yield FleetAbilitySource for fleets with strategic abilities.

    Requires `set_fleet_lookups` to have been configured by the strategy
    session. Without lookup callbacks, yields nothing.
    """
    if hex_coord is None:
        lookup = _FLEETS_IN_SYSTEM_LOOKUP
        fleets = lookup(system) if lookup else []
    else:
        lookup = _FLEETS_AT_HEX_LOOKUP
        fleets = lookup(system, hex_coord) if lookup else []
    for fleet in fleets:
        adapter = FleetAbilitySource(fleet=fleet, registries=registries)
        if adapter.get_abilities():
            yield adapter


def _system_archetype_provider(system: Any, hex_coord: Any, registries: Any) -> Iterable[Any]:
    """PROJ-304: yield SystemAbilitySource if the system has an archetype.

    Archetype abilities are all scope: system, so the source is yielded for
    every query (hex or system-wide); the collector's _SYSTEM_SCOPES filter
    ensures sector queries don't accidentally pick up system-scope abilities.
    """
    if system is None:
        return
    if not getattr(system, 'archetype', None):
        return
    if not getattr(system, 'intrinsic_abilities', None):
        return
    yield SystemAbilitySource(system=system)


def _warp_point_provider(system: Any, hex_coord: Any, registries: Any) -> Iterable[Any]:
    """PROJ-303: yield WarpPointAbilitySource for warp points with abilities."""
    if system is None:
        return
    warp_points = getattr(system, 'warp_points', None) or []
    for wp in warp_points:
        if not getattr(wp, 'intrinsic_abilities', None):
            continue
        adapter = WarpPointAbilitySource(warp_point=wp, system=system)
        if hex_coord is None or adapter.affects_hex(hex_coord):
            yield adapter


# Register the built-in providers at module load. PROJ-304..305 register their
# own additional providers from their own modules.
register_source_provider_at_hex(_facility_provider)
register_source_provider_at_hex(_storm_provider)
register_source_provider_at_hex(_planet_intrinsic_provider)
register_source_provider_at_hex(_star_provider)
register_source_provider_at_hex(_warp_point_provider)
register_source_provider_at_hex(_system_archetype_provider)
register_source_provider_at_hex(_fleet_provider)
register_source_provider_in_system(_facility_provider)
register_source_provider_in_system(_storm_provider)
register_source_provider_in_system(_planet_intrinsic_provider)
register_source_provider_in_system(_star_provider)
register_source_provider_in_system(_warp_point_provider)
register_source_provider_in_system(_system_archetype_provider)
register_source_provider_in_system(_fleet_provider)
