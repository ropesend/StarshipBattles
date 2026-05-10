# Review Scope: PROJ-358 Review: Battle Runner Spec Component Validation

**Type:** code
**Request ID:** req_20260505_061728_88fd15
**Created:** 2026-05-05T06:17:28Z
**Requester:** claude-code

## Scope

- `game/simulation/battle_runner.py` (`_apply_spec_components_to_ship`)
- `tests/unit/simulation/battle_runner/test_spec_component_validation.py` (new)
- `Projects/active_projects/PROJ-358/decisions.md`

## Instructions

1. Verify the `ValidationException` surfaces all 4 context fields (ship_id, component_id, instance_index, design_id) in both message and `context` dict
2. Confirm bit-identical materialization for currently-valid specs (the two-pass implementation)
3. Audit OTHER silent-drift paths in the simulation layer that may use similar 'design drift' justifications
4. Check that the chosen error code (V002 SCHEMA_VALIDATION_ERROR) is consistent with project conventions for validation errors
5. Verify the new tests would fail on the unfixed code (TDD)

## Context

Just-completed project commit `42749a344`. Touches the same file as PROJ-354A (`cd8ebf5e5`) but a different function -- verify no overlap.

## Review Mode

Single-reviewer direct analysis (small scope, 3 files, specific questions). No agent swarm launched due to focused nature of review instructions.

## Reference Documents

- `docs/README.md` -- Documentation index
- `docs/01_ARCHITECTURE.md` -- Layer structure and dependency rules
- `docs/02_PATTERNS.md` -- Design patterns reference
- `docs/03_CONVENTIONS.md` -- Coding conventions
- `docs/05_ERROR_HANDLING.md` -- Error handling guidelines
- `game/core/exceptions.py` -- Exception hierarchy
- `game/core/error_codes.py` -- Error code enumeration
- `game/simulation/battle_spec.py` -- BattleSpec DTOs
