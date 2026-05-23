# Phase 0: Re-verify Stage 3 preflight audit; verify PROJ-449 Phase 3 precondition

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-450 0`
> 2. Audit results pinned in `findings/phase_0_audit.md`
> 3. PROJ-449 Phase 3 confirmed landed
> 4. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Re-verify that the 310-occurrence / 49-file audit + 3 blockers still hold at current HEAD. (The original audit comes from the Stage 3 Joint A preflight; the must-know rationale is inlined into `design.md` — the archive file is OPTIONAL background reading.) Confirm PROJ-449 Phase 3 has landed (Planet wrapper + property cluster deleted). **No code changes.**

**File ownership rule:** This project owns the full staging-yard substrate change end-to-end. Phase 0 is read-only — no `game/` or `tests/` edits.

**Source-of-truth findings:** [findings/PROJ-450_findings.md](findings/PROJ-450_findings.md) (F-B-013, DI-2026-05-18-001 substrate half, F-A-013 already-complete verification).

---

## Tasks

### Task 0.1: Confirm PROJ-449 Phase 3 precondition [Simple]
**File:** read `Projects/active_projects/PROJ-449/plan.md` Quick Status row + Current State

- [x] Open `Projects/active_projects/PROJ-449/plan.md`
- [x] Confirm Phase 3 row shows `Complete` in the Quick Status table
- [x] Verify that `_planet_init_with_legacy_kwargs` is GONE from `game/strategy/data/planet.py` (use `Grep` to confirm absence)
- [x] Verify that `Planet.staging_yard` @property/@setter pair is GONE (use `Grep` for `@staging_yard.setter` — should return zero matches)
- [x] If any of the above fail, **PAUSE**: PROJ-450 Phase 1 cannot start. Update plan.md Current State with "Blocked on PROJ-449 Phase 3" and surface to user.

### Task 0.2: Re-run the §1.2 audit at HEAD [Simple]
**Tools:** `Grep` / `Bash` with `rg`

- [x] Run (PowerShell-friendly):
  ```powershell
  # Number of files in game/ that reference staging_yard
  (rg -l "staging_yard" game/ | Measure-Object -Line).Lines   # expect 18 files
  # Number of files in tests/ that reference staging_yard
  (rg -l "staging_yard" tests/ | Measure-Object -Line).Lines  # expect 31 files
  # Total occurrences across game/ and tests/
  (rg "staging_yard" game/ tests/ | Measure-Object -Line).Lines  # expect 310 occurrences
  ```
- [x] Compare against Stage 3 preflight §1.2 numbers (310 across 49 files, broken down 82 game + 228 tests)
- [x] Pre-audit at 2026-05-19 confirmed matching counts; verify still matches at the time of execution
- [x] If count is dramatically different (>10% delta in either direction), capture the delta in `findings/phase_0_audit.md` and verify before proceeding

### Task 0.3: Re-verify the 3 blockers at HEAD [Simple]
**Files:** `game/ui/screens/strategy_detail_fmt.py`, `game/strategy/validation/transfer_validator.py`, `game/strategy/services/planet_write_service.py`, 4 integration test files

- [x] **BLOCKER #1** — UI reader:
  ```python
  # game/ui/screens/strategy_detail_fmt.py:285-297
  for item in staging_yard:
      if not isinstance(item, dict):
          continue  # ← typed objects fall here
  ```
  Verify this code is still present at lines 285-297. If the code shape has shifted, update the Phase 3 checklist line references.

- [x] **BLOCKER #2** — Integration test mutations. Run:
  ```bash
  rg "planet\.staging_yard\.(append|extend|clear)" tests/integration/
  ```
  Confirm:
  - `test_fms_planet_recovery.py:59` — 1 site
  - `test_fms_planet_lay_mines.py:82, 139, 155, 171` — 4 sites
  - `test_fms_planet_launch.py:92, 121, 157, 192` — 4 sites
  - `test_fms_a_e2e.py:305` — 1 site (`.clear()`)

- [x] **BLOCKER #3** — Validator + write service probes:
  - `game/strategy/validation/transfer_validator.py:228` — `staging = getattr(planet, 'staging_yard', [])` shape check
  - `game/strategy/validation/transfer_validator.py:363-379` — `if isinstance(item, CarriedVehicle): ... elif isinstance(item, dict) and ...` branch
  - `game/strategy/services/planet_write_service.py:100-105` — `add_staging_item` / `pop_staging_item` accept `Any`

### Task 0.4: Re-verify F-A-013 already-complete status [Simple]
**File:** `game/strategy/facade/slices/fleet_slice.py` (read)

- [x] At lines 165-191, verify the `_ship_container_snapshot` projects bay capacity from the real `_cargo_mgr.get_vehicle_bay_capacity()` (per PROJ-444 Phase 2 Task 2.4 completion)
- [x] Document in `findings/phase_0_audit.md`: "F-A-013 confirmed complete; no PROJ-450 action required"

### Task 0.5: Write `findings/phase_0_audit.md` [Simple]
**File:** `Projects/active_projects/PROJ-450/findings/phase_0_audit.md` (new)
**Tests:** none (pure documentation)

- [x] Sections:
  - "PROJ-449 Phase 3 precondition" — landed / blocked? Use direct code inspection per `Projects/active_projects/PROJ-449/decisions.md` 2026-05-19 row (the SHA-signal mechanism was removed in Bucket A fix; the canonical gate is `rg "_planet_init_with_legacy_kwargs\|@staging_yard\.setter" game/strategy/data/` returning zero hits).
  - "Audit re-verification" — counts (game/ + tests/ + total), file count, blocker confirmation
  - "Blocker confirmation" — each of the 3 blockers verified at HEAD with file:line
  - "F-A-013 already-complete" — confirmed; no action required
  - "Gate decision" — proceed to Phase 1 or pause?

**Gate criteria:**
- PROJ-449 Phase 3 must be complete → Phase 1 proceeds (verify via direct code inspection per `Projects/active_projects/PROJ-449/decisions.md` 2026-05-19 row)
- Audit deltas <10% from preflight numbers → Phase 1 proceeds
- 3 blockers all present → Phase 1 / 3 / 4 plans hold
- **Cross-group sync gate (Task 0.6) must clear** → Phase 1 proceeds
- Otherwise → PAUSE and surface

### Task 0.6: Cross-group sync gate — wait for PROJ-454 + PROJ-456 (Group B) [Simple, BLOCKING]
**Files (read-only):** `Projects/active_projects/PROJ-454/plan.md`, `Projects/active_projects/PROJ-456/plan.md`

PROJ-450 was reordered to LAST in Group A's serial sequence (2026-05-19 collision resolution) because Phase 3 and Phase 4 touch two test files that PROJ-454 + PROJ-456 (Group B) substantively edit:
- `tests/unit/strategy/engine/test_order_processor_transfer.py` — PROJ-454 Phase 3 (`process_transfer` facade call-site rewrites) vs PROJ-450 Phase 4 substrate assertions
- `tests/unit/ui/screens/test_transfer_dialog_characterization.py` — PROJ-456 Phase 4 (characterization sweep) vs PROJ-450 Phase 3 UI reader migration

Running PROJ-450 after both Group B projects land lets us rebase once cleanly on the merged Group B work rather than fighting two concurrent edits.

- [x] Open `Projects/active_projects/PROJ-454/plan.md`. Confirm the Quick Status table shows ALL phases marked `Complete` AND the Current State block reads "Project complete" (or equivalent). If still in progress, record the current phase in `findings/phase_0_audit.md` and PAUSE.
- [x] Open `Projects/active_projects/PROJ-456/plan.md`. Same check.
- [x] **If either is in progress:** STOP. Update PROJ-450 plan.md Current State with: "Blocked on sync gate — waiting on PROJ-454=<phase>, PROJ-456=<phase>". DO NOT proceed to Phase 1. Resume only when both gates clear.
- [x] **If both are complete:** record SHAs (or final-state references) in `findings/phase_0_audit.md` and proceed to Phase 1.
- [x] **Optional fill work while blocked:** read codex audit artifacts for context, do read-only verification of upstream code state, refine PROJ-450/decisions.md housekeeping. Do not start any Phase 1+ task.

**Rationale**: this gate is the cross-group resolution from the 2026-05-19 collision report. Without it, PROJ-450 risks editing the two shared test files in parallel with active Group B work, causing 3-way merge conflicts.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] `findings/phase_0_audit.md` exists with all 5 sections populated
- [x] PROJ-449 Phase 3 confirmed landed via direct code inspection (no SHA signal mechanism — that was removed in Bucket A fix)
- [x] **Task 0.6 cross-group sync gate cleared** (PROJ-454 + PROJ-456 both Complete)
- [x] Plan.md Quick Status row for Phase 0 → Complete
- [x] Plan.md Current State updated with audit summary numbers + sync-gate status
- [x] No production code or test code changed in this phase

## Notes / Risks / Coordination Touchpoints
- **PROJ-449 Phase 3 is the hard precondition.** Without it, the Planet `@property` for `staging_yard` still exists; Phase 1's new typed pop method conflicts with the legacy property.
- **No worktrees** per standing preference — serial execution in main checkout.
- **The must-know Path A rationale is inlined into `design.md`** (sections "Why partial Path A is justified" + "BLOCKER #1 — the rationale for permanent typed-readonly"). The archived Stage 3 preflight at `Projects/archived_projects/PROJ-444to447_coordinator/stage_3_joint_a_preflight_findings.md` is OPTIONAL background reading; nothing in it is required to execute the phases.
