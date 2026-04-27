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

**Phase 1 audit task** — for each ability class in `game/simulation/components/abilities/`, check current `allowed_scopes` and ask: "Does it make design sense for a SHIP to project this to nearby ships/sectors?" Add strategic scopes only where the answer is yes.

**What's already in place** (confirmed via review 2026-04-27):
- `ShieldModifier` already declares `[SELF, FLEET, SECTOR, ALLIED_SECTOR, PLAYER_SECTOR, ENEMY_SECTOR, SYSTEM, ALLIED_SYSTEM, PLAYER_SYSTEM, ENEMY_SYSTEM]` ([planetary.py:443](../../../game/simulation/components/abilities/planetary.py#L443)). **Ready to use as the PROJ-305 sample (per D10).**
- `StrategicMovement` already declares `[SELF, ALLIED_SECTOR, ALLIED_SYSTEM]` ([propulsion.py:38-56](../../../game/simulation/components/abilities/propulsion.py#L38)). Surprising legacy support — Phase 1 confirms intent.

**Other candidates** (examples; confirm during Phase 1 audit; do NOT auto-add):
- `EmissionShroud` / stealth abilities: would add `sector` if/when they exist.
- `ShieldProjection`: maybe add `allied_sector` if design-meaningful.

Abilities that should NOT gain strategic scopes:
- Combat damage modifiers, weapon abilities, propulsion (those are inherently combat-tick-rate).
- Anything with no plausible "ship at hex H emits this to other ships at hex H" reading.

The audit produces a list — do not blanket-add scopes; each addition is a design choice. *Per decisions.md D10, PROJ-305 does NOT introduce a new `SensorBoost` ability — that's a separate design item deferred to a future project.*

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
        # Per D11: a cloaked / hidden fleet projects no abilities. Future
        # stealth design sets fleet.is_cloaked / fleet.is_visible_to(empire).
        # PROJ-305 baseline: assume always-visible.
        if self._is_hidden:
            return False
        return self.fleet.location == hex_coord

    def affects_system(self, system) -> bool:
        if self._is_hidden:
            return False
        return self.fleet.location in system  # or system.contains_hex(...)

    @property
    def _is_hidden(self) -> bool:
        # Hook for future stealth design. PROJ-305 returns False unconditionally;
        # PROJ-3XX (stealth) flips this to consult fleet visibility state.
        return False

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

A fleet with N ships and M components per ship requires `O(N*M)` ability extraction per `get_abilities()` call. With 100 systems × 10 fleets × 5 ships × 20 components = 100,000 component reads per turn-end if every consumer queries every fleet. Caching needed.

**Plan** (per decisions.md D12, refined 2026-04-27):
1. Phase 4 profiles a representative galaxy (the QA galaxy fixture, or a 100-system seeded gen). Compare against PROJ-300 Phase 4's `findings/perf_baseline.md`.
2. **Per-fleet-snapshot memoization on `FleetAbilitySource.get_abilities()`**, NOT a per-turn collector cache:
   ```python
   @dataclass(frozen=True)
   class FleetAbilitySource:
       fleet: Fleet
       registries: GameRegistries
       _abilities_cache: Optional[Dict[str, Any]] = field(default=None, init=False)

       def get_abilities(self) -> Dict[str, Any]:
           if self._abilities_cache is None:
               object.__setattr__(self, '_abilities_cache', self._compute_abilities())
           return self._abilities_cache
   ```
3. Per-turn cache is the WRONG granularity for fleet sources because fleets move mid-turn (a fleet that moved H→H' invalidates effects at both hexes). Per-instance memoization is correct: adapter instances are created during iteration and discarded after the query, so the cache lifecycle matches the snapshot lifecycle.
4. Static-source caching (planet, star, system archetype) is handled in PROJ-300 Phase 4 perf work — separate concern.

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
