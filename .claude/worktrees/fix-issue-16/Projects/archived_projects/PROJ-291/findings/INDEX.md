# PROJ-291 Findings Index

> Durable archive of the dual cross-project audit that drove PROJ-291 + PROJ-292.
> Originals lived at `c:/Developer/StarshipBattles/Temp Review Docs/` (the user's working dir). Copies here so the source of truth survives temp-dir cleanup.

## What's in this directory

### Prior 5-skeptic audit (the user's pre-existing review)

| File | Lens | Key findings |
|---|---|---|
| [SUMMARY.md](SUMMARY.md) | Executive summary | 3 Critical (C1, C2, C3) + 4 Major (M1-M4) + 5 Minor + 12 cleared false-positives |
| [pipeline_reachability_skeptic.md](pipeline_reachability_skeptic.md) | End-to-end pipeline reachability | **C1** — Treasury Total excludes Population Upkeep (the audit's headline find; my session-end review missed it) |
| [architecture_shims_skeptic.md](architecture_shims_skeptic.md) | Architecture / shim lifecycle / layer integrity | **C2** — FoodAllocationEditor runtime crash; **M1** — UI→engine layer violation |
| [state_cache_skeptic.md](state_cache_skeptic.md) | State coherence + cache invalidation | **C3** — HappinessEngine wrong-race fallback; **M2** — CachedRaceRegistry no mtime fallback; **M3 (cleared)** — TurnStateSnapshot.restore() vulnerability concern |
| [merge_hazards_skeptic.md](merge_hazards_skeptic.md) | PROJ-289 ↔ PROJ-290 merge hazards | Asymmetric `update_planet` semantics (m1) — flagged as the only real merge hazard; rest are false positives |
| [tests_docs_skeptic.md](tests_docs_skeptic.md) | Test quality + docs/code consistency | **M4** — Treasury Upkeep row not e2e tested; **M5** — CachedRaceRegistry invalidation untested |

### My session-end review (single-pass, 3 layered reviewers)

Lives outside this dir at [`C:\Users\rossr\.claude\plans\perform-a-full-code-zippy-moore.md`](file://C:/Users/rossr/.claude/plans/perform-a-full-code-zippy-moore.md). Identified 1 Critical (the FoodAllocationEditor crash, matches prior audit's C2) + 5 High + 11 Medium + 8 Low. **Missed C1 and M1**, which the prior audit caught.

### Reconciliation + impartial subagent verdicts

Two impartial Explore agents adjudicated the disagreements between the two reviews:

1. **PROJ-289 view-kwarg threading** — my review called it HIGH severity / "UX regression"; prior audit called it MINOR / "by design". **Impartial verdict: MY CALL UPHELD — HIGH.** BuildQueuePanelFactory ONLY shows colonized planets and currently uses legacy single-line rendering. PlanetListWindow shows both colonized + uncolonized. Owner: PROJ-292 Phase 1.

2. **Cache rollback under PROJ-251 error boundary** — prior audit flagged as Major / "VULNERABILITY UNCERTAIN". **Impartial verdict: CLEARED.** `TurnStateSnapshot.restore()` does `session.galaxy = Galaxy.from_dict(...)` — full deserialization that discards the stale planet objects with their `init=False` cache fields. The receiving objects are fresh, so the cache fields can never carry stale data across rollback.

The full reconciliation table lives in [`C:\Users\rossr\.claude\plans\perform-a-full-code-zippy-moore.md`](file://C:/Users/rossr/.claude/plans/perform-a-full-code-zippy-moore.md) under the "Audit reconciliation table" heading.

## How the findings map to projects

| Severity | Finding | Owner |
|---|---|---|
| Critical | C1 — Treasury Total excludes Upkeep | **PROJ-291 Phase 1** |
| Critical | C2 — FoodAllocationEditor crash | **PROJ-291 Phase 3** |
| Critical | C3 — HappinessEngine + PopulationEngine wrong-race fallback | **PROJ-291 Phase 2** |
| High | H1 — view-kwarg dead in 2 callers | **PROJ-292 Phase 1** |
| High | H2 — projector reaches private API | **PROJ-292 Phase 3** |
| High | H3 — net-cell colour exception swallow | **PROJ-292 Phase 4** |
| Major | M1 — UI→engine layer violation | **PROJ-292 Phase 2** |
| Major | M2 — CachedRaceRegistry untested + no mtime | **PROJ-292 Phase 3** |
| Major | M3 — Treasury Upkeep row not e2e tested | **PROJ-291 Phase 1 Task 1.3** (closes simultaneously with C1 fix) |
| Major | M4 — TurnStateSnapshot.restore cache concern | **CLEARED** by impartial subagent |
| Minor | m1, m4-m13 | **PROJ-292 Phase 5** |
| Minor | m17 (`projects_index.md` typo) | **PROJ-292 Phase 5 Task 5.1** |

## After PROJ-291 + PROJ-292 close

The user can delete `c:/Developer/StarshipBattles/Temp Review Docs/` — the originals are no longer needed. This `findings/` directory is the durable archive.
