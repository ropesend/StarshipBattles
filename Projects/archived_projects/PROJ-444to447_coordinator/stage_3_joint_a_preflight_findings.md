# Stage 3 Joint A — Pre-flight Findings Report

**Author:** Claude (PROJ-444 / PROJ-445 Joint A agent)
**Date:** 2026-05-18
**Status:** STOPPED before code change — surfacing scope mismatch to coordinator
**Scope of this report:** PROJ-444 F-A-013 (substrate half) + PROJ-445 F-B-013 + DI-2026-05-18-001 substrate half
**TL;DR:** The literal Joint A task (typed `_staging_yard` substrate) cannot be completed inside the Joint A cross-bucket exception (PROJ-444 data/facade + PROJ-445 engine). Two unavoidable reader sites live in PROJ-446 / unowned territory; widening the substrate without coordinating those readers either (a) silently regresses the planet detail UI, or (b) requires a back-compat shim that violates CLAUDE.md. Recommended path: **defer literal substrate widening to a four-way joint phase** (444 + 445 + 446 + integration-tests-root owner) and land **engine-only API cleanup** in this session as a partial Joint A.

---

## 1. Pre-flight context

### 1.1 Joint A entry conditions met

- `python Projects/scripts/current_task.py PROJ-444` → Phase 2 complete, Current State block points at Phase 3.
- `python Projects/scripts/current_task.py PROJ-445` → Phase 2 complete, two documented partial deferrals (engine-side RESOURCE_SHORTAGE emit + ShipInstance delegators).
- F-A-013 (`_ship_container_snapshot` capacity tightening) is **already done** in [`game/strategy/facade/slices/fleet_slice.py:165-191`](../../../game/strategy/facade/slices/fleet_slice.py) — landed in PROJ-444 Phase 2 Task 2.4 (2026-05-18). Stage 3-A-3 is therefore already complete; Joint A's remaining work is Stage 3-A-1 / 3-A-2 / 3-A-4.
- DI-2026-05-18-001's user-visible bug (fleet-to-fleet drop_pod/vehicle silent no-op) is **already fixed** in [`transfer_branches.py:525-549`](../../../game/strategy/engine/order_handlers/transfer_branches.py) by PROJ-445 Phase 2's `_dispatch_fleet_to_fleet_drop_pod` / `_dispatch_fleet_to_fleet_vehicle` branches. Joint A's residual work is the substrate-typing half — internal bookkeeping cleanup, not user-visible behavior.

### 1.2 Audit: `rg "staging_yard" game/ tests/`

**Raw totals:**
- **310 occurrences** across **49 active files** (excluding archived `Projects/`, `Reviews/`, `_marked_for_deletion_*`, `docs/`).
- Task spec STOP threshold: *"more than ~20 call sites suggests substrate coupling deeper than the finding scoped."* We are at **~15× the threshold by file count and ~15× by occurrence count**.

**Direct mutations of `planet.staging_yard` (the substrate that would change):**

| Site                                                                 | Operation       | Partition          |
| -------------------------------------------------------------------- | --------------- | ------------------ |
| `game/strategy/data/planet.py:321`                                   | `append`        | PROJ-444 ✓          |
| `game/strategy/data/planet.py:327`                                   | `pop`           | PROJ-444 ✓          |
| `tests/integration/test_fms_a_e2e.py:305`                            | `.clear()`      | **unowned**         |
| `tests/integration/test_fms_planet_recovery.py:59`                   | `.append(item)` | **unowned**         |
| `tests/integration/test_fms_planet_launch.py:92, 121, 157, 192`      | `.append/.extend` | **unowned**       |
| `tests/integration/test_fms_planet_lay_mines.py:82, 139, 155, 171`   | `.append`       | **unowned**         |
| `tests/unit/strategy/engine/test_pod_transfer.py:45, 54`             | `.append/.pop`  | PROJ-445 (engine)   |
| `tests/unit/strategy/engine/order_handlers/test_transfer_handler.py:227, 443` | `.pop`  | PROJ-445 (engine)   |
| `tests/unit/strategy/engine/test_order_processor_transfer.py:411`    | `.pop`          | PROJ-445 (engine)   |
| `tests/unit/strategy/engine/test_staging_yard_operations.py:69`      | `.pop`          | PROJ-445 (engine)   |
| `tests/unit/strategy/data/test_mutator_boundary_ast_guard_self_test.py:36` | `.clear()` | PROJ-444 ✓        |

