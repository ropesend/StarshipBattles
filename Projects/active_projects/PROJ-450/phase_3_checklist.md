# Phase 3: UI reader migration + DTO / validator / write-service tightening

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-450 3`
> 2. Sharded suite green
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Depends on:** phase_2 (typed substrate in place; dict-projection bridge alive)
**Objective:** Migrate the UI reader at `game/ui/screens/strategy_detail_fmt.py:285-297` to read typed entries. Migrate 5 dict-injection fixture tests at `tests/unit/ui/screens/test_strategy_detail_fmt.py:915-1009`. Tighten `IPlanetMutator.add_staging_item` / `pop_staging_item` signatures. Drop validator shape probes. Then **replace the Phase-2 dict-projection bridge with a permanent typed read-only property** `Planet.staging_yard -> Tuple[CarriedVehicle | DropPod, ...]` so external readers (`game/ui/screens/strategy_detail_fmt.py`, `game/strategy/facade/slices/planet_slice.py`, `game/strategy/facade/dto/planet_dto.py`) keep a stable public surface — but mutations now require routing through `add_to_staging_yard` / `pop_staging_yard_typed` / `remove_from_staging_yard` (no setter, no list-mutation through the public name).

**File ownership rule:** Phase 3 touches UI reader + UI tests + validator + write service + facade slice + DTO + the Phase-2 bridge cleanup. No engine handler changes (those landed in Phase 1).

**Source-of-truth findings:** Stage 3 preflight §2.1 / §2.3 BLOCKER #1 + #3 — see [findings/PROJ-450_findings.md](findings/PROJ-450_findings.md).

---

## Tasks

### Task 3.1: RED — UI reader typed-input contract test [Simple]
**File:** `tests/unit/ui/screens/test_strategy_detail_fmt.py` (extend)
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py -q`

- [x] Add new test cases mirroring `test_staging_yard_renders_inline_after_complexes_before_energy` (line 915) but with TYPED fixtures:
  ```python
  def test_staging_yard_renders_typed_carried_vehicle(self, mock_planet):
      from game.strategy.data.carried_vehicle import CarriedVehicle
      mock_planet.staging_yard = [
          CarriedVehicle(design_id="mk1_mine", vehicle_type="mine", design_data={"name": "Mk1 Mine"}, mass=5.0),
          CarriedVehicle(design_id="mk1_mine", vehicle_type="mine", design_data={"name": "Mk1 Mine"}, mass=5.0),
      ]
      # ... assert " - Mk1 Mine x2 (Staged)" in result
  ```
- [x] Add `test_staging_yard_renders_typed_drop_pod`
- [x] Run; expect failures (the UI reader still does `isinstance(item, dict): continue` and silently skips typed entries)

### Task 3.2: GREEN — migrate the UI reader [Medium]
**File:** `game/ui/screens/strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py -q`

- [x] Locate the staging-yard read at lines 285-297. Current:
  ```python
  staging_yard = getattr(planet, "staging_yard", None)
  if isinstance(staging_yard, list) and staging_yard:
      group_counts: dict[tuple, int] = {}
      for item in staging_yard:
          if not isinstance(item, dict):
              continue
          key = (item.get("name", "Unknown"), item.get("vehicle_type", "unknown"))
          group_counts[key] = group_counts.get(key, 0) + 1
  ```
- [x] Replace with typed-aware reader. **CRITICAL** (codex r5 review 2026-05-19): the Task 3.4 property returns `tuple[CarriedVehicle | DropPod, ...]`, NOT a `list`. The reader must NOT use `isinstance(staging_yard, list)` — a tuple fails that check and the entire block silently no-ops, hiding all staging contents in the UI. Use a truthy check or `isinstance(..., (list, tuple))`:
  ```python
  from game.strategy.data.carried_vehicle import CarriedVehicle
  from game.strategy.data.drop_pod import DropPod  # verify import path
  staging_yard = getattr(planet, "staging_yard", None)
  # NOTE: Task 3.4 typed property returns tuple, NOT list. Truthy check
  # (or isinstance(..., (list, tuple))) — never `isinstance(..., list)` alone.
  if staging_yard:
      group_counts: dict[tuple, int] = {}
      for item in staging_yard:
          if isinstance(item, CarriedVehicle):
              name = item.design_data.get("name", "Unknown") if item.design_data else item.design_id
              vtype = item.vehicle_type
          elif isinstance(item, DropPod):
              name = item.payload.get("name", "Unknown")
              vtype = item.payload.get("vehicle_type", "drop_pod")
          elif isinstance(item, dict):
              # Tolerance for legacy mocks (PROJ-450 Phase 3 retained behavior)
              name = item.get("name", "Unknown")
              vtype = item.get("vehicle_type", "unknown")
          else:
              continue
          key = (name, vtype)
          group_counts[key] = group_counts.get(key, 0) + 1
  ```
