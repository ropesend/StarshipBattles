# PROJ-67: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-07 | Project initialized | Starting point for Fleet Space Yards |
| 2026-02-07 | Reuse SpaceShipyardAbility, new component | Create `fleet_space_yard` component with `allowed_vehicle_types: ["Ship"]` using existing `SpaceShipyardAbility`. Avoids duplicate ability class, system treats them identically. |
| 2026-02-07 | Explicit BUILD order type | Add `OrderType.BUILD` to fleet orders. Fleet must be explicitly ordered to build. While building, movement orders are blocked. Player must cancel build to move. |
| 2026-02-07 | Built ships join building fleet | Completed ships from fleet yards join the building fleet directly. Simpler than spawning new fleets. |
| 2026-02-07 | Generalize BuildQueueScreen | Refactor BuildQueueScreen to accept a 'build context' (planet or fleet) instead of just a planet. Maximum code reuse. |
| 2026-02-07 | Time-only build costs (for now) | Fleet yards just need turns to build. Resource costs deferred to future project. |
| 2026-02-07 | Same hex as planet for complex building | Fleet must be at exact same hex coordinate as a planet to build complexes. More restrictive but clearer rule. |
| 2026-02-07 | Full vehicle type support | Fleet yards can always build ships/fighters/satellites. Complexes only when at same hex as a planet. |
| 2026-02-07 | Test baseline: 6244 passed, 2 pre-existing failures | Screenshot tests (test_bug_15) fail independently - not related to this project. |