The `tests/integration/test_fms_planet_*` cluster (4 files, 9+ direct mutations) is the killer for the "fully-typed substrate" path — see §2 below.

### 1.3 Per-file reference counts (top 30, full audit recorded)

```
21  tests/unit/strategy/engine/test_pod_transfer.py
20  tests/unit/strategy/engine/test_production_spawner_staging_yard.py
19  game/strategy/data/planet.py
18  game/strategy/engine/order_handlers/transfer_branches.py
17  tests/unit/strategy/engine/test_staging_yard_operations.py
17  tests/unit/strategy/engine/test_production_spawner.py
17  tests/unit/strategy/engine/order_handlers/test_transfer_handler.py
17  tests/fixtures/saves/galaxy_proj372_populated.json       ← save fixture, dict-shape
13  tests/unit/ui/screens/test_strategy_detail_fmt.py        ← PROJ-446 ✗
12  tests/unit/strategy/engine/test_issuer_adapter.py
12  tests/integration/test_fms_planet_launch.py              ← unowned ✗
10  tests/unit/strategy/engine/test_order_processor_transfer.py
 9  tests/integration/test_fms_planet_recovery.py            ← unowned ✗
 8  tests/static_guards/test_no_legacy_storage_fields.py     ← PROJ-446 ✗ (static guard re-checked: doesn't pin TYPE)
 8  game/strategy/engine/issuer_adapter.py
 7  tests/unit/strategy/facade/test_container_snapshots.py
 7  tests/integration/test_fms_planet_lay_mines.py           ← unowned ✗
 6  tests/unit/strategy/engine/test_production_normalisation.py
 5  tests/unit/strategy/data/test_vehicle_bay.py
 5  tests/integration/test_fms_a_e2e.py                      ← unowned ✗
 5  game/strategy/validation/transfer_validator.py           ← partition unclear (see §2.3)
 4  tests/unit/strategy/data/test_planet_fleet_empire_post_436_contract.py
 4  game/strategy/facade/slices/planet_slice.py
 4  game/strategy/facade/dto/planet_dto.py
 4  game/strategy/data/galaxy_protocols.py
 3  tests/unit/strategy/data/test_mutator_boundary_ast_guard.py
 3  tests/static_guards/test_no_legacy_protocol_names.py     ← PROJ-446 ✗
 3  game/ui/screens/strategy_detail_fmt.py                   ← PROJ-446 ✗
 3  game/strategy/services/planet_write_service.py
 3  game/strategy/engine/production_spawner.py
```

---

## 2. Hard blockers — call sites that prevent literal substrate widening within Joint A

### 2.1 BLOCKER #1 — UI reader silently drops typed items (PROJ-446)

**File:** [`game/ui/screens/strategy_detail_fmt.py:285-297`](../../../game/ui/screens/strategy_detail_fmt.py)

```python
staging_yard = getattr(planet, "staging_yard", None)
if isinstance(staging_yard, list) and staging_yard:
    group_counts: dict[tuple, int] = {}
    for item in staging_yard:
        if not isinstance(item, dict):
            continue                                        # ← typed objects fall here
        key = (item.get("name", "Unknown"), item.get("vehicle_type", "unknown"))
        group_counts[key] = group_counts.get(key, 0) + 1
    if group_counts:
        text += "<br><b>Staged Units:</b><br>"
        for (name, _vtype), count in sorted(group_counts.items()):
            suffix = f" x{count}" if count > 1 else ""
            text += f" - {name}{suffix} (Staged)<br>"
```

If `_staging_yard` becomes `List[CarriedVehicle | DropPod]` and the `staging_yard` property returns the typed list verbatim:
- `isinstance(item, dict)` returns `False` for every entry.
- `continue` skips them all.
- `group_counts` stays empty.
- The "Staged Units:" header is omitted.
- **The planet detail panel silently renders a colony with mines/fighters/satellites/pods as if its staging yard were empty.** No exception, no log line — silent UI regression.

