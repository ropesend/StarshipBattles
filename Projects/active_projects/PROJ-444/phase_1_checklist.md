# PROJ-444 Phase 1: Tiny one-shot data + facade polish fixes

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-444 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Burn down ~15 independent <30-LOC polish fixes in the data + facade layer. Each task is self-contained; no inter-task dependencies. TDD recipe: write a focused test that fails, make the change, run targeted tests, check off the task.

**Cross-bucket file-ownership rule:** This phase only touches `game/strategy/data/`, `game/strategy/facade/`, and `tests/{unit,integration}/strategy/{data,facade}/` + `tests/integration/save_load/`. Do NOT touch any other directory. Three sibling agents are running PROJ-445/446/447 in parallel.

**Source-of-truth findings:** [`findings/bucket_a_data_facade_scan.md`](findings/bucket_a_data_facade_scan.md) — read each finding's full text (severity, source refactor, what survived, why it's a problem, suggested action) before starting that task.

---

## Tasks

### Task 1.1: F-A-001 — BayInventory remove_* non-negative guards [Simple]
**File:** `game/strategy/data/bay_inventory.py:140` (remove_resource), `:176` (remove_population)
**Tests:** `pytest tests/unit/strategy/data/test_bay_inventory.py -v`

- [ ] Read the existing `add_resource` guard at bay_inventory.py:132 and `add_population` at :172
- [ ] **RED**: Add two unit tests to `tests/unit/strategy/data/test_bay_inventory.py`: `test_remove_resource_rejects_negative_amount` and `test_remove_population_rejects_negative_count`. Both call `remove_*(-3.0)` / `remove_*(-2)` and assert `ValueError` is raised. Confirm both FAIL before code change.
- [ ] **GREEN**: Mirror the `add_*` guard at the top of `remove_resource` (`if amount < 0: raise ValueError(...)`) and `remove_population` (`if count < 0: raise ValueError(...)`). Use the same message phrasing as the corresponding `add_*` raise.
- [ ] Run targeted test — both new tests pass; existing tests still pass.
- [ ] Verify the change is symmetric with `Container.remove()` per DI-2026-05-18-005 (Container side is in scope of the DI log entry, NOT this task).

### Task 1.2: F-A-006 — Fix stale 350-LOC reference in planet_serde docstring [Simple]
**File:** `game/strategy/data/planet_serde.py:4-6`

- [ ] Read lines 4-6; current text references "the 350 LOC ceiling" from PROJ-372
- [ ] Edit the comment to reference the current 500-LOC ceiling per CLAUDE.md, OR drop the LOC reference entirely (preferred — provenance comments rot)
- [ ] No test changes required; this is a docstring polish.

### Task 1.3: F-A-015 + F-A-016 — Type BuildQueueSourceDTO.construction_queue [Medium]
**File:** `game/strategy/facade/dto/build_queue_dto.py:16,20`
**Tests:** `pytest tests/unit/strategy/facade/ -k build_queue -v`

- [ ] Read existing `BuildQueueSourceDTO` definition + the known dict shape from `Planet.add_production` at `game/strategy/data/planet.py:359-365`
- [ ] **RED**: Add a test asserting `dto.construction_queue` is immutable (`with pytest.raises(TypeError, AttributeError): dto.construction_queue.append(...)`). This test FAILS today because `List[Dict[str, Any]]` is mutable.
- [ ] **GREEN — typed item dataclass**: Add a `BuildQueueItemDTO` frozen dataclass with fields `design_id: str`, `type: str`, `turns_remaining: int`, `resources_consumed: Mapping[str, float]`, plus any other keys that exist on the dicts produced by `Planet.add_production` (verify by reading that method).
- [ ] **GREEN — retype**: Change `construction_queue: List[Dict[str, Any]]` to `construction_queue: Tuple[BuildQueueItemDTO, ...]`. Update `from_domain` to build the tuple via comprehension (no `deepcopy` needed; frozen dataclasses are immutable).
- [ ] **Caller migration**: `git grep -n "construction_queue\["` across `game/ui/` to find readers; update each to use dotted attribute access. Expected ~6 sites per the findings note.
- [ ] Run targeted tests; full sharded suite green for the touched files.

### Task 1.4: F-A-017 — Narrow FleetInfo.from_fleet exception swallowing [Simple]
**File:** `game/strategy/facade/dto/fleet_dto.py:192-196`
**Tests:** `pytest tests/unit/strategy/facade/dto/test_fleet_dto.py -v`

- [ ] Read the existing `try: ... except (ValueError, AttributeError):` block
- [ ] **GREEN**: Split into two `except` clauses. `AttributeError` → return `()` silently (test-stub path). `ValueError` → log a WARN with the fleet id then return `()` (production DI configuration bug should be visible). Use the existing logger if one is present in the module; otherwise import `logging.getLogger(__name__)`.
- [ ] **RED-then-GREEN**: Add a test that constructs a FleetInfo with a fleet whose `capabilities.list_abilities()` raises `ValueError` and asserts the WARN log is emitted (`caplog` fixture). Also keep the existing test for the empty-capabilities AttributeError path.
- [ ] Run targeted tests.

