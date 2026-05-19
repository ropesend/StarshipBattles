# Phase 1: F-A-008 — extract `Fleet.to_dict` / `Fleet.from_dict` into `fleet_serde.py`

**Status:** Complete (2026-05-19)
**Depends on:** Phase 0 complete; PROJ-451 merged into main (HARD). PROJ-449 in flight is acceptable — Phase 1 does not require it (Phase 3 does).
**Review Mode:** standard (save-load is the regression gate)
**Files:**
- `game/strategy/data/fleet.py` (production; edit)
- `game/strategy/data/fleet_serde.py` (production; new)
- `tests/integration/save_load/test_fleet_serde_roundtrip.py` (test; new — characterization-first; does not exist at HEAD)
- `Projects/active_projects/PROJ-459/decisions.md` (docs; record the serde-shape decision per Task 1.3)

**Objective:** Extract `Fleet.to_dict`, `Fleet.from_dict`, and the `resolve_order_references` helper out of `fleet.py` into a sibling `fleet_serde.py`, modeled exactly on the existing `game/strategy/data/planet_serde.py` precedent (PROJ-372). Closes F-A-008.

**Save-format invariant:** byte-identical output before and after the extraction. This is the regression gate.

**Discipline framing:** This is a **characterization-first refactor**, not RED-then-GREEN strict TDD. The extraction introduces no new behavior, so the standard RED test is replaced by a comprehensive baseline test that PASSES against current code (characterizes the current dict shape), is then locked as a frozen comparison, and is re-run after extraction — any drift is a real failure. Per CLAUDE.md's allowance for pure-refactor work, this is the correct discipline for no-behavior-change extraction. (If a structural-RED test were preferred — e.g., a test asserting `game/strategy/data/fleet_serde.py` exists, which fails before extraction and passes after — record the addition in `decisions.md` and add it alongside the characterization tests. The characterization-first approach below is the default.)

**Reference template:** `game/strategy/data/planet_serde.py` (219 LOC; `planet_to_dict(planet)` + `planet_from_dict_kwargs(data)` + `_deserialize_planet_orders` helper). Read this file in full BEFORE writing fleet_serde.py.

**Existing test coverage** (Phase 0 should reconfirm):
- `tests/unit/strategy/fleet/test_serialization.py` — unit-level `Fleet.to_dict` / `Fleet.from_dict` coverage.
- `tests/integration/save_load/test_roundtrip_fleet.py` — integration-level save/load round-trip.
- `tests/unit/strategy/data/test_fleet_serialization.py` does **not** exist at HEAD; do not cite it.

---

## Tasks

### Task 1.1: Characterization-first — write the byte-identical capture-then-replay test [Simple]

**File:** `tests/integration/save_load/test_fleet_serde_roundtrip.py` (new; this file is **created** in Phase 1)
**Tests:** `pytest tests/integration/save_load/test_fleet_serde_roundtrip.py -q`

- [x] Create the test file. Add `test_fleet_to_dict_byte_identical_pre_extraction` that:
  - Constructs a representative Fleet (ships with cargo, orders, task forces, fleet policy).
  - Calls `fleet.to_dict()` and records the dict.
  - json-dumps the dict to a known string for later comparison.
- [x] Add `test_fleet_round_trip` that:
  - Constructs a fleet, dumps to dict, reconstructs via `Fleet.from_dict(data, registries=...)`, asserts the reconstructed fleet matches the original on the surface properties (ships, orders, task_forces, fleet_policy).
- [x] Run the test. It should pass against current code (pre-extraction baseline). This is the **characterization step**, not a RED step — the test capturing current behavior is exactly the point.
- [x] Capture the to_dict output string into the test file as a frozen comparison constant for the post-extraction assertion.

### Task 1.2: Read planet_serde.py and surface its idioms [Simple]

**File:** `game/strategy/data/planet_serde.py` (read-only reference)

- [x] Read the file end-to-end.
- [x] Note the public surface: `planet_to_dict(planet) -> Dict[str, Any]`, `planet_from_dict_kwargs(data: dict) -> Dict[str, Any]`, `_deserialize_planet_orders(orders_data, planet_name)` (module-private helper).
- [x] Note the import pattern: `TYPE_CHECKING` block at the top; lazy imports inside `planet_from_dict_kwargs` for runtime dependencies (`PersistenceException`, `ErrorCode`, `deserialize_list`, `PlanetType`, `PlanetaryFacility`, `SpeciesPopulation`).
- [x] Note the use of `validation_helpers` (`require_keys`, `validate_enum`, `validate_positive`, `validate_non_negative`).
- [x] Confirm `Planet.to_dict` / `Planet.from_dict` are 1-line facades calling into this module. (Quick read of `game/strategy/data/planet.py` to confirm the wrapper shape.)

