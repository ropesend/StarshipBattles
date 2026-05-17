# Phase 11: Codex consult + verified-finding remediation

**Status:** Not Started
**Depends on:** phase_10
**Review Mode:** standard
**Files (planned):** TBD — depends on consult findings

**Objective:** Per the standing end-of-project consult workflow (`~/.claude/projects/c--Dev-Starship-Battles/memory/feedback_consult_at_project_end.md`): run a Codex consult on the landed PROJ-436 work. For each finding, verify against current code (do not trust the consult's word; consult agents have hallucinated file:line references in this repo before). Verified findings become added phases (12+, 13+, …) on this project. Unverified or out-of-scope findings logged in `decisions.md`.

---

## Tasks

To be authored after Phase 10 close. Expected:

### Task 11.1: Run Codex consult [Simple]
- [ ] Invoke `claude-consult` skill with Codex, scoped to PROJ-436's landed code + tests + plan / decisions / design files
- [ ] Wait for response file
- [ ] Read response in full

### Task 11.2: Per-finding verification [Medium]
- [ ] For each finding raised by consult:
  - [ ] Grep / read cited files; confirm the finding describes a real issue at the cited location
  - [ ] Decide: verified (real, in scope) / unverified (cited code doesn't match claim) / out-of-scope (real but not this project)
  - [ ] Log verdict in `decisions.md`

### Task 11.3: Author phases for verified findings [Medium]
- [ ] Per verified finding, create `phase_<N>_checklist.md` with objective + tasks + completion checklist
- [ ] Update `phase_state.json` with new phase entries
- [ ] Update `plan.md` Quick Status table with new phase rows
- [ ] Update plan.md Current State to point to the next remediation phase

### Task 11.4: Execute remediation phases [Variable]
- [ ] For each new remediation phase, follow standard RED→GREEN sub-phase workflow
- [ ] Each remediation phase ends with: focused tests green; full sharded suite green; status updated

---

## Phase Completion Checklist
- [ ] Codex consult run; response read; verdicts logged in `decisions.md`
- [ ] All verified-finding remediation phases complete
- [ ] Full sharded suite green
- [ ] Project ready for final audit + user verification
- [ ] Update status to Complete; update plan.md + phase_state.json
- [ ] Notify user that PROJ-436 is ready for `verified` label / archive
