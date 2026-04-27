"""FleetAbilitySource — wraps a Fleet's strategic-layer component abilities (PROJ-305).

A flagship at hex H projects sector-scope abilities visible in the Sector
Effects panel for entities at H. Distinct from combat-only fleet auras
(`FleetAuraManager`) which handle scope: fleet/team during battle. This
adapter walks the fleet's ships' components and yields entries with
strategic-layer scopes (sector, system, allied_*, etc.) — combat-only
scopes (self/fleet/team) are filtered out.

Per decisions.md D11, cloaked fleets project no abilities (the safe default
for future stealth design). Per D12, FleetAbilitySource memoizes its
get_abilities() result per-instance — mid-turn fleet movement creates new
instances at the new hex, so the per-instance cache is the correct
granularity.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


# Strategic-layer scopes — these flow through FleetAbilitySource.
# Combat-only scopes (self, fleet, team) stay in FleetAuraManager.
_STRATEGIC_SCOPES = frozenset({
    'sector', 'allied_sector', 'enemy_sector', 'player_sector',
    'system', 'allied_system', 'enemy_system', 'player_system',
    'planet', 'empire', 'allied_empire',
})


@dataclass
class FleetAbilitySource:
    """IAbilitySource adapter for a Fleet's strategic-layer ship abilities.

    NOTE: Not frozen — needs an instance-mutable cache per D12. The cache is
    safe because adapter instances are short-lived (created during iteration,
    discarded after the query); each instance corresponds to one fleet at
    one hex at one moment.
    """
    fleet: Any  # game.strategy.data.fleet.Fleet
    registries: Any = None  # GameRegistries (constructor-injected per PROJ-306)
    _abilities_cache: Optional[Dict[str, Any]] = field(default=None, init=False, repr=False)

    @property
    def source_kind(self) -> str:
        return 'fleet'

    @property
    def source_label(self) -> str:
        # Prefer the fleet's display_name if set; fall back to "Fleet {id}".
        # Per decisions.md D5 we may also surface a flagship name; keeping it
        # simple here — display_name encodes the player-set label.
        owner = getattr(self.fleet, 'owner_id', '?')
        display = getattr(self.fleet, 'display_name', '')
        if display:
            return f"Fleet '{display}' (Player {owner})"
        return f"Fleet {getattr(self.fleet, 'id', '?')} (Player {owner})"

    @property
    def source_id(self) -> str:
        return f"fleet:{getattr(self.fleet, 'id', id(self.fleet))}"

    @property
    def owner_id(self) -> Optional[int]:
        return getattr(self.fleet, 'owner_id', None)

    def get_abilities(self) -> Dict[str, Any]:
        if self._abilities_cache is not None:
            return self._abilities_cache
        result: Dict[str, List[Any]] = {}
        ships = getattr(self.fleet, 'ships', None) or []
        for ship in ships:
            if not _is_combat_capable(ship):
                continue
            design_data = getattr(ship, 'design_data', None)
            if design_data is None:
                continue
            for ability_name, ability_data in _walk_strategic_abilities(design_data, self.registries):
                result.setdefault(ability_name, []).append(ability_data)
        # Hook for future stealth: cloaked fleets project nothing (D11).
        if _is_hidden(self.fleet):
            result = {}
        # Mutate via object.__setattr__ to bypass frozen-dataclass guard
        # if we ever switch to frozen=True later.
        object.__setattr__(self, '_abilities_cache', result)
        return result

    def affects_hex(self, hex_coord) -> bool:
        if _is_hidden(self.fleet):
            return False
        return getattr(self.fleet, 'location', None) == hex_coord

    def affects_system(self, system) -> bool:
        if _is_hidden(self.fleet):
            return False
        # We don't have a quick "is this fleet's hex inside this system" check
        # without the galaxy. Trust the iterator to call only on the right system.
        return True

    def get_activation_state(self, ability_name: str) -> Optional[Any]:
        # Per-component activation across many ships is complex; PROJ-305
        # treats fleet abilities as always-active. Per-component activation
        # is a follow-up.
        return None


def _is_combat_capable(ship: Any) -> bool:
    """Best-effort 'is this ship operational' check."""
    is_combat = getattr(ship, 'is_combat_capable', None)
    if callable(is_combat):
        try:
            return bool(is_combat())
        except Exception:  # Intentional broad catch: ship-impl errors don't poison iteration
            return False
    if isinstance(is_combat, bool):
        return is_combat
    # Default: include the ship.
    return True


def _is_hidden(fleet: Any) -> bool:
    """Hook for future stealth design (PROJ-305 D11).

    Returns True if the fleet is currently hidden (cloaked). PROJ-305 ships
    a baseline that never returns True; future stealth design flips this on.
    """
    return bool(getattr(fleet, 'is_hidden', False))


def _walk_strategic_abilities(design_data: Dict[str, Any], registries: Any):
    """Yield (ability_name, ability_data) pairs for strategic-scope abilities.

    Walks every component in the design's layers and extracts each ability
    via the existing component_inspector helper. Filters by _STRATEGIC_SCOPES
    so combat-only scopes (self/fleet/team) stay in the FleetAuraManager
    path.
    """
    from game.core.patterns.layer_iterator import iter_keyed_components
    from game.strategy.services.component_inspector import extract_abilities_from_component

    for _comp_key, _layer, comp in iter_keyed_components(design_data):
        abilities = extract_abilities_from_component(comp, registries)
        for ability_name, ability_data in abilities.items():
            entries = ability_data if isinstance(ability_data, list) else [ability_data]
            for entry in entries:
                if not isinstance(entry, dict):
                    continue
                scope = entry.get('scope', 'self')
                if scope in _STRATEGIC_SCOPES:
                    yield ability_name, entry
