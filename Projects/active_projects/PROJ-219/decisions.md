# PROJ-219: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-28 | Project initialized | Starting point for Fleet Registration Consolidation |
| 2026-02-28 | Use optional `_galaxy` parameter in Empire.__init__ | Preserves backward compatibility with 50+ tests that create Empire without Galaxy |
| 2026-02-28 | Add `set_galaxy()` method for late binding | Needed for deserialization where Galaxy loads before Empires |
| 2026-02-28 | Use `if self._galaxy:` guards in add/remove_fleet | Fail-safe when galaxy unavailable (unit tests, partial construction) |
| 2026-02-28 | Do NOT serialize `_galaxy` | Transient reference, re-established on load |
| 2026-02-28 | Keep explicit registration loop in GameSession.from_dict | Deserialized fleets bypass `add_fleet()`, need explicit registration |
| 2026-02-28 | Include unregistration bug fixes in scope | User confirmed: fix all 6 ghost fleet bugs as part of consolidation |
| 2026-02-28 | Proceed despite 42 failing baseline tests | User confirmed: pre-existing failures unrelated to fleet registration |
| 2026-02-28 | Remove explicit unregister in stellarate | After change, `remove_fleet()` auto-unregisters; `pop(id, None)` is idempotent anyway |
| 2026-02-28 | Empire-Galaxy coupling acceptable | Both in Strategy layer, same pattern as Empire-Planet coupling |
| 2026-02-28 | No `restore_fleet()` method needed | Fleets restored via Empire.from_dict, explicit registration in GameSession |
