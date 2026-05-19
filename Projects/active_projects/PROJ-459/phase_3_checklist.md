# Phase 3: F-A-007 measurement decision — `ship_instance.py` close-or-spinout

**Status:** Not Started
**Depends on:** Phase 2 complete (or deferred); Phase 0 re-measurement done; **PROJ-449 merged into main** (HARD gate for this phase — PROJ-449's wrapper + @property retirement is the primary driver of the ship_instance.py LOC delta the verdict depends on). Phases 1 and 2 may have proceeded before PROJ-449 lands; Phase 3 cannot. **PROJ-454 (Group B) ALSO must have landed** before the final LOC verdict: codex r5 group1-preexecution-review COL-2 verified PROJ-454 Phase 2's component_inspector import removal (function-local imports at `ship_instance.py:635/654/663`) changes the post-PROJ-449 LOC by a non-trivial delta. Without PROJ-454 landed, the close-or-spinout threshold check is unsound.
**Review Mode:** lightweight (no code changes; verdict + optional spinout)
**Files:**
- `game/strategy/data/ship_instance.py` (production; read-only)
- `Projects/active_projects/PROJ-459/decisions.md` (docs; verdict recorded)
- `Projects/active_projects/PROJ-459/findings/PROJ-459_findings.md` (findings; F-A-007 final disposition)
- `Projects/active_projects/PROJ-461/` (project; created if spinout)

**Objective:** Decide F-A-007's disposition based on the post-PROJ-449 LOC of `ship_instance.py`. Either close it here (ceiling met) or spin it out as a fresh project (ceiling violated). **Do NOT attempt the split in this project.**

**Codex r4 directive:** "F-A-007 should not be smuggled in as a side quest; if it still sits at 839 LOC after job 1 [PROJ-449], spin it as its own next-touch project."

---

## Tasks

### Task 3.0: Verify upstream PROJ-454 landed (codex r5 COL-2) [Simple, BLOCKING]
**Files (read-only):** `Projects/active_projects/PROJ-454/plan.md`

- [ ] Open PROJ-454 plan.md. Confirm Quick Status table shows ALL phases marked `Complete` AND Current State reads "Project complete".
- [ ] If PROJ-454 is still in progress, PAUSE Phase 3. Record blocker in `findings/phase_0_audit.md` (or create `findings/phase_3_blocker.md`). Resume Phase 3 only after PROJ-454 closes.
- [ ] Rationale: PROJ-454 Phase 2 retires `component_inspector.py` imports, including function-local imports at `ship_instance.py:635/654/663` (codex r5 verified). The LOC delta from those removals (plus any incidental cleanup in PROJ-454) materially affects the close-or-spinout threshold.

### Task 3.1: Re-measure `ship_instance.py` LOC (post-PROJ-449 AND post-PROJ-454) [Simple]

**File:** `game/strategy/data/ship_instance.py`

- [ ] Run (PowerShell): `(Get-Content game/strategy/data/ship_instance.py | Measure-Object -Line).Lines`
- [ ] **Critical**: this measurement must be taken AFTER both PROJ-449 AND PROJ-454 have landed. The PROJ-454 component_inspector import removal at `ship_instance.py:635/654/663` changes the count by a small but non-zero amount.
- [ ] Compare against the Phase 0 re-measurement value. The delta from Phase 0 should equal (PROJ-449 wrapper+property drop, ~50 LOC) + (PROJ-454 function-local import removal, ~3-5 LOC).
- [ ] Record the current LOC AND the delta in `decisions.md` (split out: pre-Phase-0, post-PROJ-449, post-PROJ-454, current).

### Task 3.2: Inspect what survived PROJ-449 [Simple]

**File:** `game/strategy/data/ship_instance.py` (read-only)

- [ ] Confirm: the `_ship_instance_init_with_legacy_kwargs` module-level wrapper is gone (PROJ-449 should have deleted it).
- [ ] Confirm: the `consumable_levels` and `cargo_contents` @property/@setter pairs are gone.
- [ ] Inspect: what's the surviving shim footprint? The 5 TD-06 high-value shims (`create`, `to_dict`, `clone`, `to_ship`, `update_from_ship`) per the original F-A-007 finding were ~360 LOC. Has PROJ-449 reduced any of these?
- [ ] If anything unexpected survived (or unexpectedly disappeared), document it.

### Task 3.3: Verdict — close or spinout [Simple]

**Decision rule:**
- **LOC < 500:** close F-A-007. Update `decisions.md` with: "Date / Decision: F-A-007 closed. / Rationale: ship_instance.py at <LOC> after PROJ-449 wrapper retirement; 500 LOC ceiling met." Update `findings/PROJ-459_findings.md`.
- **LOC ≥ 500:** spinout. Proceed to Task 3.4.

### Task 3.4: Spinout (if LOC ≥ 500) [Simple]

**Files:**
- `Projects/active_projects/PROJ-461/` (new; create via the helper script)
- `Projects/active_projects/PROJ-459/decisions.md` (docs)
- `Projects/active_projects/PROJ-459/findings/PROJ-459_findings.md` (findings)

- [ ] Run the project creation script: `python Projects/scripts/create_project.py "ShipInstance LOC reduction"`. This creates PROJ-461 (or whichever ID is next available) with the standard skeleton.
- [ ] Populate the new project's `plan.md` with:
  - Overview: closes F-A-007 (carried from PROJ-459).
  - Goal: reduce ship_instance.py LOC below 500.
  - Scope: enumerate the surviving TD-06 shims, propose a caller migration sequence.
  - Dependencies: PROJ-449 (which has shipped), PROJ-459 (this project, which carries the measurement decision).
- [ ] Copy F-A-007 verbatim from `PROJ-459/findings/PROJ-459_findings.md` to `PROJ-461/findings/PROJ-461_findings.md` with status updated to "Open; project spun out from PROJ-459 Phase 3 on YYYY-MM-DD."
- [ ] In PROJ-459: update `decisions.md` with "F-A-007 spun out as PROJ-461 (or actual ID); see <new project path>."
- [ ] In PROJ-459: update `findings/PROJ-459_findings.md` F-A-007 status to "spun out as PROJ-XXX on YYYY-MM-DD; PROJ-459 carries the measurement-decision only."

### Task 3.5: Commit [Simple]

**If close branch:**
- [ ] Commit message: `PROJ-459 Phase 3: ship_instance.py at <LOC> after PROJ-449 — F-A-007 closed (ceiling met)`
- [ ] Update `plan.md` Current State to "All phases complete; ready for verification."

**If spinout branch:**
- [ ] Commit message: `PROJ-459 Phase 3: ship_instance.py at <LOC> — F-A-007 spun out as PROJ-XXX (ceiling still violated)`
- [ ] Update `plan.md` Current State to "All phases complete; F-A-007 spun out as PROJ-XXX."

---

## Phase Completion Checklist
- [ ] ship_instance.py LOC re-measured and recorded
- [ ] PROJ-449 shim retirement confirmed (or unexpected residue documented)
- [ ] Verdict made: close (LOC < 500) or spinout (LOC ≥ 500)
- [ ] If close: `decisions.md` records the closure; `findings/PROJ-459_findings.md` updated
- [ ] If spinout: new project scaffolded; F-A-007 transferred to new project's findings; PROJ-459 carries only the measurement-decision narrative
- [ ] `plan.md` Current State updated
- [ ] Sharded suite green (should be from Phase 1/2; no code touched in Phase 3)