**Companion test pinning the dict shape:** [`tests/unit/ui/screens/test_strategy_detail_fmt.py:928-960`](../../../tests/unit/ui/screens/test_strategy_detail_fmt.py) — three test cases assemble `mock_planet.staging_yard = [{"name": ..., "vehicle_type": ...}]` and assert on the rendered HTML. After substrate widening, these tests still pass (the mock injects dicts directly, bypassing the `add_to_staging_yard` normalization), but the real production path stops feeding the UI.

**Why this is unavoidable from inside Joint A:** Both files are explicitly listed under PROJ-446's ownership ("game/ui/** + tests/unit/ui/**"). Joint A's cross-bucket exception extends to PROJ-445 engine only — not PROJ-446 UI.

### 2.2 BLOCKER #2 — Integration tests inject raw dicts via direct mutation (unowned)

**Files:**
- [`tests/integration/test_fms_planet_recovery.py:59`](../../../tests/integration/test_fms_planet_recovery.py)
- [`tests/integration/test_fms_planet_lay_mines.py:82, 139, 155, 171`](../../../tests/integration/test_fms_planet_lay_mines.py)
- [`tests/integration/test_fms_planet_launch.py:92, 121, 157, 192`](../../../tests/integration/test_fms_planet_launch.py)
- [`tests/integration/test_fms_a_e2e.py:305`](../../../tests/integration/test_fms_a_e2e.py)

Representative shape:

```python
# test_fms_planet_lay_mines.py:139
planet.staging_yard.append(_mine_dict())

# test_fms_planet_launch.py:121
planet.staging_yard.extend(_fighter_dict(hp=80 - i * 5) for i in range(3))
```

These bypass `add_to_staging_yard` entirely. If `staging_yard` becomes a property that returns a **dict-projection copy** (the only way to preserve UI compat — see §3.3), these `.append` / `.extend` mutations operate on a throwaway list and are lost. The tests stop exercising the real substrate.

If we instead make the property return the **raw typed list**, the integration tests inject `dict` instances into a typed-only list, breaking the type invariant; they'd be silently appended (no isinstance enforcement in `list.append`) but downstream typed-only consumers would crash.

**Partition status:** `tests/integration/test_fms_*` at the `tests/integration/` root is not under any of the four cross-bucket partitions (PROJ-444's allowed test scope is `tests/{unit,integration}/strategy/{data,facade}/` + `tests/integration/save_load/`; PROJ-446 explicitly carves out `tests/fixtures/`, `tests/static_guards/`, `tests/regression/`; engine tests live under `tests/unit/strategy/engine/`). These root-level integration tests have no listed owner. The Joint A spec only granted me cross-bucket access to PROJ-445 engine code/tests.

### 2.3 BLOCKER #3 — Validator and write service do dict-shape probes (partition unclear)

**File:** [`game/strategy/validation/transfer_validator.py:228, 363-379`](../../../game/strategy/validation/transfer_validator.py)

Lines 363-379 explicitly probe both shapes today:

```python
for item in staging:
    if isinstance(item, CarriedVehicle):
        cv = item
    elif isinstance(item, dict) and str(item.get("vehicle_type", "")).lower() in VALID_VEHICLE_TYPES:
        cv = CarriedVehicle.from_dict(item)
    else:
        continue
```

This is *the same anti-pattern* Joint A is trying to remove — a runtime shape probe at a boundary that the typed substrate is supposed to eliminate.

**File:** [`game/strategy/services/planet_write_service.py:100-105`](../../../game/strategy/services/planet_write_service.py)

```python
def add_staging_item(self, planet: "Planet", item: Any) -> None:
    planet.add_to_staging_yard(item)

def pop_staging_item(self, planet: "Planet", index: int = 0) -> Any:
    return planet.remove_from_staging_yard(index)
```

`IPlanetMutator` accepts `Any` items. The signature would tighten when the typed substrate lands — but mutator callers in PROJ-445 engine + PROJ-446 UI would all need to match the new shape.

**Partition status of `game/strategy/validation/`:** Not explicitly enumerated in any of the four projects' file-ownership rules. PROJ-445's Phase 2 touched this directory ([`tests/unit/strategy/validation/test_transfer_drop_pod.py`](../../../tests/unit/strategy/validation/test_transfer_drop_pod.py)), so it is arguably engine-adjacent and within Joint A's cross-bucket scope. Logged here for the coordinator to confirm.

### 2.4 Save fixture file pins the dict shape

**File:** [`tests/fixtures/saves/galaxy_proj372_populated.json`](../../../tests/fixtures/saves/galaxy_proj372_populated.json) (17 staging_yard refs)

Existing save fixture stores staging-yard entries as dicts. The serializer rewrite required by Stage 3-A-1 must round-trip via a `_normalize_to_typed()` helper on load — that's fine, but it confirms the save format must stay dict-shaped (CLAUDE.md's "saves are disposable" rule applies to old saves, not to the canonical on-disk format).

