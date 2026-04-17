# Phase 4: Turn State Snapshot & Rollback

**Objective:** Create a mechanism to capture the full mutable game state before a turn begins and restore it if the turn fails partway through.

**Key Principle:** A failed turn should leave the game state exactly as it was before the turn started. The player sees "Turn failed — state restored" rather than playing on corrupted state.

**Depends On:** Phase 2 (serialization must be strict and reliable — snapshot uses `to_dict()`/`from_dict()`)

---

## Problem Statement

The turn engine processes 100 ticks per turn, each with 14 phases. If Phase 4 of Tick 37 fails, Phases 0-3 of Ticks 1-37 have already mutated live game state. There is no undo. The game continues on partially-processed state that may be internally inconsistent (e.g., resources consumed but ships not spawned, fleets moved but combat not resolved).

## Design

### Snapshot via Serialization Round-Trip

The project already has comprehensive `to_dict()`/`from_dict()` methods on all major objects. The snapshot mechanism reuses this:

1. **Before turn:** Serialize all empires and galaxy to dicts via `to_dict()`
2. **Process turn:** Normal execution (mutates live objects)
3. **On failure:** Deserialize from the saved dicts via `from_dict()`, replacing the live objects

This approach:
- Reuses tested serialization infrastructure (no new serialization code)
- Stress-tests the serialization path every turn (catches serialization bugs early)
- Is straightforward to implement and verify
- Acceptable performance: one serialization pass per turn (~16ms for typical game)

### TurnStateSnapshot Class

```python
@dataclass
class TurnStateSnapshot:
    """Pre-turn state capture for rollback on failure."""
    turn_number: int
    empire_dicts: List[dict]       # [empire.to_dict() for empire in empires]
    galaxy_dict: dict              # galaxy.to_dict()
    timestamp: float               # time.time() for diagnostics
    
    @classmethod
    def capture(cls, turn_number: int, empires: List, galaxy) -> 'TurnStateSnapshot':
        """Serialize current state into a snapshot."""
        ...
    
    def restore(self, session) -> None:
        """Deserialize snapshot back into live objects, replacing session state."""
        ...
```

**Location:** New file `game/strategy/engine/turn_state_snapshot.py`

### What Gets Captured

Based on the turn engine mutation analysis, the following state is mutated during a turn:

| Object | Mutable State | Captured Via |
|--------|--------------|--------------|
| Empire | resource_pool, colonies list, fleets list, max_storage | `Empire.to_dict()` |
| Fleet | location, resources, orders, ships, construction_queue, path | `Fleet.to_dict()` |
| Ship | current_hp, is_alive, enabled_components, resources, carried_items | via Fleet |
| Planet | stockpile, deposits (quality/quantity), energy, atmosphere, facilities, active_abilities | `Galaxy.to_dict()` → `StarSystem.to_dict()` → `Planet.to_dict()` |
| Facility | construction_queue, component_states, consumable_levels | via Planet |
| Galaxy | (no direct mutations — planets are mutated via systems) | `Galaxy.to_dict()` |

### Restore Mechanics

Restoration is non-trivial because of object references:
- Empires reference fleets, which reference ships
- Empires reference colonies, which are planet objects in the galaxy
- Fleet orders reference target fleets/planets (resolved via `resolve_order_references()`)

The `GameSession.from_dict()` method already handles all of this (two-phase load: galaxy first, then empires with reference resolution). The restore method delegates to the same path.

```python
def restore(self, session) -> None:
    """Replace session state with snapshot data."""
    session.galaxy = Galaxy.from_dict(self.galaxy_dict)
    session.empires = [
        Empire.from_dict(d, galaxy=session.galaxy, registries=session._registries)
        for d in self.empire_dicts
    ]
    # Re-register fleets with galaxy
    for empire in session.empires:
        for fleet in empire.fleets:
            session.galaxy.register_fleet(fleet)
    # Resolve order references (fleet/planet targets)
    for empire in session.empires:
        for fleet in empire.fleets:
            fleet.resolve_order_references(session.galaxy, session.empires)
```

### Crash Snapshot for Debugging

When a turn fails, besides restoring state, dump the pre-failure state to a JSON file for debugging:

```
saves/<game>/crash_turn{N}_tick{T}_phase_{name}.json
```

Contains: the snapshot dicts + the exception details + which phase failed. This lets developers reproduce the exact state that caused the failure.

---

## Checklist

### Tests First (TDD)

#### Snapshot Capture
- [ ] Write test: `TurnStateSnapshot.capture()` produces snapshot with correct turn_number
- [ ] Write test: snapshot `empire_dicts` is a list of dicts (not live object references)
- [ ] Write test: snapshot `galaxy_dict` is a dict (not live object reference)
- [ ] Write test: modifying live objects after capture does NOT change snapshot data (isolation proof)
- [ ] Write test: capture succeeds for empty game (no empires, minimal galaxy)
- [ ] Write test: capture succeeds for game with multiple empires, fleets, ships

#### Snapshot Restore
- [ ] Write test: capture → mutate empires → restore → empires match original state
- [ ] Write test: capture → mutate galaxy (planet deposits) → restore → galaxy matches original
- [ ] Write test: capture → mutate fleet locations → restore → fleets at original locations
- [ ] Write test: capture → mutate ship HP → restore → ships at original HP
- [ ] Write test: capture → add new fleet → restore → new fleet gone, original fleets present
- [ ] Write test: capture → remove fleet → restore → fleet restored
- [ ] Write test: restore re-registers fleets with galaxy
- [ ] Write test: restore resolves order references (fleet/planet targets)

#### Capture Failure Handling
- [ ] Write test: if `to_dict()` raises during capture, `TurnStateSnapshot.capture()` raises `PersistenceException` with code `SNAPSHOT_FAILED`
- [ ] Write test: if capture fails, original state is untouched (capture is non-destructive)

#### Crash Snapshot File
- [ ] Write test: `dump_crash_snapshot()` writes valid JSON to the specified path
- [ ] Write test: crash snapshot JSON contains empire data, galaxy data, error info, phase name, tick number
- [ ] Write test: `dump_crash_snapshot()` handles write failures gracefully (logs error, doesn't raise)

- [ ] Run tests — confirm they fail

### Implementation

#### TurnStateSnapshot class
- [ ] Create `game/strategy/engine/turn_state_snapshot.py`
- [ ] Implement `TurnStateSnapshot` dataclass with fields: turn_number, empire_dicts, galaxy_dict, timestamp
- [ ] Implement `capture()` classmethod — serializes empires and galaxy to dicts
- [ ] Wrap capture in try/except; raise `PersistenceException(code=SNAPSHOT_FAILED)` on failure
- [ ] Implement `restore()` method — deserializes and replaces session state
- [ ] Implement `dump_crash_snapshot()` — writes JSON file for debugging

#### Integration Points (prepared but not wired in yet — that's Phase 5)
- [ ] `capture()` takes empires list and galaxy, returns `TurnStateSnapshot`
- [ ] `restore()` takes a session-like object with `.galaxy`, `.empires`, `._registries` attributes
- [ ] `dump_crash_snapshot()` takes save_path, snapshot, exception info; writes JSON file

- [ ] Run tests — confirm they pass

### Performance Verification
- [ ] Write a benchmark test: capture + restore for a game with 4 empires, 20 fleets, 100 ships
- [ ] Verify capture time is < 50ms (acceptable overhead per turn)
- [ ] Verify restore time is < 100ms (only triggered on failure, can be slower)

### Verification
- [ ] Run full test suite — no regressions
- [ ] Verify the snapshot file is importable without circular dependencies
