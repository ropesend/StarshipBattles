# PROJ-225 Decisions Log

## DEC-001: Project Creation
- **Date:** 2026-03-24
- **Decision:** Created as Dedup Campaign 2/5, focusing on simulation layer consolidation
- **Source:** General code review `Reviews/results/2026-03-24_200858_general_duplication-consolidation-full-codebase/`
- **Rationale:** PROJ-224 created shared utilities; PROJ-225 consolidates simulation-layer duplication using those utilities and new extraction patterns.

## DEC-002: Scope Exclusions
- **Date:** 2026-03-24
- **Decision:** Excluded DUP-SIM-006 (API naming confusion) and DUP-SIM-008 (validator caching) from scope
- **Rationale:** DUP-SIM-006 (renaming get_ability_total vs get_total_ability_value) requires updating many call sites across layers and is better suited for a dedicated rename refactor. DUP-SIM-008 (validator caching) is a performance optimization, not a dedup task.

## DEC-003: Excluded DUP-SYS findings already handled by PROJ-224
- **Date:** 2026-03-24
- **Decision:** DUP-SYS-004, DUP-SYS-003, DUP-SYS-007, DUP-SYS-008, DUP-SIM-004, DUP-XL-007, DUP-XL-009 all handled by PROJ-224
- **Rationale:** These were part of PROJ-224's Phase 1-4 deliverables.

## DEC-004: weapon_firing_system.py seeker arc check NOT consolidated
- **Date:** 2026-03-24
- **Decision:** The seeker arc check in weapon_firing_system.py is NOT consolidated to use check_firing_solution
- **Rationale:** The seeker launch code uses the arc check for a different purpose: determining launch direction (aim toward target if in arc, else launch in component facing direction). This is semantically different from the accept/reject firing decision in check_firing_solution. Consolidating would change behavior.
