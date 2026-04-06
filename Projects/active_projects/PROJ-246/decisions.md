# PROJ-246: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-06 | Project initialized | Starting point for Silent Formula Evaluation Failure |
| 2026-04-06 | Keep `safe_evaluate` in `_evaluate_formulas_in_abilities` | Ability formulas may contain runtime variables (e.g. `range_to_target`) that are not available at load time. Switching to strict `evaluate()` would crash on valid production data (e.g. railgun's damage formula). Only attribute formulas and resource_cost formulas are pure data-loading formulas suitable for strict mode. |
| 2026-04-06 | Fix `sync_data()` missing formula context | Pre-existing bug: `sync_data()` called `_parse_formula_field()` without `formula_context`, so formulas with `range_to_target` would fail. Previously masked by `safe_evaluate`. Fixed by passing `{'range_to_target': 0}` default context, matching `__init__` behavior. |
