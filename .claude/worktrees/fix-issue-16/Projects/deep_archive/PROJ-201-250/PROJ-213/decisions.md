# PROJ-213: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-28 | Project initialized | Starting point for Build Queue Reversion Bug Fix |
| 2026-02-28 | Calculate cost in command handler, not UI controller | Handler is the correct architectural layer — it's where queue items are created. UI controller's `_build_cost_tracking()` was never called and shouldn't be responsible for data integrity. |
| 2026-02-28 | Keep `turns_remaining: 1.0` as default | ProductionEngine recalculates dynamically via `_update_turns_remaining()` during tick processing. No need to pre-calculate in handler. |
| 2026-02-28 | Graceful fallback to `{}` on design load failure | Matches existing pattern in `BuildQueueController._get_design_cost()`. Logs warning but doesn't block queue addition. |
| 2026-02-28 | Reuse `DesignCostCalculator.calculate_total_cost()` | Same utility already used by `ProductionEngine._calculate_design_cost()`. Centralized, tested, correct. |
