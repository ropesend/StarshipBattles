# PROJ-450 Consolidated Findings

> Findings closed (or partially closed) by this project. Each entry copied from the archived bucket reports + a current-state verification line dated **2026-05-19**.
>
> Sources:
> - `Projects/archived_projects/PROJ-445/findings/bucket_b_engine_services_scan.md`
> - `Projects/archived_projects/PROJ-444/findings/bucket_a_data_facade_scan.md` (F-A-013 verification)
> - `AgentCoordination/discovered_issues/log.jsonl` (DI-2026-05-18-001 substrate half)
> - `Projects/archived_projects/PROJ-444to447_coordinator/stage_3_joint_a_preflight_findings.md` (310-occurrence audit)

---

## F-B-013 — `transfer_branches.py` flattens typed `DropPod` back to dict at the staging-yard boundary
- **Severity**: low-medium (tech debt, not user-facing functional risk today)
- **Category**: obsolete-code (typed `DropPod` substrate adoption is partial — boundary still dict)
- **File**: `game/strategy/engine/order_handlers/transfer_branches.py:416-446` (call sites); `game/strategy/data/planet.py:316-322` (substrate); `transfer_branches.py:41-87` (3 helpers)
- **Symbol**: `TransferBranches._dispatch_drop_pod_unload` + `Planet._staging_yard` / `Planet.add_to_staging_yard`
- **Source refactor**: PROJ-431 Phase 1d (typed `DropPod` in `bay_inventory.pods`) — staging-yard half deferred
- **What survived**: The docstring at line 412-417 explicitly says "The planet staging yard still consumes legacy dict shape, so the typed `DropPod` is flattened to a dict at the boundary." Same pattern at production_spawner.py:358 ("Drop pods retain their legacy dict shape"). The staging-yard substrate is `Planet._staging_yard: List[Dict[str, Any]]` while every other carried-vehicle storage uses typed `CarriedVehicle` / `DropPod`. The flatten/inflate round-trip is in `transfer_branches._staging_yard_carried_vehicle` (line 76-87) and `_pod_from_dict` (line 55-73).
- **Why it's a problem**: Inconsistent substrate forces a typed-to-dict-to-typed round-trip every time a pod crosses the boundary. Tech-debt risks: field drift between the typed dataclass and the dict payload schema; missing `mass` field if a pod is added through one path and read through another; the `_is_carried_vehicle_dict` runtime probe at line 213 / 348 is the kind of shape-discrimination the PROJ-431 work was designed to retire on the typed slots.
- **Suggested action**: Add a typed `Planet._staging_yard: List[CarriedVehicle | DropPod]` slot (or migrate the existing list to typed entries with a one-shot save-data normalization). Drop the `_staging_yard_carried_vehicle` probe and the `pod.payload`/`pod.design_data`/`pod.mass` flatten block.
- **Effort**: medium
- **CROSS-BUCKET CLASSIFICATION** (historical): STRUCTURAL JOINT-PHASE under the old PROJ-444..447 partition. Codex r4 redesign re-bundles into PROJ-450 as a single owner.
- **Status as of 2026-05-19**: open. Substrate at `planet.py:316-328` still `List[Dict[str, Any]]`. Closed by **PROJ-450 Phase 2** (substrate widening).

---

## DI-2026-05-18-001 — fleet-to-fleet drop_pod/vehicle transfer (engine substrate half)
- **Severity**: medium
- **Category**: bug (substrate half) → tech-debt after substrate widens
- **File**: `game/strategy/engine/order_handlers/transfer_branches.py:472-632`
- **Symbol**: `TransferBranches._dispatch_fleet_to_fleet`
- **Source refactor**: PROJ-425 (transfer handler lift) — substrate-typing half deferred
- **What survived (May 2026)**: PROJ-445 Phase 2 added explicit `_dispatch_fleet_to_fleet_drop_pod` / `_dispatch_fleet_to_fleet_vehicle` branches at `transfer_branches.py:472-632`. The user-visible bug is fixed (the silent no-op for `cargo_type in {'drop_pod', 'vehicle'}` is closed). Codex r4 audit at 2026-05-19 confirmed this is now `resolved`. The remaining substrate half: the new branches reach into `ship._cargo_mgr` directly (`transfer_branches.py:564`, `:607-629`) — that engine-side `ship._cargo_mgr` access is the substrate residue.
- **Why it's a problem**: The fleet-to-fleet branches operate on `ship._cargo_mgr` private slots. After substrate widening (PROJ-450 Phase 2), the migrations should route through the public typed API surface.
- **Suggested action**: PROJ-450 Phase 1 + 2 reconnects the engine-side calls to the new typed Planet API + the new `Planet.pop_staging_yard_typed` / typed `add_to_staging_yard` paths.
- **Effort**: small (lands as a byproduct of Phase 1)
- **Status as of 2026-05-19**: fleet-to-fleet user bug **resolved** (PROJ-445 Phase 2 + Codex r4 verification). Substrate cleanup half closed by **PROJ-450 Phase 1** (engine API cleanup) and **Phase 2** (substrate widening).

