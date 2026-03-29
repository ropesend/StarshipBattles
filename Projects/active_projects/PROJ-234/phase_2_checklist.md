# PROJ-234 Phase 2: Extract ShipInstanceSerializer [Medium]

**Objective:** Move to_dict/from_dict/to_json/from_json/clone to static utility class. ShipInstance keeps facade methods.
**Status:** Complete

---

#### Task 2.1: Create ShipInstanceSerializer class [Medium]
**File:** `game/strategy/data/ship_instance_serializer.py` **(NEW)**
**Tests:** `pytest tests/unit/strategy/ship_instance/ -x`
- [x] Create new file following FleetOrderSerializer pattern (static methods)
- [x] Move `to_dict` logic to `ShipInstanceSerializer.to_dict(ship)`.
- [x] Move `from_dict` logic to `ShipInstanceSerializer.from_dict(data, registries)`. Late-imports ShipInstance.
- [x] Move `to_json` logic to `ShipInstanceSerializer.to_json(ship, indent)`.
- [x] Move `from_json` logic to `ShipInstanceSerializer.from_json(json_str)`.
- [x] Move `clone` logic to `ShipInstanceSerializer.clone(ship)`. Late-imports ShipInstance + copy.
- [x] Move imports to serializer: `require_keys`, `validate_non_negative`, `json`, `copy`, `uuid`
**Notes:** 130-line serializer file. All static methods with late imports for ShipInstance.

#### Task 2.2: Replace ShipInstance methods with facades [Simple]
**File:** `game/strategy/data/ship_instance.py`
**Tests:** `pytest tests/unit/strategy/ship_instance/ -x`
- [x] Replace `to_dict` body with: late-import ShipInstanceSerializer, delegate
- [x] Replace `from_dict` body with: late-import ShipInstanceSerializer, delegate. Kept @classmethod and full signature/docstring.
- [x] Replace `to_json` body with: late-import + delegate
- [x] Replace `from_json` body with: late-import + delegate
- [x] Replace `clone` body with: late-import + delegate
- [x] Remove now-unused imports: `require_keys`, `validate_non_negative` (line 21), `json` (line 18)
- [x] Keep `uuid` import (still used by `create()`)
- [x] Run broader tests: `pytest tests/unit/strategy/ -x` — 2506 passed
**Notes:** Also verified save/load integration tests (221 passed).

#### Task 2.3: Write serializer unit tests [Simple]
**File:** `tests/unit/strategy/ship_instance/test_ship_instance_serializer.py` **(NEW)**
**Tests:** `pytest tests/unit/strategy/ship_instance/test_ship_instance_serializer.py -v`
- [x] Test `to_dict` -> `from_dict` round-trip preserves all fields
- [x] Test `clone` produces new instance_id but identical data
- [x] Test `to_json` -> `from_json` round-trip
- [x] Test `from_dict` raises `PersistenceException` on missing required keys
- [x] Test `from_dict` raises `PersistenceException` on negative numeric values
- [x] Test `from_dict` with registries passes them through to the instance
**Notes:** 10 tests, written TDD-first before serializer implementation. All pass.

---

**Phase 2 Complete When:**
- [x] All 3 tasks checked off
- [x] `pytest tests/unit/strategy/ship_instance/ -x` passes (104 tests: 94 original + 10 new)
- [x] `pytest tests/integration/save_load/ -v` passes (221 passed)
