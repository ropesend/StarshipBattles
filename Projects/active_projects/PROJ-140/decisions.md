# PROJ-140: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-13 | Project initialized | Starting point for Colony Ship Colonization Validation |
| 2026-02-13 | Fix all 5 bugs including "Any Planet" validation | User confirmed "Any Planet" should also validate pod match |
| 2026-02-13 | Restructure process_colonize() to pre-check ship before mutation | Risk assessor found order is popped before ship removal — if removal fails, state is inconsistent. Pre-check avoids mutation on failure. |
| 2026-02-13 | Add pre-validation to ColonizeMissionCommandHandler | Even though execution-time validation (Bug 1 fix) catches mismatches, early rejection provides better UX — user doesn't wait for fleet to travel only to fail |
| 2026-02-13 | Access component_registry in mission handler via turn_engine._registries | Matches established pattern used by validate_colonize_order() at turn_engine.py:300. Facade pattern (get_default_registry_provider) is for UI layer only. |
| 2026-02-13 | COLONIZE order serialization bug is out of scope | Planet targets serialize as 'fleet_ref' in FleetOrder.to_dict — separate issue, not causing the reported bugs |
| 2026-02-13 | Preserve legacy path (component_registry=None) | All pod checks are gated on `if component_registry is not None`. Tests explicitly verify backward compatibility. |
