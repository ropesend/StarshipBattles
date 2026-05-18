# Phase 6: Codex consult + verified-finding remediation

**Status:** Not Started
**Depends on:** phase_5
**Review Mode:** standard
**Files (planned):** TBD per consult findings

**Objective:** Per the standing end-of-project Codex-consult workflow (`feedback_consult_at_project_end.md`): run a Codex consult on the landed PROJ-443 work. Verify every finding against current code; remediate verified findings as sub-phases; document unverified or out-of-scope items in `decisions.md`.

---

## Tasks (authored at phase start)

### Task 6.1: Run Codex consult [Simple]

- [ ] Invoke `claude-consult` skill with Codex, mode `pre-final-check`, `--allow-tests`. Frame:
  > "Review PROJ-443's pytest.ini config flip and hidden-test triage. Verify: (a) the new `--ignore=./data` correctly excludes only the top-level `data/`; (b) no other `norecursedirs` tokens (`.* build dist CVS _darcs {arch} *.egg venv env .venv ShipThemes Assets combat_lab`) are silently hiding tests elsewhere; (c) Phase 5 bundled cleanups (5a-5d) landed cleanly; (d) the regression guard `test_no_hidden_test_directories.py` is structurally sufficient — does it catch every flavor of hidden-test config drift, or only the one we just fixed?; (e) the post-flip sharded count makes sense — is the count delta consistent with the on-disk file count?"
- [ ] Read response file in full.

### Task 6.2: Verify findings against code [Medium]

- [ ] For each finding, grep / read cited files. Consult agents have hallucinated file:line refs in this repo before; never trust without verifying.
- [ ] Classify: verified (in scope) / unverified / out-of-scope.

### Task 6.3: Author remediation sub-phases [Medium]

- [ ] Per verified finding, author a sub-phase checklist (6a, 6b, ...). Each RED→GREEN tested and committed separately.
- [ ] Unverified / out-of-scope findings: log in `decisions.md` with rationale.

### Task 6.4: Execute remediation [Variable]

- [ ] Per sub-phase, follow standard RED→GREEN workflow. Sharded gate at each commit.

---

## Phase Completion Checklist
- [ ] Codex consult run; response read; verdicts logged
- [ ] All verified-finding remediation sub-phases complete
- [ ] Sharded suite green
- [ ] Project ready for final audit + user verification
- [ ] `plan.md` + `phase_state.json` updated
- [ ] Notify user that PROJ-443 is ready for `verified` label / archive
