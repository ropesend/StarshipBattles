# Phase 1: Facade Read-Path Policy + Static Guard + First Migration Slice (Pattern #5)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-472 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Close the verified facade read-path gap (FAC-001/FAC-002/FAC-003) incrementally: decide + document the read-path policy, add a read-path static guard mirroring the write-path guard, and migrate the densest bypass sites as the first slice. NOT a single-pass migration of all ~93 `game/ui/` import sites.

---

## Tasks

### Task 1.1: Decide and record the read-path policy [Complex]
**File:** `docs/02_PATTERNS.md` (Pattern #5 entry)
**Tests:** N/A (decision task; output is a documented contract)

- [ ] Choose between (a) add read DTOs to the facade for UI-accessed types, or (b) formally document which strategy data classes are UI-safe for read-only access and enforce via static guard + convention
- [ ] Record the chosen policy in Pattern #5 in `docs/02_PATTERNS.md`, naming the UI-safe read types (or the DTO coverage plan)
- [ ] Verify the policy explicitly covers the audit-listed types: `CarriedVehicle`, `DropPod`, `FighterWing`, `SatelliteConstellation`, `MineGroup`, `BuildQueueSource`, `BuildContext`, `FleetCapabilityCalculator`, `ActivationPhase`, `ComponentActivationState`, `ContainableKind`, `FacilityAbilitySource`, `RaceConfig`, `HabitabilityFactors`, `DesignMetadata`, `DesignRoleRegistry`, `GameConfig`

### Task 1.2: Add a read-path static guard [Complex]
**File:** `tests/static_guards/test_facade_read_path_guard.py` (new)
**Tests:** `pytest tests/static_guards/test_facade_read_path_guard.py`

- [ ] Write a failing AST/import-scan guard (mirroring `tests/static_guards/test_facade_bypass_guard.py`) that fails on `game/ui/` runtime imports of strategy data/engine types NOT on the Task 1.1 allowlist
- [ ] Run it; confirm it fails against current code (catches existing bypass sites)
- [ ] Implement the allowlist so the guard passes for sanctioned read types and fails for net-new ones
- [ ] Verify the guard is in the static-guard suite and re-introducing a non-allowlisted UI read import fails CI

### Task 1.3: Migrate the densest BuildQueue/fleet bypass sites (first slice) [Complex]
**File:** `game/ui/screens/build_queue_screen.py`
**Tests:** `pytest tests/ --testmon` plus the Task 1.2 guard

- [ ] Route `BuildQueueSource` / `collect_build_queues_at_hex` runtime import (`build_queue_screen.py:23`) through a facade read DTO or sanctioned accessor per Task 1.1 (FAC-002)
- [ ] In `build_queue_controller.py`: reconcile the `BuildContext`/`BuildQueueSource` TYPE_CHECKING imports (lines 18-20) and any runtime strategy reads with the policy (FAC-002)
- [ ] In `fleet_data_source.py`: route the `FleetCapabilityCalculator` late-import (line 242) through the facade or sanctioned read surface (FAC-002)
- [ ] Verify the migrated sites pass the Task 1.2 guard and `pytest tests/ --testmon`

### Task 1.4: Migrate the StrategyScreen.session read-path consumers [Complex]
**File:** `game/ui/screens/strategy_screen.py`
**Tests:** `pytest tests/ --testmon` plus the Task 1.2 guard

- [ ] Add facade accessor methods (registries / active_empire / turn / empires) so UI no longer reads `screen.session.<x>` directly (FAC-003; `strategy_screen.py:242-257`)
- [ ] Migrate `strategy_detail_formatter.py:112` (`.session.registries`) to the facade accessor
- [ ] Migrate `strategy_detail_formatter.py:395-396` (`.session.turn_engine`) to the facade accessor
- [ ] Migrate `strategy_windows/list_windows.py:69` (`.session.empires`) to the facade accessor
- [ ] Migrate `hex_outlines.py:30` (`.session.active_empire.id`) to the facade accessor
- [ ] Extend the Task 1.2 guard (or add a sibling) to fail on new `.session.<read>` access from `game/ui/`
- [ ] Verify the 4 consumers no longer touch `.session`; guard passes; `pytest tests/ --testmon`

### Task 1.5: Phase verification [Medium]
**File:** n/a
**Tests:** `pytest tests/static_guards/ && pytest tests/ --testmon`

- [ ] Verify pytest passes; the read-path static guard passes; no new bypass sites re-introduced (re-run `python Tools/pattern_audit/pattern_audit.py` and confirm the Pattern #5 facade-bypass count drops for the migrated slice)
- [ ] Record the remaining (~85) un-migrated sites as follow-on batches/phases

---

## Phase Completion Checklist
When all tasks above are done:
- [ ] All task checkboxes above are checked
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase

_Scope extracted from PROJ-470 (pattern-audit `Reviews/results/2026-05-20_075227_pattern-audit/`) under Protocol 06/07._
