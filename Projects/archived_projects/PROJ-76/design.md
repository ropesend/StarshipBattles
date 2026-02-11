# PROJ-76: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

The project adds an empire-wide view of all build queues/space yards. Key findings:

1. **Existing Infrastructure**: `BuildQueueSource` dataclass in `build_queue_source.py` already abstracts queue sources. Function `collect_build_queues_at_hex()` collects queues at a single hex - we extend this pattern for empire-wide collection.

2. **Window Pattern**: `PlanetListWindow` provides a mature modular pattern with sidebar filters, configurable columns, virtual scrolling. Follow this pattern.

3. **Multi-Select Pattern**: `BuildQueueScreen` implements Ctrl+click multi-select with `selected_queue_indices: Set[int]` - reuse this pattern.

4. **Navigation**: Clicking a row should open the hex build screen using existing `BuildQueueScreen`.

## Swarm Findings Summary

### Architecture
- Use modular file structure following PlanetListWindow pattern
- Main window file + separate filter/column/renderer modules if needed
- Start simple, extract modules only if file grows beyond 400 lines

### Key Patterns to Reuse
- **BuildQueueSource**: `game/strategy/data/build_queue_source.py:20-39` - Queue abstraction
- **collect_build_queues_at_hex()**: `game/strategy/data/build_queue_source.py:70-136` - Discovery pattern
- **_facility_is_shipyard()**: `game/strategy/data/build_queue_source.py:42-67` - Shipyard detection
- **PlanetListWindow layout**: `game/ui/screens/planet_list_window.py:90-142` - Three-panel layout
- **Multi-select**: `game/ui/screens/build_queue_screen.py:106-109, 309-359` - Ctrl+click toggle
- **Column config**: `game/ui/screens/planet_list_window.py:68-88` - Column definition format

### Dependencies & Risks
1. **Hex coordinate mapping**: Planets have relative location, fleets have global. Must compute global hex for planets.
2. **Build rate**: No explicit "build rate per turn" - system uses turns_remaining that decrements by 1 each turn.
3. **Large empires**: May have 100+ queues. Virtual scrolling recommended but can start simple.

### Opportunities Discovered
- Could add "jump to location" button in addition to opening build screen
- Could show queue completion estimates
- Could add sorting by various columns

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.

## Data Flow

```
Empire.colonies ─→ Planet.has_space_shipyard ─→ Planet base queue
                                              └→ Planet.facilities ─→ Shipyard queues

Empire.fleets ─→ Fleet.has_space_shipyard ─→ Fleet queue

All sources ─→ List[BuildQueueSource] ─→ Filter ─→ Sort ─→ Display
```

## Column Definitions

| ID | Title | Width | Source |
|----|-------|-------|--------|
| portrait | (none) | 50 | Asset resolver |
| location | Location | 180 | source.display_name |
| system | System | 120 | galaxy.get_system_of_planet() or fleet system |
| sector | Sector | 80 | Hex coordinates |
| queue_count | Items | 80 | len(source.construction_queue) |
| first_item | Building | 150 | queue[0]['design_id'] if queue else '-' |
| turns_left | Turns | 80 | queue[0]['turns_remaining'] if queue else '-' |
| capabilities | Can Build | 100 | 'Ships' / 'Complexes' / 'Both' |
| build_rate | Rate/Turn | 80 | '1/turn' (fixed in current system) |

## Filter Definitions

| Filter | Options | Default |
|--------|---------|---------|
| Location Type | Planet, Fleet | Both on |
| Queue Status | Active (has items), Empty | Both on |
| Capabilities | Ships, Complexes | Both on |
| Text Search | Free text | Empty |
