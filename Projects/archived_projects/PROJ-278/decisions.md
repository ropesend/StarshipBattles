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
| 2026-04-17 | Phase 1 RoleRegistry test JSON shape: `{"roles": [{...}, ...]}` (list of dicts) | Existing `data/design_roles.json` uses `{"roles": {id: {...}}}` (dict-keyed-by-id) with field names `name`/`allowed_vehicle_types`. Phase 2 will port the file to the new shape — see Phase 2 decisions below |
| 2026-04-17 | Phase 1 chose plain `KeyError` for `RoleRegistry.get(missing_id)` over a domain-specific exception | Consistent with dict-like API. Subsystems wanting a domain exception can wrap the lookup |
| 2026-04-17 | Phase 1 chose `load_json_required` (raises) over `load_json` (silent default) | Critical config files — silent failure would mask data corruption. User-overlay path (which may not exist) gets a separate `load_from_file_optional` method in Phase 2 |
| 2026-04-17 | Phase 1: callback exceptions in `_fire_invalidation_callbacks` are caught + logged, not re-raised | A misbehaving subscriber should not block correct registration or prevent other callbacks from firing. Matches graceful-degradation pattern in `event_logging.py` |
| 2026-04-17 | **Phase 2 decision: Port `data/design_roles.json` to new shape** (option a, not extend loader) | User answered: "Port". Single migration, no permanent loader complexity. Field renames: `name` → `display_name`, `allowed_vehicle_types` → `vehicle_type_filter`. Dict-keyed-by-id → list-of-dicts |
| 2026-04-17 | **Phase 2 decision: Delete `DesignRoleRegistry` class entirely + migrate all 4 production call sites + 1 test file** | User answered: "delete and migrate". Per codebase eradicate-old-systems policy. Keep `DesignRole` enum + `classify_*` functions in `design_role.py` (orthogonal concerns); only the registry class goes away |
| 2026-04-17 | **Phase 2 decision: Add `load_from_file_optional` to `RoleRegistry`** | User answered: "yes, add it". Tolerates missing file (returns silently); still raises on malformed JSON. Used for `user_data/design_roles.json` overlay which won't exist on first run |
| 2026-04-17 | Phase 2: add `get_roles_for_vehicle_type` query method to `RoleRegistry` | Production callers use this lookup pattern. It's general-purpose — any code can ask "which roles match this vehicle type?". Migration replaces the legacy `DesignRoleRegistry.get_roles_for_vehicle_type` directly |
| 2026-04-17 | Phase 2: new module `game/strategy/data/design_role_registry.py` for layered loading + module-level accessor | Keeps the layered-loading + ApplicationContext-style accessor close to the strategy domain that consumes it. `game/core/roles.py` stays generic — no domain knowledge of file paths or layering specifics |
