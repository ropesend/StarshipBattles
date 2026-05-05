# PROJ-358: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project ID = PROJ-358 | User-directed sequence start at 356; this is #3 of 5. |
| 2026-05-04 | Project created from realtime-combat tech-debt review | Review finding #7 (P2 hidden-failure): `_apply_spec_components_to_ship` silently drops unmapped components. |
| 2026-05-04 | Manual scaffolding (not via `create_project.py`) | Folder pre-existed with `plan.md`. Mirrored canonical templates from `Projects/scripts/create_project.py` and `Reviews/scripts/review_to_project.py`. |
| 2026-05-04 | Opted into 03c phase-aware execution | Per `.claude/skills/claude-proj-start/SKILL.md` Phase D. |
| 2026-05-04 | Single-phase project | One narrow surface (one function); the validation, error-type choice, and caller contract live together. |
| 2026-05-04 | Reuse `ValidationException` | Per AGENTS.md, prefer existing registries/services/protocols/helpers. Adding a new exception type is unwarranted. |
| 2026-05-04 | Error code `V002 SCHEMA_VALIDATION_ERROR` | Drift is structural (the spec describes a layout the design doesn't have); fits "structural validation error (missing fields, invalid data structure)" closer than V001 generic or V003 missing-entity. |
| 2026-05-04 | Report only the first unmapped key | Keeps the error message focused. The first drift typically points at the root cause (stale design, wrong design_id, compiler bug); subsequent drifts are usually downstream symptoms. |
| 2026-05-04 | Two-pass design (apply, then validate) | Lets the valid-case materialization remain bit-identical (single forward walk through layers). Validation is a `set` diff afterwards — O(n) extra work, no behavioral change for valid specs. |
| 2026-05-04 | Audit found NO existing test fixture relying on silent absorb | All 8 `ComponentStateSpec(...)` usages in tests/ construct entries that map cleanly to their fixture designs. None encoded the bug. |

## Audit Remediation (2026-05-05)

OpenCode review of commit `42749a344` produced 0 CRIT, 2 MAJ findings.
See `Reviews/results/2026-05-05_061731_code_proj-358-review-battle-runner-spec-component-valid_req-req_20260505_061728_88fd15/report.md`.

| Finding | Severity | Verdict | Notes |
|---------|----------|---------|-------|
| CQ-01: Silent skip of unknown component IDs in `ship_serialization.py:198-199` | MAJOR | **Fixed** | Replaced silent `continue` with `raise ValidationException(code=SCHEMA_VALIDATION_ERROR)` carrying `ship_name`, `layer`, `component_id` context. Mirrors the PROJ-358 contract — drift between persisted/serialized component ids and the live registry now surfaces loudly. |
| CQ-02: `battle_runner.py` exceeds 500 LOC ceiling (730 lines) | MAJOR | **Deferred** | Reviewer explicitly noted "Not blocking for PROJ-358 — file as a follow-up cleanup ticket." Effort: Medium. The split touches multiple unrelated subsystems (telemetry, outcome extraction, end-reason derivation) and is a cross-cutting refactor that should be its own ticket so it can be reviewed independently. |

### Test impact (CQ-01 follow-on, addressing CQ-05)

The silent-skip removal exposed test fixtures that had been encoding the bug
(synthetic component ids like `reactor_standard`, `engine_basic`, `bridge_standard`,
`weapon_laser`, `weapon_missile`, `hull_plating`, `reactor`). These were
silently dropped by the old code — the tests asserted on whatever survived
(usually nothing real). All updated to reference real registry components
(`bridge`, `crew_quarters`, `life_support`, `generator`, `fuel_tank`, `battery`,
`mini_battery`, `armor_plate`, `laser_cannon`, `standard_engine`,
`hull_escort`) and to obey layer classification rules:

- `tests/unit/simulation/entities/test_ship_serialization.py::test_from_dict_unknown_component_id` → renamed to `_raises`, now asserts `ValidationException` with full context.
- `tests/unit/ui/services/test_ship_io.py::test_load_ship_ignores_unknown_component_ids` → renamed to `_raises_for_unknown_component_ids`, now asserts the loud failure contract.
- `tests/unit/strategy/test_ship_instance_damage.py` (multiple fixtures): synthetic ids replaced with real registry ids placed in legal layers.
- `tests/unit/strategy/test_ship_consumable_manager.py::ship_with_resources` fixture: `reactor` → `generator`.

Tests run: full sharded suite (`python Tools/test_sharded/test_sharded.py`) — 17777 passed / 0 failed.
