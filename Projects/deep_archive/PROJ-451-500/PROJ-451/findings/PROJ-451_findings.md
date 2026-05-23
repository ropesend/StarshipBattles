# PROJ-451 Consolidated Findings

> Findings closed (or partially closed) by this project. Each entry copied from the discovered-issues log + archived bucket reports + a current-state verification line dated **2026-05-19**.
>
> Sources:
> - `AgentCoordination/discovered_issues/log.jsonl` (DI-2026-05-18-006, DI-2026-05-18-007)
> - `Projects/archived_projects/PROJ-445/findings/bucket_b_engine_services_scan.md` (F-B-019)

---

## DI-2026-05-18-006 — Fleet production affordability-vs-consumption rounding mismatch
- **Severity**: medium
- **Category**: bug
- **File**: `game/strategy/data/fleet.py:245-269` (data-layer half) + `game/strategy/engine/production_engine.py:649-687` (engine UX gap half)
- **Symbol**: `Fleet.has_cargo_resources` + `Fleet.consume_cargo_resource` (data); `ProductionEngine._apply_resource_consumption` (engine)
- **Source refactor**: PROJ-436 Phase 12 (Option C truth-up) — intentional residue at that time
- **What survived (May 2026)**: Fleet production had an affordability-vs-consumption rounding mismatch. `Fleet.has_cargo_resources` compared against unrounded float; `Fleet.consume_cargo_resource` did `int(round(amount))` before unloading from integer cargo. Result for fractional per-step costs that round to 0 (requested 0.1 against cargo=1): affordability passed, the engine consumed 0, `ProductionEngine._apply_resource_consumption` recorded 0 progress, `_process_queue_tick_dynamic` decremented `tick_capacity`, the queue stalled correctly — but no `RESOURCE_SHORTAGE` event because affordability had passed.
- **Why it's a problem**: Player sees a stuck fleet build with no shortage indicator. Latent in current `data/components.json` (ratios produce integer per-step costs); becomes visible as soon as a new ship class lands fractional ratios on fleet builds.
- **Suggested action (per log entry)**: (a) Engine-side: detect `amount > 0 was requested but actually_consumed == 0` (diff is zero) and route to `_log_resource_shortage` with rounding-vs-cargo cause. (b) Data-side: change `Fleet.has_cargo_resources` to compare against `int(round(amount))` so affordability matches consumption semantics.
- **Effort**: small (Option B) / small (Option A)
- **Status as of 2026-05-19**: **partially-resolved**. PROJ-444 Phase 2 (2026-05-18) applied Option B at the data-layer: `Fleet.has_cargo_resources` now compares against `int(round(amount))`, symmetric with `consume_cargo_resource`'s rounding (verified at `fleet.py:245-269`). The engine UX gap is OPEN — no RESOURCE_SHORTAGE emitted when `amount` rounds to 0 → 0. **Closed engine-side by PROJ-451 Phase 2.**
- **Codex r4 verification (2026-05-19)**: data half confirmed resolved at `fleet.py:245-269`; remaining engine UX hole explicitly documented in the docstring (lines 255-257 of `fleet.py`).

---

## DI-2026-05-18-007 — `ProductionEngine._apply_resource_consumption` ignores bool return
- **Severity**: low
- **Category**: bug
- **File**: `game/strategy/engine/production_engine.py:677-682` (current line range; was 637 in original log entry)
- **Symbol**: `ProductionEngine._apply_resource_consumption`
- **Source refactor**: PROJ-436 Phase 12 (Option C truth-up)
- **What survived**: The method ignores the bool return of `production_consume_resource` and only records the `production_get_resource` before/after diff. If a future `IProductionResourceSource` implementation returns False from `production_consume_resource` AFTER affordability passed (sub-tick race, partial-charge contract, contract breach), the diff records 0 progress but `_process_queue_tick_dynamic` still subtracts `ticks_to_spend` from `tick_capacity`. Result: tick capacity burns without forward progress. No present production caller exercises this (Planet and Fleet both currently succeed when affordability passes), but the Protocol contract permits the failure mode.
- **Why it's a problem**: The Phase 12 Protocol docstring update implies but does not enforce "consume MUST succeed when affordability passed."
- **Suggested action**: Two options:
  - (a) Capture the consume return value in `_apply_resource_consumption` and signal back to `_process_queue_tick_dynamic` so it can skip the `tick_capacity` decrement when consume returned False (preserves capacity for retry or shortage).
  - (b) Tighten the Protocol contract to hard-assert "production_consume_resource MUST succeed when affordability passed" so failure is a programmer error rather than a contract-permitted outcome.
- **Effort**: tiny (option b — docstring + assert) / small (option a — defensive plumbing)
- **Status as of 2026-05-19**: **partially-resolved**. The Protocol contract docstring at `production_engine.py:60-95` already declares the affordability/consumption symmetry MUST-language (post-PROJ-444 Phase 2). The engine-side defensive branch never landed — `_apply_resource_consumption` at lines 677-682 still ignores the bool return. Codex r4 verified this at 2026-05-19. **Closed by PROJ-451 Phase 3 (option (a) or (b) per the project's Phase 3 decision).**

---

## F-B-019 — `IProductionResourceSource.production_consume_resource` Protocol-side complement (engine-facing contract)
- **Severity**: medium
- **Category**: missing-functionality
- **File**: `game/strategy/engine/production_engine.py:60-95` (Protocol contract docstring)
- **Symbol**: `IProductionResourceSource.production_consume_resource`
- **Source refactor**: PROJ-436 Phase 8 (unified Protocol seam) + PROJ-436 Phase 12 (Option C truth-up)
- **What survived (May 2026)**: The Protocol contract docstring described the actual-vs-requested-amount semantics but did NOT declare that `production_has_resources(...)` returning True implies `production_consume_resource(...)` returns True. DI-2026-05-18-007 already flagged this on the engine side; F-B-019 is its Protocol-side complement.
- **Why it's a problem**: Two engine-side problems flow from the unenforced Protocol contract:
  - (a) future implementers can return False from `production_consume_resource` after `production_has_resources` returned True, burning tick_capacity without progress (the DI-007 path).
  - (b) the affordability/consumption rounding mismatch in `Fleet.has_cargo_resources` (DI-006) was a real-today instance of this exact contract gap.
- **Suggested action**: Declare in `IProductionResourceSource.production_consume_resource` Protocol docstring that "MUST return True when `production_has_resources(costs)` returned True for the same `(resource_type, costs[resource_type])`. Implementers that perform rounding (integer-typed sources) MUST do so symmetrically in both methods."
- **Effort**: tiny (Protocol docstring + a single ratchet test); the actual implementer fix is sized in DI-006
- **Status as of 2026-05-19**: open. The protocol docstring at `production_engine.py:60-95` ALREADY contains MUST-language (post-PROJ-444 Phase 2 update — verified by direct read). The remaining residue is the engine-side enforcement and the per-implementer ratchet test. **Closed by PROJ-451 Phases 3 + 4.**

---

## Codex r4 redesign — PROJ-451 row

> 3. `Production resource-consumption semantics` - Finish the engine-side half of the fleet-production contract: resolve the rounded-to-zero shortage UX gap, decide whether `_apply_resource_consumption` honors the bool return or fails hard on contract breach, and add the stocked-fleet ratchets. Closes the live remainder of `DI-006`, `DI-007`, and completes `F-B-019`. Parallel-safe. Depends on: none. Size: medium.

The project is parallel-safe with PROJ-449 and PROJ-450 because the engine-side residue is entirely contained in `production_engine.py` + tests, with no shared file surface with either of the other Stage-3 projects.
