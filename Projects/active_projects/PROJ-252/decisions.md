# PROJ-252: Decisions Log

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-06 | Use `random.Random(seed)` instances, not global `random.seed()` | Per-instance RNG is the standard Python pattern for deterministic subsystems. Thread-safe, no cross-contamination. |
| 2026-04-06 | Keep module-level `log_event()` as deprecated convenience during migration | Many call sites use it. Incremental migration: inject EventBus where available, fall back to global, then ratchet. |
| 2026-04-06 | Extract registries from Ship (already holds them) rather than adding new constructor params | ShipComponentManager already receives Ship; Ship already holds `_registries`. No new plumbing needed. |
