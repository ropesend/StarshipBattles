# PROJ-439: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-17 | Project initialized | Starting point for Content Contracts and Loader Validation |
| 2026-05-17 | Use `03c-phase-aware-execution` for PROJ-439 | The work is multi-phase, cross-cutting, and benefits from phase-level validation and cumulative review gates. |
| 2026-05-17 | Charter source is the shared roadmap discussion plus direct local code review | `tech_debt_roadmap_r001.md` already captured the agreed shape for PROJ-439..442; reusing it avoids re-litigating scope. |
| 2026-05-17 | Baseline for project start is the canonical sharded suite, not ad hoc focused tests | `python Tools/test_sharded/test_sharded.py` passed `21233/21233`, giving the project a real starting baseline. |
| 2026-05-17 | The project is schema-first and loader-first, not a runtime object-model rewrite | The agreed roadmap explicitly scoped out a Pydantic migration and a whole-sale `FormulaEvaluator` replacement. |
| 2026-05-17 | No fresh Codex subagent swarm was launched during initialization | Current Codex instructions disallow unrequested delegation, so the plan records sequential-review findings instead. |
