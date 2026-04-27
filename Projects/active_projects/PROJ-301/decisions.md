# PROJ-301: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-26 | Project initialized | Starting point for Planet Intrinsic Ability Sources |
| 2026-04-26 | **Planets-themselves are a separate `IAbilitySource` from their facilities** | Conceptually distinct: a volcanic planet's intrinsic plasma plumes are not a "facility" you build; they are a property of the planet. Two `IAbilitySource` adapters wrap the same Planet instance — `FacilityAbilitySource` (one per facility) and `PlanetIntrinsicAbilitySource`. Both contribute to Sector Effects. |
| 2026-04-26 | **Planet intrinsic abilities are ownerless (`owner_id=None`)** | The volcano damages friend and foe equally. If "this planet's effect only applies to its owner" is needed later, declare that via `scope: allied_sector` on the ability data — not by toggling owner_id. Keeps the adapter rule simple. |
| 2026-04-26 | **Intrinsic abilities support generation-time rolls via `{"min": x, "max": y}`** in registry | Per user direction: "some values will need to be generated at galaxy creation, damage amounts etc..." Registry holds the template; instance carries the rolled scalar. A shared `roll_intrinsic_abilities` helper handles the conversion and is reused in PROJ-302/303/304. |
| 2026-04-26 | **Empty `abilities` dicts are allowed** for planet types with no intrinsic effects (oceanic, terrestrial, barren) | Cleaner than maintaining "list of types that have intrinsic abilities." The iterator skips planets whose `get_abilities()` returns `{}`. |
| 2026-04-26 | **`source_label` format: `"{planet.name} ({type.capitalize()})"`** e.g. `"Tarsis IV (Volcanic)"` | Matches the precedent set by PROJ-300 storms (`"Ion Storm Alpha"`) — descriptive, identifies both the instance and its type. |
