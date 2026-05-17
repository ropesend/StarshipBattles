# Phase 5: Codex consult + verified-finding remediation

**Status:** Not Started
**Depends on:** phase_4
**Review Mode:** standard
**Files (planned):** TBD — depends on consult findings

**Objective:** Per the standing end-of-project consult workflow: run a Codex consult on landed PROJ-437 UI work. Verify each finding against current code. Verified findings become added phases (6+, 7+, …). Unverified or out-of-scope findings logged in `decisions.md`.

---

## Tasks

To be authored after Phase 4 close. Expected workflow mirrors PROJ-436 Phase 11:

### Task 5.1: Run Codex consult [Simple]
- [ ] Invoke `claude-consult` skill with Codex, scoped to PROJ-437's landed code + tests + plan / decisions / design
- [ ] Wait for response file
- [ ] Read response in full

### Task 5.2: Per-finding verification [Medium]
- [ ] For each finding: grep / read cited files; confirm the finding describes a real issue at the cited location
- [ ] Decide: verified / unverified / out-of-scope
- [ ] Log verdict in `decisions.md`

### Task 5.3: Author phases for verified findings [Medium]
- [ ] Per verified finding, create `phase_<N>_checklist.md` with objective + tasks
- [ ] Update `phase_state.json` with new phase entries
- [ ] Update `plan.md` Quick Status table with new phase rows
- [ ] Update plan.md Current State to point to the next remediation phase

### Task 5.4: Execute remediation phases [Variable]
- [ ] For each new remediation phase, follow standard RED→GREEN sub-phase workflow
- [ ] Each remediation phase ends with: focused tests green; full sharded suite green

---

## Phase Completion Checklist
- [ ] Codex consult run; response read; verdicts logged in `decisions.md`
- [ ] All verified-finding remediation phases complete
- [ ] Full sharded suite green
- [ ] Project ready for final audit + user verification
- [ ] Update status to Complete; update plan.md + phase_state.json
- [ ] Notify user that PROJ-437 is ready for `verified` label / archive