### Task 1.5: F-A-018 — Add total_resources aggregate to EmpireInfo [Simple]
**File:** `game/strategy/facade/dto/empire_dto.py:76-116`
**Tests:** `pytest tests/unit/strategy/facade/dto/test_empire_dto.py -v`

- [ ] Read `EmpireInfo` dataclass + existing `from_empire` factory
- [ ] **RED**: Add a unit test `test_empire_info_total_resources_aggregates_colony_stockpiles` that builds an empire with 2 colonies (stockpiles `{metals: 10, organics: 5}` and `{metals: 3, fuel: 2}`) and asserts `info.total_resources` is a tuple with all `ResourceCatalog.all_ids()` ordering, with the correct aggregated quantities.
- [ ] **GREEN**: Add `total_resources: Tuple[Tuple[str, float], ...]` field to `EmpireInfo`. In `from_empire`, populate via `tuple((rid, empire.resource_pool.get(rid, 0.0)) for rid in ResourceCatalog.from_json().all_ids())`.
- [ ] Run targeted tests.

### Task 1.6: F-A-019 — Stable catalog-order iteration in PlanetInfo.stockpile [Simple]
**File:** `game/strategy/facade/dto/planet_dto.py:78-79` + `_dict_to_tuple` helper at `:34-41`
**Tests:** `pytest tests/unit/strategy/facade/dto/test_planet_dto.py -v`

- [ ] Read the existing `_dict_to_tuple` helper
- [ ] **RED**: Add a test `test_planet_info_stockpile_uses_catalog_order` that builds two Planets with different insertion-order stockpile dicts and asserts both produce identical `info.stockpile` tuples (same key order).
- [ ] **GREEN**: In `from_planet` (or the `_dict_to_tuple` helper if used elsewhere), iterate `ResourceCatalog.from_json().all_ids()` and emit `(rid, planet.stockpile.get(rid, 0.0))` tuples. Keep `_dict_to_tuple` for other call sites if any; for stockpile specifically use the catalog-iteration form.
- [ ] Run targeted tests.

### Task 1.7: F-A-020 — Fail-fast on unknown target type in OrderSerializer [Simple]
**File:** `game/strategy/data/order_serializer.py:148-152`
**Tests:** `pytest tests/unit/strategy/data/test_order_serializer.py -v`

