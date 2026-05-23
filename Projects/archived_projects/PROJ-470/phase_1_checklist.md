# Phase 1: Critical - Facade Read-Path DTO Gap (Pattern #5)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-470 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Extracted -> PROJ-472 (Deferred)

> **SCOPE REVISION 2026-05-20 (Protocol 06/07):** This entire phase (FAC-001/FAC-002/FAC-003)
> was deferred to **PROJ-472 "Facade read-path migration"**. The dual independent+Codex review
> determined the facade read-path gap is a deliberately-deferred architecture migration
> (PROJ-382 / U1–U3) spanning ~93 `game/ui/` files, not a contained conformance fix. The full
> policy + static-guard + first-slice scope now lives in `Projects/active_projects/PROJ-472/`.
> See PROJ-470 decisions.md and PROJ-472 plan/design/decisions. The tasks below are preserved
> as historical context only; do NOT implement them under PROJ-470.
**Objective:** Close the verified CRITICAL Pattern #5 facade read-path gap identified by audit `2026-05-20_075227_pattern-audit`. The `StrategySessionFacade` is a write-path-only half-facade: commands route through `facade.handle_command()` (guarded), but 135+ `game/ui/` import sites read strategy data objects directly. Scope this phase as **policy decision + read-path static guard + first migration slice of the densest sites** — NOT a single-pass migration of all 135 sites (full migration is tracked as follow-on work, see Notes).

---

## Tasks

### Task 1.1: Decide and record the read-path policy [Complex]
**File:** `docs/02_PATTERNS.md` (Pattern #5 entry)
**Pattern:** #5 (Facade / Delegate)
**Tests:** N/A (decision task; output is a documented contract)

- [x] (Deferred -> PROJ-472) Choose between option (a) add read DTOs to the facade grouped namespaces for UI-accessed types, or option (b) formally document which strategy data classes are UI-safe for read-only access and enforce via static guard + convention (per audit `report.md` §4 CRITICAL-1 remediation)
- [x] (Deferred -> PROJ-472) Record the chosen policy in Pattern #5 in `docs/02_PATTERNS.md`, naming the UI-safe read types (or the DTO coverage plan)
- [x] (Deferred -> PROJ-472) Verify: the policy explicitly covers the audit-listed types: `CarriedVehicle`, `DropPod`, `FighterWing`, `SatelliteConstellation`, `MineGroup`, `BuildQueueSource`, `BuildContext`, `FleetCapabilityCalculator`, `ActivationPhase`, `ComponentActivationState`, `ContainableKind`, `FacilityAbilitySource`, `RaceConfig`, `HabitabilityFactors`, `DesignMetadata`, `DesignRoleRegistry`, `GameConfig`

### Task 1.2: Add a read-path static guard [Complex]
**File:** `tests/static_guards/test_facade_read_path_guard.py` (new)
**Pattern:** #5 (Facade / Delegate)
**Tests:** `pytest tests/static_guards/test_facade_read_path_guard.py`

- [x] (Deferred -> PROJ-472) Write a failing AST/import-scan guard test (mirroring `tests/static_guards/test_facade_bypass_guard.py`'s write-path guard) that fails on `game/ui/` runtime imports of strategy data/engine types NOT on the Task 1.1 UI-safe allowlist
- [x] (Deferred -> PROJ-472) Run it; confirm it fails against current code (catches the existing bypass sites)
- [x] (Deferred -> PROJ-472) Implement the allowlist so the guard passes for sanctioned read types and fails for net-new ones
- [x] (Deferred -> PROJ-472) Verify: guard is in the static-guard suite and re-introducing a non-allowlisted UI read import fails CI

### Task 1.3: Migrate the densest BuildQueue/fleet bypass sites (first slice) [Complex]
**File:** `game/ui/screens/build_queue_screen.py`
**Pattern:** #5 (Facade / Delegate)
**Tests:** Run `pytest tests/ --testmon` plus the Task 1.2 guard

- [x] (Deferred -> PROJ-472) Route `BuildQueueSource` / `collect_build_queues_at_hex` runtime import (line 23) through a facade read DTO or sanctioned accessor per the Task 1.1 policy (FAC-002)
- [x] (Deferred -> PROJ-472) In `game/ui/panels/build_queue_controller.py`: reconcile the `BuildContext`/`BuildQueueSource` TYPE_CHECKING imports (lines 18-20) and any runtime strategy reads with the policy (FAC-002; note these are currently type-only under `TYPE_CHECKING`)
- [x] (Deferred -> PROJ-472) In `game/ui/screens/fleet_data_source.py`: route the `FleetCapabilityCalculator` late-import (line 242) through the facade or the sanctioned read surface (FAC-002)
- [x] (Deferred -> PROJ-472) Verify: the migrated sites pass the Task 1.2 guard and `pytest tests/ --testmon`

### Task 1.4: Phase verification [Medium]
**File:** n/a
**Pattern:** #5 (Facade / Delegate)
**Tests:** `pytest tests/static_guards/ && pytest tests/ --testmon`

- [x] (Deferred -> PROJ-472) Verify: pytest passes; the new read-path static guard passes; no new bypass sites re-introduced (re-run `python Tools/pattern_audit/pattern_audit.py` and confirm the Pattern #5 facade-bypass count drops for the migrated slice)

**Notes:** FAC-001 (the full 135-site migration) is intentionally NOT completed in this phase — Phase 1 establishes the policy + guard + first slice. The remaining sites are migrated incrementally under the guard; if the full sweep is large enough to warrant its own project, decompose it then. (Per Codex consult 2026-05-21 and decisions.md.)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] (N/A — phase extracted to PROJ-472) All task checkboxes above are checked
- [x] (N/A — phase extracted to PROJ-472) Update status at top of this file to `Complete`
- [x] (N/A — phase extracted to PROJ-472) Update plan.md phase table row to `Complete`
- [x] (N/A — phase extracted to PROJ-472) Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-20_075227_pattern-audit/`. See `findings/source_audit.md` for the link._