### Task 1.3: Create `fleet_serde.py` with `fleet_to_dict` and `fleet_from_dict_kwargs` [Medium]

**File:** `game/strategy/data/fleet_serde.py` (new)
**Tests:** `pytest tests/integration/save_load/test_fleet_serde_roundtrip.py tests/unit/strategy/fleet/test_serialization.py -q -n 4`

**Design note — verified against `game/strategy/data/fleet.py:44-68`:** `Fleet.__init__` accepts ONLY constructor identity/config fields: `fleet_id`, `owner_id`, `location`, `speed`, `component_registry`, `display_name`. It initializes `self.ships = []`, `self._task_forces = []`, `self.fleet_policy = CombatPolicy()`, `self.orders = []`, and `self.path = []` internally. There is NO `ships=` kwarg. The helper therefore CANNOT return a ready-to-go kwarg dict that includes the ships list — `Fleet(**kwargs_with_ships)` would TypeError. The split is mandatory.

**Decision (record in `decisions.md` before writing the helper):** `fleet_from_dict_kwargs` returns ONLY the `__init__` kwargs. Per-ship hydration, task-force list, fleet_policy, orders, and resolve_order_references happen OUTSIDE the helper in `Fleet.from_dict` AFTER `Fleet(**fleet_from_dict_kwargs(data, registries))` returns. The `registries` parameter threads through `fleet_from_dict_kwargs` only insofar as it is needed for validation; the actual `ShipInstance.from_dict(ship_data, registries=registries)` calls run in a sibling helper exported from `fleet_serde.py` (e.g., `_deserialize_fleet_ships(ship_data_list, registries) -> List[ShipInstance]`) which `Fleet.from_dict` calls after construction.

- [x] Create the new file with a module docstring modeled on `planet_serde.py`'s:
  ```python
  """Save/load helpers for ``Fleet``.

  The ~30 fields, validation, and the order-deserialization path live
  here. ``Fleet.to_dict`` / ``Fleet.from_dict`` are 1-line facades that
  call into these helpers.
  """
  ```
- [x] Add `TYPE_CHECKING` block importing `Fleet`, `ShipInstance`, `GameRegistries` (and any other type-only refs).
- [x] Write `fleet_to_dict(fleet: "Fleet") -> Dict[str, Any]`:
  - Mirror the existing body of `Fleet.to_dict` (currently fleet.py:520-557). Same keys, same values, same ordering.
  - Handle optional fields (task_forces, fleet_policy) the same way the current method does.
- [x] Write `fleet_from_dict_kwargs(data: dict, registries: "GameRegistries") -> Dict[str, Any]`:
  - Validate top-level required keys with `require_keys` (mirroring `planet_serde.planet_from_dict_kwargs`).
  - Return ONLY the `Fleet.__init__` kwargs: `{"fleet_id": ..., "owner_id": ..., "location": ..., "speed": ..., "component_registry": ..., "display_name": ...}`.
  - Do NOT include `ships` / `task_forces` / `fleet_policy` / `orders` keys — `Fleet.__init__` does not accept them.
- [x] Write sibling helpers used by `Fleet.from_dict` for post-construction hydration. At minimum:
  - `_deserialize_fleet_ships(ship_data_list: List[Dict[str, Any]], registries: "GameRegistries") -> List["ShipInstance"]` — wraps the loop over `ShipInstance.from_dict(ship_data, registries=registries)`.
  - `_deserialize_fleet_orders(orders_data: List[Dict[str, Any]], fleet_id: str) -> List[Order]` — mirrors `_deserialize_planet_orders` from `planet_serde.py`.
  - Optionally: `_deserialize_fleet_task_forces`, `_deserialize_fleet_policy` if these grow beyond a handful of lines inline.
- [x] Add `__all__` exporting `fleet_to_dict`, `fleet_from_dict_kwargs`, and any helper functions `Fleet.from_dict` needs (e.g., `_deserialize_fleet_ships`).

### Task 1.4: Replace `Fleet.to_dict` / `Fleet.from_dict` bodies with facades [Medium]

**File:** `game/strategy/data/fleet.py`
**Tests:** `pytest tests/integration/save_load/ tests/unit/strategy/fleet/test_serialization.py -q -n 4`

