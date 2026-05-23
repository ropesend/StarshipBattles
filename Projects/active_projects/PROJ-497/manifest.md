# PROJ-497 File Manifest

> Used by `/proj-parallel` for conflict detection. Updated if implementation
> discovers additional files.

## Files

| File | Type | Notes |
|------|------|-------|
| data/modifiers.json | Data | Conditional edit (efficient_engines, facing/turret_mount seeker rows) — only if user approves in Phase 1 |
| data/components.json | Data | Conditional edit (mini_capital_missile type AND ability payload) — only if user approves in Phase 1. See Phase 2 Task 2.2 warning: type-only edit is a no-op for allowance check |
| tests/regression/modifier_ability_snapshots/test_utility_modifiers.py | Test | Possibly affected if efficient_engines is edited/deleted |
| tests/regression/modifier_ability_snapshots/test_weapon_modifiers.py | Test | Possibly affected if facing/turret_mount seeker rows change |
| tests/regression/snapshots/*.json | Test fixtures | Re-shot or pruned if data edits change rendered output |
| docs/guides/modifier_system.md | Doc | Phase 3 Task 3.1: add "data-intent decisions" reference + remove efficient_engines if deleted |
| docs/guides/adding_modifiers.md | Doc | Phase 3 Task 3.2: clarify allow_abilities key namespace |
| Projects/active_projects/PROJ-498/findings/source_review.md | Project doc (sibling) | Phase 3 Task 3.3: append "PROJ-497 outcomes" handoff |
| AgentCoordination/discovered_issues/log.jsonl | DI log | Phase 3 Task 3.4: resolve or accept-known DI-2026-05-23-004 |
| Projects/active_projects/PROJ-497/decisions.md | Project doc | All user decisions recorded with rationale |

## Conflicts with PROJ-498
PROJ-498 (sibling engineering hardening project) touches:
- `game/simulation/services/modifier_service.py` (reason API)
- `game/simulation/battle_state.py` and `game/simulation/entities/ship_serialization.py` (rejection logging)
- New parametrized rejection-matrix test under `tests/regression/modifier_ability_snapshots/`

PROJ-497 and PROJ-498 share `data/modifiers.json` only if the rejection-matrix test in
PROJ-498 hard-codes expected rejected pairs. Avoid that — derive the matrix from
`data/modifiers.json` + `data/components.json` at test-collection time so PROJ-497 data
edits do not break PROJ-498 tests. **Execution order: PROJ-497 then PROJ-498.**
