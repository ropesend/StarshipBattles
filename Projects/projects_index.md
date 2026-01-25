# Projects Index

## Active Projects

| ID | Title | Status | Started | Last Updated |
|----|-------|--------|---------|--------------|
| PROJ-15 | Phase 2 - Remove Shims and Aliases | Planning | 2026-01-25 | 2026-01-25 |
| PROJ-14 | Legacy Cleanup Phase 1 - Delete Dead Code | Ready for Implementation | 2026-01-25 | 2026-01-25 |

## Archived Projects

| ID | Title | Status | Started | Completed |
|----|-------|--------|---------|-----------|
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

## Next Project ID: PROJ-16
