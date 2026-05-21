# Phase 2: Codex-audit follow-ups

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-469 2`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Implement the VERIFIED findings from the one-round Codex audit (`AgentCoordination/Scratchpad/Consult/proj469_audit/`). Both are the same defect class PROJ-469 owns (Fleet-vs-DeployedGroup terminology drift; project-internal count consistency), in files already touched this project.

**Revision Reason:** Codex audit (one round, 2026-05-20) surfaced one remaining terminology-drift cluster in `docs/systems/satellites.md` recovery prose and one stale objective line in this project's own checklist. Codex finding (c)-2 (`03_CONVENTIONS.md:117` `Optional[int]`) was REJECTED — the doc faithfully mirrors the live source declaration (`game/strategy/engine/commands/__init__.py:47`), so "fixing" it would make the doc contradict code; logged as a code-style discovered-issue instead.

---

## Tasks

### Task 2.1: satellites.md recovery prose — DeployedGroup terminology + live-code accuracy [Simple]
**File:** `docs/systems/satellites.md`
**Verification:** Cross-check against `game/strategy/engine/order_handlers/recover_satellites.py:120-170`.

- [x] Fix the `RecoverSatellitesOrderHandler` description (lines ~198-207): the live handler method is issuer-polymorphic (`execute_for_issuer(*, issuer: IIssuerAdapter, ...)`, not `execute_action_order`), locates the constellation at `issuer.location` (not "the recovering fleet's hex"), and prunes the empty `SatelliteConstellation` from `empire.deployed_groups` (NOT `empire.fleets`) — same Fleet-vs-DeployedGroup drift as Task 1.3. Verified against recover_satellites.py:120-170.
- [x] Verify: recovery prose no longer says `empire.fleets` for satellite-group pruning or "recovering fleet's hex"

### Task 2.2: phase_1_checklist.md stale objective count [Simple]
**File:** `Projects/active_projects/PROJ-469/phase_1_checklist.md`

- [x] Update the Phase 1 objective line (line 9) from "the 4 verified MAJOR" to "the 3 surviving MAJOR (README count finding dropped — see decisions.md)" so it matches plan.md and the dropped Task 1.2

### Task 2.3: Phase-wide verification [Simple]
- [x] Verify: `Last verified:` stamp on satellites.md reflects Phase 2 edits; re-run docs audit shows no new dead refs in touched files (72 dead refs unchanged; new code ref recover_satellites.py resolves)

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State

_Codex audit source: `AgentCoordination/Scratchpad/Consult/proj469_audit/audit.md.invalid-output-*.txt` (harvester rejected frontmatter; content intact)._
