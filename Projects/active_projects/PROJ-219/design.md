# PROJ-219: Fleet Registration Consolidation - Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Problem Statement

Fleet registration with the galaxy registry currently requires two separate calls:
1. `empire.add_fleet(fleet)` - adds to empire ownership
2. `galaxy.register_fleet(fleet)` - enables O(1) lookup by ID

This two-step ritual is error-prone. PROJ-216 found that fleet registration was missing in 3 locations, causing all fleet orders to silently fail.

**Additionally discovered during analysis:** Fleet UNREGISTRATION is missing in 6+ locations, leaving "ghost" fleets in the registry that can be looked up but are no longer valid.

## Initial Analysis

### Current Empire Class (`game/strategy/data/empire.py`)
- `add_fleet()` (lines 56-58): Just appends to list, sets owner_id
- `remove_fleet()` (lines 60-62): Just removes from list
- `from_dict()` (lines 176-251): Deserializes fleets but doesn't register
- **NO `_galaxy` reference currently**

### Current Registration Points
| Location | File:Line | Pattern |
|----------|-----------|---------|
| Production | production_engine.py:639-643 | `add_fleet()` + `register_fleet()` |
| Split Fleet | command_handlers.py:691-692 | `add_fleet()` + `register_fleet()` |
| Load Game | game_session.py:353-357 | Post-load registration loop |

### Missing Unregistration (BUGS)
| Location | File:Line | Impact |
|----------|-----------|--------|
| Combat destruction | conflict_resolution_engine.py:186 | Ghost fleets after combat |
| JOIN_FLEET merge | fleet_order_processor.py:113 | Merged fleet stays in registry |
| COLONIZE empty | fleet_order_processor.py:216 | Empty fleet stays in registry |
| Instant merge | fleet_order_processor.py:663 | Merged fleet stays in registry |
| Superweapon finalize | superweapon_order_processor.py:103 | Consumed fleet stays in registry |

Only correct location: `superweapon_order_processor.py:238-241` (stellarate)

## Swarm Findings Summary

### Architecture (Architecture Analyst)
- Empire owns fleets via `self.fleets` list (line 30 in empire.py)
- Galaxy maintains `fleets_by_id` dict via `GalaxyEntityRegistry` (line 175 in galaxy.py)
- Fleet has no back-reference to Galaxy or Empire (data object design)
- Registration is O(1) dict insert, lookup is O(1) dict get
- Adding `_galaxy` to Empire mirrors the existing Planet pattern (Empire ↔ Planet via colony_ids)
- No layer violation: Both Empire and Galaxy are Strategy layer entities

### Key Patterns to Reuse (Pattern Scout)
- **Colony registration**: `empire.add_colony()` sets `planet.owner_id` - same pattern for fleets
- **Galaxy facade delegation**: `galaxy.register_fleet()` delegates to `GalaxyEntityRegistry`
- **Optional references**: Many classes use `if self._dependency:` guards for optional deps
- **Lazy init**: `self._nav_service = None` pattern used in FleetMovementEngine
- **Three-phase lifecycle**: Create object → Add to owner → Register with lookup

### Dependencies & Risks (Dependency Mapper, Risk Assessor)
1. **Tests without Galaxy**: ~50+ tests create Empire without Galaxy context
   - Mitigation: `if self._galaxy:` guard makes registration optional
2. **Double-unregister in stellarate**: Will unregister twice after change
   - Mitigation: Remove explicit call, `pop(id, None)` is idempotent
3. **Deserialization order**: Galaxy must exist before empires
   - Mitigation: Use `set_galaxy()` after both are loaded
4. **No circular import risk**: Empire doesn't import Galaxy (uses TYPE_CHECKING)
5. **`_galaxy` not serialized**: Transient reference, not in `to_dict()`

### Data Flow Traces (Data Flow Tracer)
**Fleet Creation:**
- ProductionEngine._spawn_ship() → Fleet() → empire.add_fleet() → galaxy.register_fleet()

**Fleet Destruction:**
- ConflictResolutionEngine._resolve_combat_at_hex() → empire.remove_fleet() [MISSING: unregister]
- FleetOrderProcessor.process_join_fleet() → empire.remove_fleet() [MISSING: unregister]

**Fleet Lookup:**
- galaxy.get_fleet_by_id() → GalaxyEntityRegistry.get_fleet_by_id() → fleets_by_id.get()

**Deserialization:**
- Galaxy.from_dict() → Empire.from_dict() → Fleet.from_dict() → [explicit registration loop]

### Test Impact (Test Impact Analyst)
- 50+ test files create Empire without Galaxy
- 21 files call Empire.from_dict()
- Pattern A (simple constructor): `Empire(0, "Test", (255,0,0))` - requires optional galaxy
- Pattern B (from_dict): `Empire.from_dict(data, galaxy=session.galaxy)` - already passes galaxy
- New tests needed: 6+ integration tests for formerly-buggy locations

### Opportunities Discovered
- Fixing unregistration bugs will eliminate "ghost fleet" issues
- Consolidated registration reduces maintenance burden
- Clear ownership model: Empire is the single point of fleet lifecycle
- Maintenance scuttling also has missing unregister (maintenance_engine.py:286)

## Design Decisions

### Chosen: Empire-Galaxy Back-Reference

```python
class Empire:
    def __init__(self, ..., galaxy: 'Galaxy' = None):
        self._galaxy = galaxy

    def set_galaxy(self, galaxy: 'Galaxy') -> None:
        self._galaxy = galaxy

    def add_fleet(self, fleet):
        self.fleets.append(fleet)
        fleet.owner_id = self.id
        if self._galaxy:
            self._galaxy.register_fleet(fleet)

    def remove_fleet(self, fleet):
        if fleet in self.fleets:
            self.fleets.remove(fleet)
            if self._galaxy:
                self._galaxy.unregister_fleet(fleet)
```

### Alternatives Rejected

1. **Fleet holds galaxy reference**: Fleet is a data object, shouldn't know about Galaxy
2. **Event-based registration**: Over-engineered for this use case
3. **Registration service**: Adds another call site to remember

### Wiring

```
GameInitializer.initialize()
    └── Creates Galaxy, Empires
    └── empire.set_galaxy(galaxy)  <-- NEW

GameSession.from_dict()
    └── Loads Galaxy, Empires
    └── empire.set_galaxy(galaxy)  <-- NEW
    └── Registers deserialized fleets (explicit loop - kept)

Runtime:
    empire.add_fleet(fleet) → auto-registers
    empire.remove_fleet(fleet) → auto-unregisters
```

See [decisions.md](decisions.md) for the full log with rationale.
