# Projects Index

## Active Projects

| ID | Title | Status | Started | Last Updated |
|----|-------|--------|---------|--------------|
| PROJ-21 | Legacy Cleanup Phase 8: Tests and Patterns | Planning | 2026-01-26 | 2026-01-26 |

## Archived Projects

| ID | Title | Status | Started | Completed |
|----|-------|--------|---------|-----------|
| PROJ-20 | Standardize Data Formats | Archived | 2026-01-26 | 2026-01-27 |
| PROJ-19 | Standardize Data Formats | Archived | 2026-01-26 | 2026-01-26 |
| PROJ-18 | Standardize Registry Access | Archived | 2026-01-25 | 2026-01-26 |
| PROJ-17 | Enforce Layer Boundaries | Archived | 2026-01-25 | 2026-01-26 |
| PROJ-16 | Consolidate Re-exports (Phase 3) | Archived | 2026-01-25 | 2026-01-26 |
| PROJ-15 | Phase 2 - Remove Shims and Aliases | Archived | 2026-01-25 | 2026-01-25 |
| PROJ-14 | Legacy Cleanup Phase 1 - Delete Dead Code | Archived | 2026-01-25 | 2026-01-25 |
| PROJ-12 | God Class Decomposition | Archived | 2026-01-24 | 2026-01-25 |
| PROJ-13 | Code Quality & Documentation | Archived | 2026-01-24 | 2026-01-25 |
| PROJ-11 | Architecture Layer Separation | Archived | 2026-01-24 | 2026-01-24 |
| PROJ-10 | Error Handling & Logging Remediation | Archived | 2026-01-24 | 2026-01-24 |
| PROJ-09 | Test Coverage Remediation | Archived | 2026-01-23 | 2026-01-24 |
| PROJ-08 | Data-Driven Resource System | Archived | 2026-01-21 | 2026-01-24 |
| PROJ-07 | Strategy Layer Stats Refactor | Archived | 2026-01-21 | 2026-01-23 |
| PROJ-06 | Quickstart 1P / 2P Buttons | Archived | 2026-01-21 | 2026-01-24 |
| PROJ-01 | Design Workshop UI Enhancement | Archived | 2026-01-21 | 2026-01-23 |
| PROJ-02 | Race Setup Screen | Archived | 2026-01-21 | 2026-01-23 |
| PROJ-03 | Fleet Report Window | Archived | 2026-01-21 | 2026-01-23 |

---

## Status Legend

- **Planning** - Initial analysis and plan creation in progress
- **In Progress** - Implementation underway
- **Auditing** - Skeptical review in progress
- **Awaiting Verification** - Audit passed, waiting for user to verify
- **Revision** - Completed project reopened for changes based on user feedback
- **Archived** - Completed and archived

---

## Project Summaries

### PROJ-16: Consolidate Re-exports (Phase 3)
**Scope:** Legacy Code Cleanup Phase 3 - Update callers to import from canonical locations and remove re-exports
**Phases:** 5 (PLANET_RESOURCES → Component Constants → AI Re-exports → Ship Loader → Wrapper Evaluation)
**Key Goals:** Remove re-exports from component.py, ship.py, controller.py, planet.py; Remove ShipControllableAdapter backward compat in stages
**Dependencies:** Phase 2 (Remove Shims & Aliases) should be complete
**Source:** [legacy_cleanup/PHASE_3_CONSOLIDATE_REEXPORTS.md](legacy_cleanup/PHASE_3_CONSOLIDATE_REEXPORTS.md)

### PROJ-15: Phase 2 - Remove Shims and Aliases
**Scope:** Legacy Code Cleanup Phase 2 - Remove backward compatibility shims and aliases
**Phases:** 6 (Singleton Aliases → Fleet Warp → ShipBuilderService → PathSegment/to_hit_profile → Deprecated Functions → Builder Shims)
**Key Goals:** Delete 5 shim files, remove method aliases, standardize singleton access, remove deprecated functions
**Dependencies:** Phase 1 (Dead Code Deletion) must be complete
**Source:** [legacy_cleanup/PHASE_2_REMOVE_SHIMS_ALIASES.md](legacy_cleanup/PHASE_2_REMOVE_SHIMS_ALIASES.md)

### PROJ-10: Error Handling & Logging Remediation
**Scope:** 47 error handling issues from code review
**Phases:** 4 (Critical → Major → Minor → Standardization)
**Key Goals:** Eliminate bare except clauses, add logging to all handlers, standardize patterns
**Dependencies:** None (can start immediately)
**Source:** [Review 2026-01-24_general_full-codebase-maintainability](../Reviews/results/2026-01-24_general_full-codebase-maintainability/)

### PROJ-11: Architecture Layer Separation
**Scope:** 13+ architecture findings - layer violations
**Phases:** 4 (Core Math → Simulation → Strategy-UI → Interfaces)
**Key Goals:** Remove pygame from simulation, remove UI from strategy, enable headless execution
**Dependencies:** Should complete PROJ-10 first
**Source:** [Review 2026-01-24_general_full-codebase-maintainability](../Reviews/results/2026-01-24_general_full-codebase-maintainability/)

### PROJ-12: God Class Decomposition
**Scope:** Ship (750 lines), TurnEngine (737 lines), RaceSetupScreen (2325 lines)
**Phases:** 5 (Ship Combat → Ship Components → TurnEngine → RaceSetupScreen → AIController)
**Key Goals:** Reduce all classes to <400 lines, improve testability
**Dependencies:** Should complete PROJ-11 first
**Source:** [Review 2026-01-24_general_full-codebase-maintainability](../Reviews/results/2026-01-24_general_full-codebase-maintainability/)

### PROJ-13: Code Quality & Documentation
**Scope:** Dead code, magic numbers, documentation gaps, remaining quality issues
**Phases:** 5 (Dead Code → Constants → Documentation → UI Patterns → Remaining)
**Key Goals:** Remove dead code, document core systems, extract constants
**Dependencies:** Can run in parallel with other projects
**Source:** [Review 2026-01-24_general_full-codebase-maintainability](../Reviews/results/2026-01-24_general_full-codebase-maintainability/)

---

## Recommended Execution Order

```
PROJ-10 (Error Handling) ✅ COMPLETE ──────────────────────┐
                                                           │
PROJ-13 Phase 1 (Dead Code) ───────────────────────────────┤
                                                           │
                    PROJ-11 (Architecture) ✅ COMPLETE ────┤
                              │                            │
                              ▼                            │
                    PROJ-12 (God Classes) ─────────────────┤
                              │                            │
                              ▼                            │
                    PROJ-13 Phase 3-5 (Docs, Quality) ─────┘
```

---

## Next Project ID: PROJ-22