**Partition status:** `tests/fixtures/` is explicitly carved out by PROJ-446 as out-of-scope. If we need to regenerate this fixture (we shouldn't, since serde would normalize on load), it would be a cross-bucket touch.

---

## 3. Three paths forward — concrete trade-offs

### 3.1 Path A — **Engine-only API cleanup (RECOMMENDED for this session)**

**What changes:**
- Keep `_staging_yard: List[Dict[str, Any]]` substrate unchanged.
- Widen `Planet.add_to_staging_yard(item)` to accept `Dict | CarriedVehicle | DropPod`. Internally normalize to dict via `.to_dict()`.
- Add new `Planet.pop_staging_yard_typed(index) -> CarriedVehicle | DropPod | None` that returns the typed equivalent of the popped dict (using `vehicle_type` to discriminate, mirroring `_pod_from_dict` / `_staging_yard_carried_vehicle`).
- Engine handlers in `transfer_branches.py` / `production_spawner.py` / `issuer_adapter.py` stop their `_pod_from_dict` / `_staging_yard_carried_vehicle` / `cv.to_dict()` flatten/inflate by routing through the new typed API.
- The `_pod_from_dict` / `_staging_yard_carried_vehicle` / `_is_carried_vehicle_dict` helpers in `transfer_branches.py:41-87` move into `Planet` as private helpers (single source of truth for the dict↔typed mapping).
- Save format unchanged; UI reader unchanged; integration tests unchanged.

**What is closed:**
- Engine-side bookkeeping repetition (the literal flatten/inflate calls at the engine boundary). The dict↔typed conversion still happens, but it's centralized inside `Planet`, not duplicated in three engine files.
- DI-2026-05-18-001 substrate half is **partially** resolved — the engine call sites stop their own flatten/inflate, but the substrate itself stays dict-typed.
- F-B-013 in PROJ-445 is **partially** resolved — engine call-site adoption done, substrate widening deferred.

**What is NOT closed:**
- Literal typed substrate (`_staging_yard: List[CarriedVehicle | DropPod]`). F-A-013's substrate half remains open as a deferred follow-up.
- `transfer_validator.py:363-379` shape probe — could be cleaned up in this session via the new typed pop API, but the probe at line 228 (`getattr(planet, 'staging_yard', [])` followed by `len(staging)`) is a count-only check that doesn't care about shape.
- Future "drop_pod"-only or "vehicle"-only typed contracts.

**Estimated effort:** 1-2 hours at LLM pace. ~80 LOC in `planet.py`, ~40 LOC simplification in `transfer_branches.py`, ~20 LOC in `issuer_adapter.py`, ~20 LOC in `production_spawner.py`. Two new integration tests for Stage 3-A-4. Zero file changes outside data/facade/engine. **Within Joint A's permission envelope.**

**Risks:**
- CLAUDE.md's "no compatibility shims" rule could be argued to apply to the new `pop_staging_yard_typed` method — it exists *because* the substrate isn't fully typed. Counter-argument: it's a deliberate single-source-of-truth API that ELIMINATES three duplicate helper functions, so it's a refactor, not a shim.

### 3.2 Path B — **Stop entirely; schedule full four-way joint phase**

**What changes:** Nothing in this session. Document blockers in `decisions.md` for PROJ-444, PROJ-445, PROJ-446 and (a new) coordinator project. Hand off to a future joint phase that bundles:
- PROJ-444 substrate change (Planet, planet_serde, planet_slice, planet_dto)
- PROJ-445 engine call-site adoption (transfer_branches, issuer_adapter, production_spawner, validator)
- PROJ-446 UI reader + UI test fixture migration (strategy_detail_fmt + its tests, transfer_dialog_characterization, transfer_view_model_container, planet_report_panel)
- Integration-test owner (likely PROJ-446 since these tests cover end-to-end FMS flows): migrate the `tests/integration/test_fms_planet_*` direct `.append`/`.extend` mutations to typed inputs or to the public `add_to_staging_yard` API.

**Pros:**
- Literal F-B-013 / F-A-013 substrate half closed in one coordinated PR.
- No back-compat shim.
- Save format change (if any) is a single coordinated event.

**Cons:**
- Stage 3 Joint A makes zero progress this session.
- Requires a coordinator who can schedule all four sibling agents and ensure the PR sequences correctly.
- The "deeper than scoped" framing in the task spec implicitly anticipates this outcome — the spec wrote a STOP condition for exactly this case.

### 3.3 Path C — **Full substrate widening with dict-projection compat shim (NOT recommended)**

**What changes:**
- `_staging_yard: List[CarriedVehicle | DropPod]` — typed internal.
- `staging_yard` PROPERTY returns `[item.to_dict() if hasattr(item, 'to_dict') else item for item in self._staging_yard]` — dict-projection list.
- `staging_yard` SETTER normalizes incoming dicts to typed via `_promote_to_typed`.
- `add_to_staging_yard(item)` accepts both; normalizes to typed.
- `remove_from_staging_yard(index)` returns typed.
- Engine handlers drop their flatten/inflate.
- UI reader keeps working (sees dict-projection).
- **Direct mutations like `planet.staging_yard.append(dict)` BREAK silently** — the mutation hits the throwaway projection list, never reaching `_staging_yard`. The 9+ integration test sites listed in §2.2 stop exercising the substrate, and any production code path that mutates via the property would silently fail.

**Why "NOT recommended":**
- CLAUDE.md explicitly forbids compatibility shims. The dict-projection property is a textbook compat shim.
- The silent-mutation-loss failure mode is exactly the class of bug DI-2026-05-18-001 was filed for. Trading one silent no-op for another is a net loss for the codebase's predictability.
- The audit-then-decide STOP condition in the task spec exists to prevent this kind of "ship the shim and hope nobody notices" outcome.

---

## 4. Recommendation

**Land Path A (engine-only API cleanup) in this session.** Update both project plans to:

1. Mark **Stage 3-A-3 / F-A-013 snapshot tightening** as already complete (landed in PROJ-444 Phase 2).
2. Mark **DI-2026-05-18-001 substrate half** as `partially-resolved` in `log.jsonl` — engine call-site adoption done, substrate typing deferred.
3. Mark **PROJ-445 F-B-013** as `partially-resolved` in PROJ-445 decisions.md.
4. **Open a new joint-phase placeholder** in `Projects/active_projects/PROJ-444to4447 coordinator/` (this directory) for the four-way coordinated PR that finishes substrate typing. Suggested name: `joint_a2_typed_staging_yard.md`. Pre-flight blockers listed above are the input to that joint.

Then explicitly **defer Joint B (wrapper retirement)** per the original Stage 3 instructions.

### 4.1 What Path A's deliverables look like

#### Stage 3-A-1 (revised scope)

- [ ] `Planet.add_to_staging_yard(item)` accepts `Dict | CarriedVehicle | DropPod`; normalizes to dict internally (single normalization site).
- [ ] New `Planet.pop_staging_yard_typed(index) -> CarriedVehicle | DropPod | None` — returns typed view of popped entry.
- [ ] Move `_pod_from_dict` / `_staging_yard_carried_vehicle` / `_is_carried_vehicle_dict` from `transfer_branches.py:41-87` into `planet.py` as private module-level helpers (or class methods).
- [ ] New unit test `tests/unit/strategy/data/test_planet_staging_yard_typed_api.py` covering: typed input → stored as dict; pop returns correct typed type by discriminator; unknown vehicle_type → DropPod fallback.

#### Stage 3-A-2 (revised scope)

- [ ] `transfer_branches.py`: drop `_pod_from_dict` (line 55-73), `_staging_yard_carried_vehicle` (line 76-87), `_is_carried_vehicle_dict` (line 41-52); replace call sites with `planet.pop_staging_yard_typed(i)` / `planet.add_to_staging_yard(cv)` direct typed passes.
- [ ] `transfer_branches.py:412` — drop `planet.add_to_staging_yard(cv.to_dict())`, change to `planet.add_to_staging_yard(cv)`.
- [ ] `transfer_branches.py:454-460` — drop the `pod_dict = dict(pod.payload); pod_dict["design_id"] = ...; planet.add_to_staging_yard(pod_dict)` flatten block; change to `planet.add_to_staging_yard(pod)`.
- [ ] `production_spawner.py:347-360` — keep the dict construction (it's the producer side; the new `add_to_staging_yard` accepts dicts fine) OR migrate to typed `CarriedVehicle(...) / DropPod(...)` construction. Decision: keep dict for now; cleaner once substrate is fully typed.
- [ ] `issuer_adapter.py:130-143` `_matches` shape probe — KEEP. The adapter intentionally accepts both shapes today; the dict path is exercised by current substrate. Re-evaluate when substrate is fully typed.
- [ ] `issuer_adapter.py:363` — `vehicle.to_dict()` flatten before `add_to_staging_yard` — drop, change to `add_to_staging_yard(vehicle)`.

#### Stage 3-A-3

- [ ] Already complete in PROJ-444 Phase 2 Task 2.4. Confirm via diff at [`fleet_slice.py:165-191`](../../../game/strategy/facade/slices/fleet_slice.py).

#### Stage 3-A-4

- [ ] New integration test `tests/integration/strategy/facade/test_fleet_to_fleet_drop_pod.py` (lives in my partition under `tests/integration/strategy/facade/`) — verifies the fleet-to-fleet pod path that PROJ-445 Phase 2 already fixed continues to work after Path A's engine cleanup.
- [ ] New integration test `tests/integration/strategy/facade/test_planet_to_fleet_drop_pod_typed.py` — fleet unloads a typed `DropPod` to planet; pops it back; asserts the popped value (via `pop_staging_yard_typed`) is a `DropPod` instance with the original `design_id`/`mass`/`payload`.

---

## 5. Status snapshot for the coordinator

| Project   | Phase | Stage 3 Joint A status                                      | Notes                                                                                                              |
| --------- | ----- | ----------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| PROJ-444  | 2 done | F-A-013 already complete (Phase 2 Task 2.4); substrate widening blocked. | Recommend Path A (engine API cleanup) in this session.                                                              |
| PROJ-445  | 2 done | F-B-013 substrate-typing half blocked; fleet-to-fleet bug (DI-001 main symptom) already closed by Phase 2.            | Recommend Path A engine cleanup completes the call-site bookkeeping half.                                           |
| PROJ-446  | n/a   | Out of Joint A's permission envelope.                       | Will need to be included in a future four-way joint phase if literal substrate typing is to land. Owns UI reader + UI test + static guards. |
| PROJ-447  | n/a   | Not involved.                                               | docs / sim / AI partition unaffected.                                                                              |
| Integration-test root (`tests/integration/test_fms_*`) | n/a | Unowned. | 4 files, 9+ direct `.append`/`.extend` sites. Needs a coordinator decision on ownership before substrate widening can land cleanly. |

---

## 6. Concrete file inventory for the deferred four-way joint phase

For convenience when the coordinator schedules the next joint, here is the full set of files that would need to migrate in lockstep for literal typed-substrate:

**PROJ-444 (data + facade) — substrate + serde + facade projections:**
- `game/strategy/data/planet.py` — substrate, `add_to_staging_yard`, `remove_from_staging_yard`, `staging_yard` property
- `game/strategy/data/planet_serde.py` — `staging_yard` serialize/deserialize
- `game/strategy/data/galaxy_protocols.py` — `IStagingYardHolder` protocol annotations
- `game/strategy/facade/slices/planet_slice.py:194-213` — `_planet_staging_yard_snapshot` (replace `item.get(...)` with typed attribute access)
- `game/strategy/facade/dto/planet_dto.py:99-112` — `staging_yard_summary` builder
- `tests/unit/strategy/data/test_planet_*` (4 files)
- `tests/unit/strategy/facade/test_container_snapshots.py`

**PROJ-445 (engine) — call-site adoption:**
- `game/strategy/engine/order_handlers/transfer_branches.py` — drop 3 helpers + 2 flatten blocks
- `game/strategy/engine/issuer_adapter.py` — drop `_matches` dict probe; tighten `pop_carried`/`append_carried` signatures
- `game/strategy/engine/production_spawner.py` — construct typed `DropPod`/`CarriedVehicle` directly instead of dicts
- `game/strategy/engine/order_handlers/transfer.py`, `order_processor.py`, `handlers/launch_*`, `handlers/lay_mines.py`, `order_handlers/lay_mines.py` — read-paths to verify
- `game/strategy/validation/transfer_validator.py:228, 363-379` — drop runtime shape probe
- `game/strategy/services/planet_write_service.py:100-105` — tighten `add_staging_item` / `pop_staging_item` signatures
- 10 `tests/unit/strategy/engine/test_*` files (staging_yard + production_spawner + transfer + issuer_adapter + pod_transfer + staging_yard_operations + production_normalisation + order_processor_transfer + order_handlers/test_transfer_handler + order_handlers/test_colonize_transfer)
- 1 `tests/unit/strategy/validation/test_transfer_drop_pod.py`

**PROJ-446 (UI + UI tests + static guards):**
- `game/ui/screens/strategy_detail_fmt.py:285-297` — UI reader (the big blocker)
- `tests/unit/ui/screens/test_strategy_detail_fmt.py:915-1009` — 5 tests pinning the dict shape (3 with dict-injection fixtures, 1 missing-attr, 1 non-dict-tolerance)
- `tests/unit/ui/screens/test_transfer_view_model_container.py`
- `tests/unit/ui/screens/test_transfer_dialog_characterization.py`
- `tests/unit/ui/panels/test_planet_report_panel.py`
- `tests/static_guards/test_no_legacy_storage_fields.py` — re-check; current text doesn't pin the TYPE, but the comment at line 9 mentions `staging_yard` as a dataclass field shape
- `tests/static_guards/test_no_legacy_protocol_names.py`

**Integration-test root (unowned in current partition):**
- `tests/integration/test_fms_planet_recovery.py:59`
- `tests/integration/test_fms_planet_lay_mines.py:82, 139, 155, 171`
- `tests/integration/test_fms_planet_launch.py:92, 121, 157, 192`
- `tests/integration/test_fms_a_e2e.py:305`

**Fixtures:**
- `tests/fixtures/saves/galaxy_proj372_populated.json` — would still serialize as dict; `planet_serde._normalize_to_typed` handles load conversion. No edit required IF serde does the round-trip correctly.
- `tests/fixtures/saves/_build_galaxy_fixture.py` — verify if any staging items are constructed here.

---

## 7. Open questions for the coordinator

1. **Approve Path A for this session?** I will proceed with engine-only API cleanup as soon as confirmed. Approximate diff: ~150 LOC across 4 files (planet.py, transfer_branches.py, issuer_adapter.py, production_spawner.py) plus 2 new test files.

2. **Confirm ownership of `tests/integration/test_fms_*`** — these 4 files block the four-way joint and have no listed owner. PROJ-446 covers UI; PROJ-447 covers sim/AI/docs; PROJ-444/PROJ-445 cover data/facade/engine. End-to-end FMS integration tests sit between the two engine-side projects and UI. Suggestion: assign to PROJ-446 alongside the other UI/test fixture migrations.

3. **Confirm partition of `game/strategy/validation/`** — Joint A's grant says "PROJ-444 data/facade + PROJ-445 engine", and validation is engine-adjacent. PROJ-445's own Phase 2 already touched validation tests. Suggested ruling: validation is in PROJ-445's bucket.

4. **Future joint phase naming/numbering** — should the four-way be filed as PROJ-444 Phase 3 (the project that originated the substrate finding), as a new PROJ-NNN, or as a coordinator-owned joint (this directory)?

---

## Appendix — STOP conditions per task spec

The Stage 3 Joint A task spec listed five explicit STOP conditions. Triggered ones:

- ✅ **"The `rg "staging_yard"` audit reveals more than ~20 call sites — that suggests substrate coupling deeper than the finding scoped."** — 49 files, 310 occurrences. Triggered with ~15× margin.

Not (yet) triggered:
- Stage 3-A-1's substrate widening breaks save-load round-trip (not attempted)
- New failing tests in Stage 3-A-1 or Stage 3-A-4 pass before change (not attempted)
- Sharded test suite reveals unrelated regression (no changes made yet)

No code changes were made before this report. Working tree is clean of Joint A edits. The pre-flight read pass and audit are the only consumed steps.

---

**Next action awaiting coordinator input.** Default if no response: proceed with Path A.