---

## F-A-013 — `FleetSlice._ship_container_snapshot` capacity projection — ALREADY COMPLETE
- **Severity**: low
- **Category**: polish
- **File**: `game/strategy/facade/slices/fleet_slice.py:165-191`
- **Symbol**: `_ship_container_snapshot` (module-level helper)
- **Source refactor**: PROJ-437 Phase 1a
- **What survived (May 2026)**: PROJ-444 Phase 2 Task 2.4 tightened the snapshot's capacity model on 2026-05-18. The function projects each ship's `bay_inventory` into a snapshot at the real bay capacity (no longer `inf` projection); the F-A-013 finding is closed at the code level.
- **Status as of 2026-05-19**: **complete**. Verify at `fleet_slice.py:165-191` in Phase 0 only — no PROJ-450 code change required. Cross-referenced here so the finding ledger stays complete; PROJ-450 inherits no action items from F-A-013.

---

## Stage 3 Joint A preflight — 310-occurrence audit (2026-05-18 → 2026-05-19 re-verification)

**Source**: `Projects/archived_projects/PROJ-444to447_coordinator/stage_3_joint_a_preflight_findings.md` §1.2 + §1.3.

**Audit re-verification at HEAD 2026-05-19**:
- `rg "staging_yard" game/`: 82 occurrences across 18 files (matches §1.3 expected count).
- `rg "staging_yard" tests/`: 228 occurrences across 31 files (matches §1.3 expected count).
- **Total: 310 occurrences across 49 files** — identical to the May 2026 audit.

**The 3 hard blockers from §2** (all still present at HEAD 2026-05-19):

### BLOCKER #1 — UI reader silently drops typed items
- **File**: `game/ui/screens/strategy_detail_fmt.py:285-297`
- **Verified at HEAD**: yes; the `isinstance(item, dict): continue` skip is at lines 286-290 (verified by direct read).
- **Closed by**: **PROJ-450 Phase 3** UI reader migration.

### BLOCKER #2 — Integration tests inject raw dicts via direct mutation
- **Files**:
  - `tests/integration/test_fms_planet_recovery.py:59` (1 site)
  - `tests/integration/test_fms_planet_lay_mines.py:82, 139, 155, 171` (4 sites)
  - `tests/integration/test_fms_planet_launch.py:92, 121, 157, 192` (4 sites)
  - `tests/integration/test_fms_a_e2e.py:305` (1 site)
- **Verified at HEAD**: yes; counts match preflight numbers.
- **Closed by**: **PROJ-450 Phase 4** integration test migration.

### BLOCKER #3 — Validator + write service do dict-shape probes
- **Files**: `game/strategy/validation/transfer_validator.py:228, 363-379`; `game/strategy/services/planet_write_service.py:100-105`
- **Verified at HEAD**: yes; the validator at `:363-379` has the explicit `if isinstance(item, CarriedVehicle): ... elif isinstance(item, dict) and ...` branch; the write service signatures still accept `Any`.
- **Closed by**: **PROJ-450 Phase 3** validator + write-service tightening.

### Save fixture (NOT a blocker, but a constraint)
- **File**: `tests/fixtures/saves/galaxy_proj372_populated.json` (17 staging_yard refs in dict form)
- **Constraint**: save format stays dict-shaped per CLAUDE.md "saves are disposable" interpretation. `_normalize_to_typed()` converts on load; `planet_to_dict` serializes each typed entry via `.to_dict()` on save. No edit required to the fixture file.

---

## Codex r4 redesign — PROJ-450 row

> 2. `Typed staging-yard substrate completion` - Convert `Planet._staging_yard` to the typed drop-pod/carried-vehicle substrate and remove the flatten/unflatten boundary in `transfer_branches`. Closes `F-B-013` and the remaining structural half of DI-001's transfer residue. Sequential. Depends on: `1` (shared `planet.py` / serde surface). Size: large.

The "Depends on: 1" dependency is critical. PROJ-449 Phase 3 (Planet wrapper + property cluster deletion) must land BEFORE PROJ-450 Phase 1 starts. The Phase 0 audit verifies this precondition.
