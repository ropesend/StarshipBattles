# BUG-79: Ships with multiple Fleet Space Yard components only get 1 Build Yard entry

## Description

If a Ship design has multiple Fleet Space Yard components then it should have multiple entries in the BuildYards list in the Sector(hex) build queue screen. Currently if a design has 2 Fleet Space Yard components then it only gets 1 entry.

## Priority

**High** — Significant feature broken; players cannot utilize all build yard capacity from multi-yard ship designs.

## Status
Awaiting Confirmation

## Root Cause
`fleet.has_space_shipyard` was a boolean property — it only answered "does this fleet have any yard?" The build queue source creation used this boolean check to create exactly 1 entry per fleet, regardless of how many yard components existed.

## Fix Applied
- **`game/strategy/data/fleet_capability_calculator.py`**: Added `space_shipyard_count` property that counts all `fleet_space_yard` and `SpaceShipyard` ability components across combat-capable ships. Refactored `has_space_shipyard` to use `count > 0`.
- **`game/strategy/data/fleet.py`**: Added `space_shipyard_count` property delegation.
- **`game/strategy/data/build_queue_source.py`**: Both `collect_build_queues_at_hex()` and `collect_all_build_queues_for_empire()` now create one entry per yard component (looping `range(yard_count)` instead of boolean check). Queue IDs indexed as `fleet_{id}_yard_{n}`. Display names show "Shipyard 1", "Shipyard 2" etc. when count > 1.

## Tests
- **`tests/unit/strategy/fleet/test_space_yard.py`**: Added `TestFleetSpaceShipyardCount` class with 5 tests (empty, one yard, two yards on one ship, yards across ships, destroyed ship excluded).
- Updated 3 existing tests to expect new queue_id format `fleet_{id}_yard_{n}`.
- 61/61 yard + build queue tests pass, 1687 strategy+UI tests pass.

## Work Log
- Traced build queue creation in `build_queue_source.py` — boolean `has_space_shipyard` check
- Added `space_shipyard_count` property to capability calculator
- Updated both queue collection functions to loop per-yard
- Updated existing test assertions for new queue_id format
