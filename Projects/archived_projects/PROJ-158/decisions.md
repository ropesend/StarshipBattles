# PROJ-158: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-20 | Project initialized | Starting point for Eradicate Dead Production API and Fix Production Tests |
| 2026-02-20 | No legacy item support | Per CLAUDE.md: eradicate old systems completely. All queue items must have `total_cost` + `resources_consumed`. Items without these fields are invalid. |
| 2026-02-20 | Delete `process_production()` entirely | It's an empty stub (`pass`). The real work happens in `process_construction_tick()` during the 100-tick loop. No reason to keep a dead method. |
| 2026-02-20 | Delete `process_fleet_production()` entirely | Same — empty stub, fleet production handled in tick loop via `process_construction_tick()`. |
| 2026-02-20 | `cost_per_tick` is a dead field — do not use in tests | Dynamic system calculates per-tick consumption from `production_rates.json` rates and `total_cost`. The item-level `cost_per_tick` is never read. |
| 2026-02-20 | `ticks_in_current_turn` is a dead field — do not assert on it | Dynamic system tracks progress via `resources_consumed` fractionally, not via an integer tick counter. |
| 2026-02-20 | Delete ~33 unit tests, rewrite ~41 tests | Tests calling dead API are deleted (behavior now covered by tick system). Tests validating real behavior (completion, spawning, gating, economy) are rewritten to use live API. |
| 2026-02-20 | Fix tests, not production code | The production engine's tick-based system works correctly. The failures are test-side — calling dead methods or asserting on dead fields. No production code logic changes needed (only API surface deletion). |
| 2026-02-20 | Use `production_rates.json` values in test calculations | Tests must calculate expected consumption based on the actual rates (planetary_yard=2000/turn=20/tick, shipyard=3000/turn=30/tick). No hardcoded per-item rates. |
