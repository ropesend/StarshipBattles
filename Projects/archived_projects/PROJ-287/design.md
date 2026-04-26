# PROJ-287: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Today's situation

- `game/strategy/systems/race_library.py::RaceLibrary` is file-backed. `get_race(race_id)` reads `{races_folder}/{race_id}.json` from disk every call.
- `PROJ-285/game/strategy/formulas/colony_output.py::planet_habitability_multiplier` calls `race_registry.get_race(race_id)` per species per tick — CURRENTLY mitigated by PROJ-285's per-turn cache on Planet, but only for habitability. The UI projects (PROJ-289+) will hit `get_race` per frame per species on many panels simultaneously.
- `PopulationEngine._get_race_config` + `HappinessEngine._get_race_config` each have their own resolver that delegates to `empire.race_config` (primary race only, doesn't generalize to multi-species).
- `StrategySessionFacade` is the CQRS-lite UI entry (docs/02_PATTERNS.md §6). Reads return DTOs, writes dispatch commands. A new `get_race_registry()` read method fits naturally.
- `Empire.colonies: List[Planet]`. Each `Planet.populations: List[SpeciesPopulation]`. `SpeciesPopulation.race_id: str`, `SpeciesPopulation.count: int`. No current aggregation across colonies to collect unique race_ids — UIs roll their own.

## Architecture

### `IRaceRegistry` protocol

Minimal surface:
```python
from typing import Protocol, Optional, runtime_checkable
if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig

@runtime_checkable
class IRaceRegistry(Protocol):
    def get_race(self, race_id: str) -> Optional[RaceConfig]: ...
```

Placed in `game/core/protocols.py` alongside the other `@runtime_checkable` protocols. Deliberately narrow — just the one method. No iteration, no list-all — those can be added when a consumer needs them.

### `CachedRaceRegistry` implementation

```python
class CachedRaceRegistry:
    def __init__(self, backing: 'RaceLibrary'):
        self._backing = backing
        self._cache: Dict[str, Optional['RaceConfig']] = {}

    def get_race(self, race_id: str) -> Optional['RaceConfig']:
        if race_id not in self._cache:
            self._cache[race_id] = self._backing.get_race(race_id)
        return self._cache[race_id]

    def invalidate(self, race_id: Optional[str] = None) -> None:
        """Clear cached entries. None → clear all; otherwise clear one id.
        Called from race-editor save flows so freshly-saved races are seen
        on the next `get_race` call."""
        if race_id is None:
            self._cache.clear()
        else:
            self._cache.pop(race_id, None)
```

Caches `None` results too — so a repeated lookup of a non-existent race_id doesn't hit disk twice. Invalidation on race save wipes the cache; subsequent reads re-load.

### Facade exposure

```python
class StrategySessionFacade:
    def __init__(self, session):
        self._session = session
        self._race_registry: Optional[IRaceRegistry] = None

    def get_race_registry(self) -> IRaceRegistry:
        if self._race_registry is None:
            from game.strategy.systems.race_library import RaceLibrary, CachedRaceRegistry
            self._race_registry = CachedRaceRegistry(RaceLibrary())
        return self._race_registry
```

Lazy-init on first read. One instance per facade (= one per game session).

### `Empire.resident_species()`

```python
def resident_species(self) -> Set[str]:
    """Return the set of race_ids with count >= 1 anywhere in this empire's
    colonies. Canonical 'species living in this empire' set — used by UI
    that iterates per-species (e.g. uncolonized-habitability display
    showing scores for each empire species). Recomputed every call —
    cheap compared to caching correctness concerns."""
    species: Set[str] = set()
    for colony in self.colonies:
        for pop in colony.populations:
            if pop.count >= 1:
                species.add(pop.race_id)
    return species
```

Deliberately NOT cached — empires have O(10-100) colonies × O(1-5) species, so this is tens-of-iterations cheap. Caching would introduce invalidation complexity (what if a species goes extinct mid-turn?) for no measurable gain.

### Invalidation discipline

The cache must invalidate when a race is saved in the race editor. The race editor saves via `RaceLibrary.save_race(race)` which is called from `RaceSetupScreen`. We add a hook:

```python
# In RaceLibrary.save_race (end of method):
# Emit a race-saved signal; the CachedRaceRegistry registered with the
# session listens and invalidates the cache entry.
```

OR simpler: expose the registry on the facade, and `RaceSetupScreen` calls `facade.get_race_registry().invalidate(race_id)` after save. The user-facing race-save flow is the only thing that can mutate a race file during a game session, so this is the one spot to wire.

## Key Patterns to Reuse

- **Protocol + runtime_checkable** (docs/02_PATTERNS.md §2) — existing pattern; fits naturally.
- **CQRS-lite read method on facade** (docs/02_PATTERNS.md §6) — `get_race_registry()` returns an interface, not a mutable live object. Consumers read; they don't mutate the registry itself.
- **Lazy init on first read** — mirrors `TurnEngine.harvesting_engine` etc. (PROJ-285 pattern).

## Dependencies & Risks

1. **Invalidation coverage** — if a race file is edited externally (user opens the JSON in a text editor mid-game), the cache won't know. Low-severity edge case; the workaround is "restart the game" which is reasonable.

2. **Memory** — the cache grows to at most one `RaceConfig` per unique race_id encountered. O(races × fields) = maybe 2KB per race × ~20 races = 40KB. Negligible.

3. **Thread safety** — pygame is single-threaded; the cache doesn't need locks.

4. **Engines don't migrate** — PopulationEngine and HappinessEngine keep their own `_get_race_config` helpers. If a future project wants them to use the facade registry, that's a separate refactor. In scope here: only the UI path.

## Design Decisions

See [decisions.md](decisions.md) for the full log with rationale.
