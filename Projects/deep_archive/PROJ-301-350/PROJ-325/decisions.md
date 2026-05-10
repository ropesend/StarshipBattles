# PROJ-325: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Continuation of PROJ-323 (1 CRIT + 15 MIN findings from OpenCode review) + 2 PROJ-323 deferrals worth pursuing + RaceSetupScreen disposition. Source: continuation review at `AgentCoordination/Scratchpad/plans/proj_321_322_323_continuation_plan.md`. |
| 2026-05-04 | **D-001:** Phase 3 (RaceSetupScreen) starts only after PROJ-324 Phase 3 Task 3.4 reports GO/NO-GO | The RaceSetupScreen migration probe in PROJ-324 produces the signal that scopes Phase 3 here. Starting earlier risks duplicate / conflicting edits to `test_race_setup_screen.py` and `game/ui/screens/race_setup/screen.py`. |
| 2026-05-04 | **D-002:** Phase 1 + Phase 2 may be done in parallel | File-disjoint: Phase 1 touches `Projects/active_projects/PROJ-323/` + `tests/unit/simulation/projectile/`; Phase 2 touches `tests/unit/strategy/engine/` + (TBD) `tests/unit/strategy/data/`. |
| 2026-05-04 | **D-003:** Task 3.34 worth pursuing despite PROJ-323's "deferred with rationale" decision | OpenCode 323-review found rationale factually weak (production handlers split across 5 sub-modules but test file is monolithic 1899 LOC). Two-group parametrize (fleet_id vs entity_id handlers) preserves the legitimate interface boundary. ~75 LOC saved. The Task 3.2 precedent in same project phase already proved the pattern. |
| 2026-05-04 | **D-004:** Task 3.37 worth pursuing despite ≥3-member threshold | OpenCode 323-review FND-P1-003: zero/negative cargo amount tests across load/unload are textbook 2-member parametrize candidates. The threshold rule was slightly too strict here. |
| 2026-05-04 | **D-005:** Phase 3 NO-GO triggers PanelRegistry extraction, NOT RaceSetupScreen rewrite | If `bypass_init` alone doesn't unblock the test wiring, the surgical fix is to extract the 8 panel constructions to a `PanelRegistry` protocol passed in. Avoid rewriting the screen wholesale. |
| 2026-05-04 | **D-006:** If Phase 3 NO-GO estimate exceeds 3 sessions, stop and surface to user | Risk-mitigation. A panel-registry refactor that grows past clean extraction signals hidden coupling — better to defer to a focused PROJ-32y than balloon this project. |
| 2026-05-04 | **D-007:** Out-of-scope items NOT silently dropped | User feedback: "I do not want the additional issues forgotten." All PROJ-322 deferrals not closed by PROJ-324 are queued in PROJ-327. PROJ-326 owns the linter / SystemTreePanel / facade-contract follow-ups. |
| 2026-05-04 | **D-008:** Branch strategy: same as PROJ-324 (`feat/03c-phase-aware-execution` unless user directs otherwise) | Awaiting user confirmation. |
