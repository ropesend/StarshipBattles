# BUG-77: Ships/fleets missing after save and load

## Description
When I save a game then load it later, all of the ships/fleets are missing.

## Priority
**Critical** - Blocks core gameplay; saved games lose all military units, making continued play impossible.

## Status
Awaiting Confirmation

## Root Cause
`Fleet.to_dict()` could not serialize `HexCoord` locations. The code checked for `hasattr(self.location, 'to_dict')` (HexCoord has no such method) and `isinstance(self.location, tuple)` (HexCoord is not a tuple). As a result, all fleet locations serialized as `null` in save files. On load, fleets had `location=None`, causing the strategy renderer to skip drawing them (line 562-564 of `strategy_renderer.py`).

The same issue affected the `path` field — movement paths with HexCoords were not serialized either.

## Fix Applied
- **`game/strategy/data/fleet.py`**: Updated `to_dict()` to check `isinstance(self.location, HexCoord)` and serialize as `{'q': q, 'r': r}` dict format. Updated `from_dict()` to handle the new dict format (with backward compatibility for old `[q, r]` list format). Applied same fix to path serialization/deserialization.

## Tests Updated
- **`tests/unit/strategy/fleet/test_serialization.py`**:
  - Updated `test_roundtrip_serialization` to verify HexCoord roundtrip without manual workaround
  - Replaced `test_to_dict_location_limitation` (documented the bug) with `test_to_dict_serializes_hexcoord_location` (asserts correct serialization)
  - Added `test_from_dict_restores_hexcoord_dict_format` for the new dict format
  - Removed `d['location'] = [0, 0]` workaround from `test_roundtrip_orders_preserved`

## Regression Test Results
- 9/9 fleet serialization tests pass
- 130/130 fleet + production tests pass
- 46/46 save/load integration tests pass
- 1918/1918 total strategy tests pass

## Work Log
- Investigated save/load pipeline: `SaveGameService -> GameSession.from_dict -> Empire.from_dict -> Fleet.from_dict`
- Inspected actual save file (`starting again/turn_7.json`) - confirmed fleet location stored as `null`
- Traced serialization: `Fleet.to_dict()` line 299-303 — HexCoord falls through both checks, stays None
- Fixed `to_dict()` with `isinstance(HexCoord)` check, fixed `from_dict()` with `{'q','r'}` dict support
- Also fixed path serialization/deserialization with same pattern
- All tests pass including backward compatibility with list format
