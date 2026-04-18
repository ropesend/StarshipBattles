# PROJ-278: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-04-17 | Project initialized | Starting point for Unified Role Registry (design_role + Combat Lab scenario_role) |
| 2026-04-17 | Unify the machinery (one `Role` schema + one `RoleRegistry` class), NOT the instances | User chose "Both — unified Role concept". A ship's design_role is intrinsic and persistent; its scenario_role is positional and ephemeral. Sharing the schema is a clean win; sharing the instance would conflate two orthogonal axes |
| 2026-04-17 | Combat Lab loads its own roles from `combat_lab/data/scenario_roles.json` | User: "the combat lab loads it's own data files for some things already, we can do the same for roles". Matches existing pattern (Combat Lab owns its own components.json + ship JSONs) |
| 2026-04-17 | `design_role` storage is layered: base file + mod overlays + user overlay | User: "Mods are made by altering the base .json files" + user-overlay file for runtime additions. Same machinery serves modding AND runtime player additions |
| 2026-04-17 | Two separate fields on ShipSpec: `design_role: Optional[str]` and `scenario_role: Optional[str]` | A unified `role` field would conflate two concepts (intrinsic-persistent vs positional-ephemeral). Two fields are honest about the orthogonality |
| 2026-04-17 | Combat Lab `scenario_role` registry uses `allow_runtime_add=False` | Players don't write Combat Lab scenarios; runtime add is meaningless there. Same `RoleRegistry` class, but the instance refuses mutation |
| 2026-04-17 | UI for player runtime-add is OUT OF SCOPE | User: "We do not need to implement the UI for the player to do this yet". Project delivers the data model + API only |
| 2026-04-17 | Full mod system loader is OUT OF SCOPE | Loader tolerates a `mods/` directory if it exists, but loose-file mod resolution beyond design_role is its own future project |
