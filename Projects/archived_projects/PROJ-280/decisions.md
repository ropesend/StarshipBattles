# PROJ-280: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-17 | Project initialized | Starting point for Combat Lab Template Deduplication + Authoring Rules |
| 2026-04-17 | Approach: authoring rules + base-class enforcement | User chose "Authoring rules + base-class enforcement (Recommended)". Doc-only relies on author discipline; light enforcement leaves no signal when drift occurs. Hard guardrails prevent re-bloat |
| 2026-04-17 | Sequencing: AFTER PROJ-279 | PROJ-279 simplifies TestScenario base by removing the `to_spec` stub. Working on a clean base avoids touching the same code twice |
| 2026-04-17 | Enforcement mechanism choice DEFERRED to Phase 3 | Three candidate mechanisms (AST inspection / runtime sentinel / composition API). Choice depends on assessment of how invasive the API change is — Phase 3 evaluates |
| 2026-04-17 | Out of scope: adding NEW templates | This project is consolidation. Anyone wanting new templates after this lands has clearer guardrails to follow |