- [x] The dict branch stays for backward compatibility with mock fixtures (some tests at lines 993-1009 specifically test non-dict tolerance and dict-mock tolerance — keep those green)
- [x] Run focused tests
- [x] **Codex r5 verification step:** read `game/ui/screens/strategy_detail_fmt.py:285-297` AFTER your edit and confirm the `isinstance(..., list)` check is gone everywhere. Same check pattern may also exist in `tests/unit/ui/screens/test_strategy_detail_fmt.py` mock-injection sites — those tests need to be consistent with the new reader shape.

### Task 3.3: GREEN — migrate 5 dict-injection fixture tests [Medium]
**File:** `tests/unit/ui/screens/test_strategy_detail_fmt.py`
**Tests:** `pytest tests/unit/ui/screens/test_strategy_detail_fmt.py -q`

- [x] Migrate the 3 dict-injection tests at lines 915-961 to construct typed `CarriedVehicle` / `DropPod` fixtures instead of dict literals. Keep one as a backward-compat "dict-tolerance" test (the one at line 944).
- [x] Verify the existing tests `test_empty_staging_yard_omits_header`, `test_missing_staging_yard_attr_is_safe`, `test_non_dict_staging_yard_entries_silently_ignored` (lines 963-1009) still pass — those test edge cases (empty list / missing attr / mixed non-dict tolerance) and should be unaffected by the migration

### Task 3.4: GREEN — replace the Phase-2 dict-projection bridge with a typed read-only property [Simple]
**File:** `game/strategy/data/planet.py`
**Tests:** `pytest tests/unit/strategy/data/test_planet_staging_yard_typed_api.py tests/unit/ui/screens/test_strategy_detail_fmt.py -n 4 -q`

- [x] Replace the temporary `@property staging_yard` (dict-projection) added in Phase 2 Task 2.2 with a **permanent typed read-only property**:
  ```python
  @property
  def staging_yard(self) -> "tuple[CarriedVehicle | DropPod, ...]":
      """Typed read-only view of the staging-yard substrate.

      PROJ-450 Phase 3 (Option A): replaces the Phase-2 dict-projection
      bridge with a permanent typed read-only tuple. External readers
      (UI / facade / DTO) iterate over this property; mutations MUST
      route through ``add_to_staging_yard`` / ``pop_staging_yard_typed``
      / ``remove_from_staging_yard``. There is no setter — assigning to
      ``planet.staging_yard`` raises AttributeError.
      """
      return tuple(self._staging_yard)
  ```
- [x] **Do NOT add a setter.** Any test or production code that previously did `planet.staging_yard = [...]` MUST route through the write API instead.
- [x] The Phase-2 dict-projection bridge (`[item.to_dict() for item in self._staging_yard]`) is GONE; the new property hands out typed objects directly. The migrated UI reader (Task 3.2) is the matching read-side change.
- [x] **Migration verification:** confirm Task 3.2 + Task 3.3 (UI reader) and Task 3.7 (facade slice + DTO) have all landed before this task — otherwise readers see typed objects but their code still expects dicts. See Phase 3 sequencing note below.

