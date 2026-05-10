# PROJ-407: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-09 | Project initialized | Starting point for Tier 3: stale docs + architecture wording sweep (D-01..D-09) |
| 2026-05-09 | D-03 reconciliation: 05_ERROR_HANDLING.md | Live `EventBus` (`game/core/event_logging.py`) only exposes `__init__(handler=None)`, `set_handler(handler)`, and `log_event(event_type, **kwargs)`. The module-level `log_event` / `set_event_handler` / `get_event_handler` shim was retired by PROJ-390 and the file no longer defines those functions. Doc previously stated the shim "remains compatibility API"; replaced with the session-scoped, constructor-injected pattern matching `02_PATTERNS.md` §6 EventBus and the module's own docstring. Also corrected the Source Files line and renamed `set_event_handler` to the live method name `set_handler`. |
| 2026-05-09 | D-03 reconciliation: 01_ARCHITECTURE.md line 96 | Was: "`EventBus`, event handler accessors, `log_event`." That implied the module-level accessors still exist. Replaced with: "session-scoped `EventBus` class (constructor-injected; PROJ-390 retired the module-level shim)." |
| 2026-05-09 | D-08 type tightening: `TaskForceSpec.formation` | Tightened from the Phase 1 `formation: object` vestige to `FormationSpec \| None`. Enforced via `__post_init__` (frozen dataclass, no native annotation enforcement) — invalid types raise `TypeError` at construction. Replaced the silent isinstance-drop fallback in `_task_force_spec_to_dict` with a direct call. Updated test fixture `_SENTINEL_FORMATION` to a real `FormationSpec(LINE_ABREAST, 100.0)` and rewrote the legacy "serializes non-FormationSpec as None" test to assert the new TypeError contract. TDD trail: RED -> GREEN. |