- [x] Replace `Fleet.to_dict` body (fleet.py:520) with:
  ```python
  def to_dict(self) -> Dict[str, Any]:
      """Serialize Fleet to dict for save system. See fleet_serde.py."""
      from game.strategy.data.fleet_serde import fleet_to_dict
      return fleet_to_dict(self)
  ```
- [x] Replace `Fleet.from_dict` body (fleet.py:558) with the split-call shape (matches the Task 1.3 design):
  ```python
  @classmethod
  def from_dict(cls, data: Dict[str, Any], registries: "GameRegistries") -> "Fleet":
      from game.strategy.data.fleet_serde import (
          fleet_from_dict_kwargs,
          _deserialize_fleet_ships,
          _deserialize_fleet_orders,
      )
      fleet = cls(**fleet_from_dict_kwargs(data, registries))
      fleet.ships = _deserialize_fleet_ships(data.get("ships", []), registries)
      fleet.orders = _deserialize_fleet_orders(data.get("orders", []), fleet.id)
      # ... task_forces reattach, fleet_policy load — stays inline or via helpers
      return fleet
  ```
  The post-construction hydration of `ships` / `orders` / `task_forces` / `fleet_policy` lives in `Fleet.from_dict`, not in `fleet_from_dict_kwargs`, because `Fleet.__init__` does not accept those kwargs (verified at fleet.py:44-68).
- [x] Audit whether `resolve_order_references` (fleet.py:657) belongs in fleet_serde.py or stays on Fleet. The planet_serde precedent keeps deserialization helpers in the serde module; order references resolved at load time are part of the same conceptual surface.
- [x] Re-run the byte-identical save-output test from Task 1.1. It MUST pass — same dict before and after extraction.

### Task 1.5: Verify and tighten [Simple]

**Tests:**
```powershell
pytest tests/integration/save_load/ tests/unit/strategy/fleet/test_serialization.py -q -n 4
python Tools/test_sharded/test_sharded.py
```

- [x] Save-load tests green.
- [x] Sharded suite green; same count as Phase 0 baseline.
- [x] Re-measure fleet.py LOC (PowerShell): `(Get-Content game/strategy/data/fleet.py | Measure-Object -Line).Lines`. Target: ~545 LOC (down from 686). Acceptable: under 600.
- [x] Measure fleet_serde.py LOC: `(Get-Content game/strategy/data/fleet_serde.py | Measure-Object -Line).Lines`. Target: ~150 LOC (in the same ballpark as planet_serde.py's 219).
- [x] Update `findings/PROJ-459_findings.md`: F-A-008 status → "closed via Phase 1 extraction; fleet_serde.py created; save-format byte-identical".

### Task 1.6: Docs sync [Simple]

**Files:** `docs/02_PATTERNS.md`, `docs/01_ARCHITECTURE.md`

- [DEFERRED to consolidation] Update `docs/02_PATTERNS.md` if it references the planet_serde pattern as a "single instance"; now there are two. (Check first; the file may already describe the pattern generically.) — Search returned no matches; no edit needed. Staged note in `_doc_consolidation/PROJ-459_pending.md`.
- [DEFERRED to consolidation] Update `docs/01_ARCHITECTURE.md` strategy/data/ listing to include `fleet_serde.py` alongside `planet_serde.py`. — Staged in `_doc_consolidation/PROJ-459_pending.md`; the last of PROJ-457/459/460 to finish applies all three projects' pending blocks.
- [DEFERRED to consolidation] Verify the docs reflect current state.

### Task 1.7: Commit [Simple]

- [NOT DONE — per main-agent instructions: "Do NOT commit. Leave changes staged for the main agent."]
- [x] Update `plan.md` Current State.

---

## Phase Completion Checklist
- [x] fleet_serde.py created (168 LOC) modeled on planet_serde.py (219)
- [PARTIAL] fleet.py drops to 632 LOC (was 693; target ~545 not reached — post-construction hydration must remain on Fleet per `__init__` constraint; see decisions.md 2026-05-19)
- [x] `Fleet.to_dict` / `Fleet.from_dict` are 1-line / facade-shaped bodies
- [x] Save-load round-trip byte-identical (new `test_fleet_serde_roundtrip.py` 3 tests pass)
- [x] `pytest tests/integration/save_load/ tests/unit/strategy/fleet/` green (388 tests)
- [x] Sharded suite green (23397/23397 passed)
- [x] F-A-008 marked closed in findings file
- [DEFERRED] Docs updated — staged to `_doc_consolidation/PROJ-459_pending.md` per cross-group consolidation rule
