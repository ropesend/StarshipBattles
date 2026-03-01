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
| 2026-03-01 | Project review (Protocol 09) conducted | 8 findings: 2 high (test import, bug table), 3 medium (missing test, line refs), 3 low (clarifications). Changes: Bug table expanded to 8 locations, hex_utils→hex_math, Task 4.7 added, line refs clarified. |
| 2026-03-01 | Bug table expanded from 6 to 8 locations | Added self-destruct (line 613) and stellarate (line 241) to documentation |
| 2026-03-01 | Task 4.7 added for maintenance scuttle test | Ensures all 7 ghost fleet bugs have integration test coverage |
