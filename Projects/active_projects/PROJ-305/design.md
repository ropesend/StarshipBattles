# PROJ-305: Design Document

> **PRECONDITION:** PROJ-300. Read [`Projects/active_projects/PROJ-300/design.md`](../PROJ-300/design.md) first. PROJ-301..304 also recommended.

---

## Initial Analysis

Phase A reading at kickoff:
- `Fleet` dataclass at `game/strategy/data/fleet.py`. Confirm: how does a fleet enumerate its ships?
- `ShipInstance` at `game/strategy/data/`. Confirm: how does a ship enumerate its components and their abilities?
- The existing `FleetAuraManager` in the simulation layer (combat). Confirm what scopes it consumes; ensure those scopes do NOT leak into strategic projection.
- The existing `Ability.allowed_scopes` mechanism in `game/simulation/components/abilities/base.py`.
- Existing strategic-layer fleet capability inspection — `game/strategy/services/component_inspector.py:has_warp_capability` is precedent for component-walking on a fleet.

## The Scope Dichotomy

The framework's scope keywords split cleanly into two consumption groups:

**Combat-only scopes** (consumed by `FleetAuraManager` during battle):
- `self`
- `fleet`
- `team`

**Strategic-layer scopes** (consumed by `system_effects_collector` via `IAbilitySource` adapters):
- `sector`, `allied_sector`, `enemy_sector`, `player_sector`
- `system`, `allied_system`, `enemy_system`, `player_system`
- `planet`, `empire`, `allied_empire`

`FleetAbilitySource` filters to **strategic-layer scopes only**. Combat-only scopes stay in the combat path. There is no overlap; an ability can declare either, but not both meaningfully on the same component (it can declare different abilities at different scopes — that's already true today).

## Architecture

### Expanding `allowed_scopes` on selected abilities

Audit each ability class in `game/simulation/components/abilities/`:
- For each ability, ask: "Does it make design sense for a SHIP to project this to nearby ships/sectors?"
- Where yes, add the strategic scopes to the class's `allowed_scopes`.

Likely candidates (examples; confirm during Phase 1):
- `SensorBoost`: add `allied_sector`, `allied_system` (a sensor array on a flagship benefits nearby allies).
- `ShieldProjection`: maybe add `allied_sector` (an escort projecting shield-bonus aura at the strategic level — design-meaningful?).
- `EmissionShroud` / stealth abilities: add `sector` (cloaks the hex on the strategy map).

Abilities that should NOT gain strategic scopes:
- Combat damage modifiers, weapon abilities, propulsion (those are inherently combat-tick-rate).

The audit produces a list — do not blanket-add scopes; each addition is a design choice.

### `FleetAbilitySource` adapter

```python
@dataclass(frozen=True)
class FleetAbilitySource:
    fleet: Fleet
    registries: GameRegistries

    @property
    def source_kind(self) -> str:
        return 'fleet'

    @property
    def source_label(self) -> str:
        flagship_name = self._flagship_name
        owner = self._owner_label
        return f"Fleet '{self.fleet.name}' ({owner})" if not flagship_name \
               else f"Flagship '{flagship_name}' ({owner})"

    @property
    def source_id(self) -> str:
        return f"fleet:{self.fleet.id}"

    @property
    def owner_id(self) -> Optional[int]:
        return self.fleet.owner_id

    def get_abilities(self) -> Dict[str, Any]:
        """Aggregate strategic-scope abilities from all operational ships in the fleet.

        Walks every ship's components, extracts abilities (via existing
        extract_abilities_from_component helper), and INCLUDES only entries whose
        scope is strategic-layer. Combat-only scopes (self/fleet/team) are skipped.
        """
        result: Dict[str, List[Any]] = {}
        for ship in self.fleet.ships:
            if not ship.is_combat_capable:
                continue
            for comp in iter_keyed_components(ship.design_data):
                abilities = extract_abilities_from_component(comp, self.registries)
                for ability_name, ability_data in abilities.items():
                    entries = ability_data if isinstance(ability_data, list) else [ability_data]
                    for entry in entries:
                        scope = entry.get('scope', 'self')
                        if scope in _STRATEGIC_SCOPES:
                            result.setdefault(ability_name, []).append(entry)
        return result

    def affects_hex(self, hex_coord) -> bool:
        return self.fleet.location == hex_coord

    def affects_system(self, system) -> bool:
        return self.fleet.location in system  # or system.contains_hex(...)

    def get_activation_state(self, ability_name: str) -> Optional[Any]:
        # Ship components can have activation state; aggregating across many
        # ships is complex. For PROJ-305, treat fleet abilities as always-active.
        # Per-component activation is a follow-up.
        return None
```

`_STRATEGIC_SCOPES = {'sector', 'allied_sector', 'enemy_sector', 'player_sector', 'system', 'allied_system', 'enemy_system', 'player_system', 'planet', 'empire', 'allied_empire'}` — the union of PROJ-300's `_SECTOR_SCOPES` and `_SYSTEM_SCOPES` plus the few extras.

### Iterator registration

```python
def _fleet_provider_at_hex(system, hex_coord, registries):
    galaxy = system._galaxy_ref or _resolve_galaxy(system)
    for empire in galaxy.empires:
        for fleet in empire.fleets:
            if fleet.location == hex_coord:
                source = FleetAbilitySource(fleet, registries)
                if source.get_abilities():
                    yield source

register_source_provider(_fleet_provider_at_hex)
```

(Provider signature may need to take `registries` — adjust API in PROJ-300 if needed and document there.)

### Performance

A fleet with N ships and M components per ship requires `O(N*M)` ability extraction per `get_abilities()` call. With 100 systems × 10 fleets × 5 ships × 20 components = 100,000 component reads per turn-end if every consumer queries every fleet. Almost certainly need caching.

**Plan**:
1. Phase 4 profiles a representative galaxy (the QA galaxy fixture, or a 100-system seeded gen).
2. If `collect_sector_effects` is hot, add a per-turn cache:
   ```python
   _SECTOR_EFFECTS_CACHE: Dict[Tuple[int, int, int], List[Dict]] = {}  # (turn, hex_id, empire_id) → effects
   ```
3. Cache invalidation is per-turn (cache is cleared at turn start in TurnEngine).

## Swarm Findings Summary

To be filled at kickoff.

### Dependencies & Risks
1. **Scope leak** — combat-only abilities (`scope: fleet`) accidentally appearing in Sector Effects, or strategic abilities accidentally double-applying as combat auras. Test rigorously with both kinds present on the same component.
2. **Fleet activation states** — combat-side activation on ship components is complex (per-ship, per-component). PROJ-305 treats fleet abilities as always-active to ship; per-component activation handling is a follow-up.
3. **Performance regression** — `collect_sector_effects` is called per-turn from movement, hazard, and combat code paths. Adding fleets multiplies the workload. Mitigation: per-turn cache (Phase 4).
4. **`registries` plumbing** — providers may need access to `GameRegistries` for component lookups. PROJ-300's iterator API may need to take `registries` as an arg if it doesn't already.

### Opportunities Discovered
- After PROJ-305, the framework supports the FULL set of source kinds. A unifying smoke test (a single hex with all 7 source kinds active) becomes the canonical regression test for the entire ability framework.
- `SensorBoost scope: allied_sector` becomes a usable mechanic for the existing fog-of-war / sensor system — opens design space for "scout-flagship" doctrine.

## Design Decisions

See [decisions.md](decisions.md).