**Note (2026-05-19 codex BLOCKER #1 fix):** The earlier draft of this task said "delete the Phase-2 bridge" — but PROJ-449 Phase 3 deleted the original Planet @property staging_yard, so a pure deletion here would leave readers (UI / facade / DTO) seeing `None` via `getattr(planet, "staging_yard", None)`, silently breaking the planet detail panel and staging-yard summaries. Option A keeps a typed read-only property as the permanent public surface; mutations go through the write API. See decisions.md row 2026-05-19 "Codex BLOCKER #1 = Option A: permanent typed read-only property."

### Task 3.5: GREEN — tighten `IPlanetMutator` and write service signatures [Medium]
**Files:** `game/strategy/services/planet_write_service.py`, `game/core/protocols/strategy_mutators.py` (`IPlanetMutator.add_staging_item` at line 105, currently `item: Any`)
**Tests:** `pytest tests/unit/strategy/services/ -n 4 -q`

- [x] At `planet_write_service.py:100-105`, change:
  ```python
  def add_staging_item(self, planet: "Planet", item: Any) -> None:
      planet.add_to_staging_yard(item)

  def pop_staging_item(self, planet: "Planet", index: int = 0) -> Any:
      return planet.remove_from_staging_yard(index)
  ```
  to:
  ```python
  def add_staging_item(
      self,
      planet: "Planet",
      item: "CarriedVehicle | DropPod",
  ) -> None:
      planet.add_to_staging_yard(item)

  def pop_staging_item(
      self,
      planet: "Planet",
      index: int = 0,
  ) -> "CarriedVehicle | DropPod | None":
      return planet.pop_staging_yard_typed(index)
  ```
- [x] Update the `IPlanetMutator` protocol signature accordingly
- [x] Run focused tests

### Task 3.6: GREEN — drop validator shape probes + fix broad-catch markers [Medium]
**File:** `game/strategy/validation/transfer_validator.py`
**Tests:** `pytest tests/unit/strategy/validation/ -n 4 -q`

- [x] At lines 363-379, the existing branch:
  ```python
  for item in staging:
      if isinstance(item, CarriedVehicle):
          cv = item
      elif isinstance(item, dict) and str(item.get("vehicle_type", "")).lower() in VALID_VEHICLE_TYPES:
          cv = CarriedVehicle.from_dict(item)
      else:
          continue
  ```
  Now that the substrate is typed, simplify to:
  ```python
  for item in staging:
      if isinstance(item, CarriedVehicle):
          cv = item
      else:
          continue  # DropPod or other typed entry — not a CarriedVehicle
  ```
- [x] At line 228, the count probe `staging = getattr(planet, 'staging_yard', [])` stays the same in shape — but note this now defaults to `[]` for a missing attr, while the typed property returns `tuple()`. Either default works for `len()`; keep `[]` for backward compatibility with mocks that may not provide a `staging_yard` attr.
- [x] **Codex r5 NEW-3:** at `transfer_validator.py:393` and `:423`, two `except Exception:` blocks use weaker `# Intentional:` instead of the convention-required `# Intentional broad catch: <reason>` marker (per `docs/03_CONVENTIONS.md`). Replace both `# Intentional:` markers with `# Intentional broad catch: <reason>` matching the existing reason text. No behavior change.
- [x] Run focused tests

### Task 3.7: GREEN — migrate facade slice + DTO summary builder [Medium]
**Files:** `game/strategy/facade/slices/planet_slice.py`, `game/strategy/facade/dto/planet_dto.py`
**Tests:** `pytest tests/unit/strategy/facade/slices/test_planet_slice.py tests/unit/strategy/facade/test_container_snapshots.py -n 4 -q`

- [x] At `planet_slice.py:194-213`, replace any `item.get(...)` reads with typed attribute access:
  - `item.get("design_id", ...)` → `item.design_id`
  - `item.get("vehicle_type", ...)` → `item.vehicle_type if isinstance(item, CarriedVehicle) else item.payload.get(...)` (DropPod doesn't have a top-level vehicle_type field)
- [x] At `planet_dto.py:99-112`, update `staging_yard_summary` builder to use typed attribute access
- [x] Run focused tests

### Task 3.8: Sharded suite + commit [Medium]
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Sharded suite green
- [x] Commit message: `PROJ-450 Phase 3: migrate UI reader to typed staging-yard; tighten validator / write service / facade signatures; drop Phase-2 projection bridge`

---

## Phase Completion Checklist
- [x] UI reader at `strategy_detail_fmt.py:285-297` reads typed entries (with dict-tolerance for mock fixtures)
- [x] 5 dict-injection fixture tests migrated to typed fixtures (or kept as backward-compat where intentional)
- [x] Phase-2 dict-projection bridge REPLACED by a permanent typed read-only `Planet.staging_yard -> Tuple[CarriedVehicle | DropPod, ...]` property (Option A)
- [x] `IPlanetMutator.add_staging_item` / `pop_staging_item` signatures tightened
- [x] Validator shape probes simplified
- [x] Facade slice + DTO use typed attribute access
- [x] Sharded suite green
- [x] Plan.md Quick Status → Complete; Current State updated

## Notes / Risks / Coordination Touchpoints
- **Mock-fixture tolerance kept.** The `test_non_dict_staging_yard_entries_silently_ignored` test at lines 993-1009 deliberately exercises the "non-dict entries skipped silently" path. The new typed reader still handles this via the `else: continue` branch — that contract is preserved.
- **`isinstance(item, dict)` branch retained.** Real mocks (where a test passes raw dicts to bypass the typed normalization in `add_to_staging_yard`) still need to render. Per the UI reader migration: "The dict branch stays for backward compatibility with mock fixtures."
- **Risk: a test that depended on the projection property returning `List[Dict]`.** After Phase 3 deletes the property, callers that did `for item in planet.staging_yard: item.get(...)` will fail. Phase 2's introduction of the projection was deliberate so this risk surfaces in Phase 3, not Phase 2. Mitigation: any straggler that surfaces in Task 3.8 sharded run gets fixed before commit.
- **`DropPod` import path needs verification.** The class is currently constructed via `transfer_branches._pod_from_dict(...)` returns. Locate the canonical import path (likely `game/strategy/data/drop_pod.py` or a sibling module under `game/strategy/data/`).