- [ ] Read the existing 7 format branches + the "Unknown format - return as-is" fallback at the end of `_deserialize_target`
- [ ] **RED**: Add `test_deserialize_unknown_typed_target_raises` that passes `{"type": "star_ref", "id": 1}` and asserts `PersistenceException` (or `ValueError` if PersistenceException isn't available — check `game/core/exceptions.py`) with code `CORRUPT_DATA`.
- [ ] **GREEN**: After the 6 known branches, before the pass-through, check `if isinstance(target_data, dict) and "type" in target_data:` and raise `PersistenceException("Unknown target type: {target_data['type']!r}", code=ErrorCode.CORRUPT_DATA)`. Untyped dicts (no `type` key) keep the pass-through for legacy save tolerance.
- [ ] Run targeted tests.

### Task 1.8: F-A-021 — Audit PlanetType re-export shim [Simple]
**File:** `game/strategy/data/galaxy.py:10`

- [ ] Run `git grep -n "from game.strategy.data.galaxy import.*PlanetType"` across the repo
- [ ] If only test files import via this path: migrate them to `from game.strategy.data.planet import PlanetType` and delete the line at galaxy.py:10
- [ ] If any non-test caller still uses it: leave the line, but drop the `# noqa: F401` if it's not actually needed (try the file through your linter)
- [ ] Run sharded test suite to confirm no import breakage.

### Task 1.9: F-A-022 — Audit StarGenerator PROJ-372 shim [Simple]
**File:** `game/strategy/data/stars.py:155`

- [ ] Run `git grep -n "stars\.StarGenerator\|from game.strategy.data.stars import.*StarGenerator"` across the repo
- [ ] If only test scaffolds / migration guards use it: delete the shim + the comment
- [ ] If production code uses it: leave it, but update the comment to reflect current consumption
- [ ] Run sharded test suite.

### Task 1.10: F-A-023, F-A-026, F-A-027 — Stale historical comment cleanup [Simple]
**Files:**
- `game/strategy/data/fleet_capability_calculator.py:7` (F-A-023 — PROJ-211 Task 5.7 narration)
- `game/strategy/data/empire.py:323-326` + matching block in `from_dict` (F-A-026 — duplicated PROJ-436 Phase 5 deletion-comments)
- `game/strategy/data/carried_vehicle.py:112` (F-A-027 — stale `ShipInstance.carried_items` narration)

- [ ] F-A-023: Prune the docstring at fleet_capability_calculator.py:7 to a current-behavior description or drop the LOC-history line entirely. Keep nothing older than PROJ-422.
- [ ] F-A-026: Collapse the two PROJ-436 Phase 5 deletion-comments at empire.py:323-326 and the matching one in `from_dict`. Keep at most one line at the field-comment block (~line 60-63) where the deletion is documented.
- [ ] F-A-027: Rewrite the comment to "stored in `bay_inventory.bay` (typed)" — drop the `ShipInstance.carried_items` reference.
- [ ] No test changes required.

### Task 1.11: F-A-024 + F-A-025 — Delete legacy save-shape guards [Simple]
**Files:**
- `game/strategy/data/storm.py:127-131` (F-A-024 — PROJ-300 D19 legacy 'effects' raise)
- `game/strategy/data/planet_serde.py:159` (F-A-025 — `data.get("resources", {})` legacy key fallback)
**Tests:** `pytest tests/unit/strategy/data/test_storm.py tests/unit/strategy/data/test_planet_serde.py -v`

- [ ] F-A-024: Delete the explicit `'effects'` legacy-shape raise (saves are disposable per CLAUDE.md). Let the natural `KeyError`/`TypeError` from passing the wrong shape surface. Remove any associated test that asserts the legacy raise message.
- [ ] F-A-025: Change `data.get("deposits", data.get("resources", {}))` to `data.get("deposits", {})`. Remove the parallel test if any.
- [ ] Run targeted tests.

### Task 1.12: F-A-030 — Cache specs_by_facade_helper result [Simple]
**File:** `game/strategy/facade/slices/command_dispatch_slice.py:73-107`
**Tests:** `pytest tests/unit/strategy/facade/slices/test_command_dispatch_slice.py -v`

- [ ] Read existing `__getattr__` resolver
- [ ] **GREEN**: Cache the result of `command_registry.specs_by_facade_helper()` in a module-level dict on first call (`_specs_cache: Dict[str, CommandSpec] | None = None`; lazily populated). If `command_registry` exposes a mutation hook, register cache invalidation; otherwise document the assumption that command-spec registration completes before first facade dispatch.
- [ ] **RED-then-GREEN**: Add a test asserting `specs_by_facade_helper` is called at most once for N facade dispatches (use `mock.patch.object` to spy on the call count).
- [ ] Run targeted tests.

### Task 1.13: F-A-031 — Add empire_index lazy cache to FacadeSessionState [Simple]
**File:** `game/strategy/facade/slices/_facade_state.py:113-118`
**Tests:** `pytest tests/unit/strategy/facade/slices/test_facade_state.py -v`

- [ ] Read the existing `planet_index` lazy-cache pattern at the same file (lines 66, 69 reference)
- [ ] **GREEN**: Add `empire_index: Dict[str, Empire] | None` field on `FacadeSessionState`. In `get_empire_by_id`, populate lazily on first call; clear in `invalidate_all` alongside the existing caches. Use the same pattern as `planet_index` exactly.
- [ ] **RED-then-GREEN**: Add a test asserting `get_empire_by_id` is O(1) after first call (instrument with a counter on the underlying scan).
- [ ] Run targeted tests.

### Task 1.14: F-A-032 — Rename stars_cache_new field [Simple]
**File:** `game/strategy/facade/slices/_facade_state.py:82`

- [ ] Rename `stars_cache_new` → `raw_star_list_cache` (semantic name)
- [ ] Update the ~3 internal callers in `_facade_state.py`
- [ ] Update any test that names the field directly (`git grep -n "stars_cache_new"` to find)
- [ ] Run targeted tests.

---

## Phase Completion Checklist

When all tasks above are checked off:
- [ ] All ~15 findings either fixed or recategorized with rationale in [decisions.md](decisions.md)
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-444 1` — PASSED
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 2
- [ ] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries (engine/UI/sim residue spotted during the work)

## Notes / Deferrals

- **F-A-002 / F-A-003 / F-A-004 / F-A-005** (legacy-kwarg wrapper retirement) is Phase 3 — STRUCTURAL JOINT-PHASE with PROJ-446 F-C-020. Do NOT touch in Phase 1.
- **F-A-007 / F-A-008 / F-A-009** (LOC-ceiling violations on ship_instance.py, fleet.py, planet_gen.py) are Phase 4. ship_instance.py is explicitly out of PROJ-444 scope per its findings entry; the other two are Phase 4 extractions.
- **F-A-010 / F-A-012 / F-A-013 / F-A-014** (Container substrate residue) is Phase 2.
- **F-A-028 / F-A-029** (facade integration test skip-on-RNG and resupply persistence test) are Phase 2.
- **F-A-011** (Empire.resource_pool profiling) is Phase 3 alongside the wrapper retirement.
