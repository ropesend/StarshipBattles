# PROJ-350: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Starting point for Combat Lab Registry Class Identity Fix |
| 2026-05-04 | Fix via `importlib.import_module`, not skip-list expansion | Architectural fix vs bandaid: `import_module` honors `sys.modules`, eliminating the duplicate-class-object class of bugs entirely. Skip-list patches one symptom but leaves the trap in place for future support modules. Verified independently by Claude and Codex. |
| 2026-05-04 | Project ID = PROJ-350 | User-directed correction. PROJ-343..PROJ-349 already exist in `Projects/active_projects/`; next free is PROJ-350. (Codex's `create_project.py` read returned PROJ-343, but direct directory inspection is authoritative.) |
| 2026-05-04 | Out of scope: `combat_lab/runner.py:271-292` | Codex's blast-radius scan: the only other prod user of `spec_from_file_location`, but it loads an explicit CLI-supplied path as `dynamic_scenario` and never overwrites `combat_lab.scenarios.templates`. No latent bug; no scope expansion. |
| 2026-05-04 | Discussion outcome | Inter-agent discussion (Claude+Codex, v2.6 protocol) reached unanimous consensus. Record: `AgentCoordination/Scratchpad/Discussion/20260505T010845Z_spec-compiler-class-identity/outcome.md`. Implementation owner: Claude. |

## Audit Remediation

OpenCode review (`Reviews/results/2026-05-05_073254_code_proj-350-review-combat-lab-registry-class-identity_req-req_20260505_073252_fd4806/report.md`) reported 0 CRIT, 2 MAJ, 2 MIN, 1 INFO, 1 NIT against commit `d555e8bd1`. Overall verdict: PASS.

| Finding | Severity | Verdict | Action |
|---------|----------|---------|--------|
| MAJ-001: Regression test correctly pins class-identity invariants | MAJ (positive) | Accept | No remediation. Report explicitly states "test is correctly constructed. No remediation needed." Test exercises `isinstance`, object-identity (`is`), and the functional `build_test_battle_spec` crash site that originally raised `NotImplementedError`. |
| MAJ-002: No remaining `spec_from_file_location` / `module_from_spec` in registry path | MAJ (positive) | Accept | No remediation. Report explicitly states "Fix is clean and complete. No remediation needed." Verified: `combat_lab/registry.py` uses `importlib.import_module`; no `importlib.util` import; no `spec_from_file_location`/`module_from_spec`/`exec_module` calls remain in registry. |
| MIN-001, MIN-002, INFO-001, NIT-001 | MIN/INFO/NIT | Skipped per remediation scope (MAJ-only). | NIT-001 (`templates.py` 1343 LOC) noted; the 500 LOC ceiling applies to `game/` production source, not Combat Lab test infrastructure. |

Tests run: `pytest tests/unit/combat_lab/ -v` — 268 passed. Both MAJ findings are positive confirmations of the fix; the audit identified zero defects requiring code changes.
