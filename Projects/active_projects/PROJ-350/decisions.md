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
