# PROJ-234: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-28 | Scope: Bridge + Serializer extraction (not Stats) | Gets file under 500L target. Stats cluster is already a thin cache wrapper over ShipStatsCalculator — extraction adds complexity without reducing ShipInstance responsibilities. |
| 2026-03-28 | Delete `from_ship()` classmethod | Zero callers in entire codebase. Active path uses `update_from_ship()` via FleetBattleAdapter. Dead code removal per CLAUDE.md policy. |
| 2026-03-28 | Fix magic numbers during extraction | Lines touching during refactor anyway. `_DEFAULT_MAX_HP = 100` and `SERIAL_FORMAT = '06d'`. |
| 2026-03-28 | Bridge = eager delegate (not static utility) | Bridge mutates parent state in `update_from_ship()` (sets `current_hp`, `is_alive`, `component_damage`, etc.). Needs parent reference. Matches ShipResourceManager/ShipCargoManager pattern. |
| 2026-03-28 | Serializer = static utility (not delegate) | Serialization is stateless. `from_dict()` is a constructor — doesn't need existing instance. Matches FleetOrderSerializer pattern. |
| 2026-03-28 | Keep facade methods on ShipInstance | 126+ existing tests call ShipInstance methods directly. Facades preserve exact signatures and semantics. Zero test changes, zero call-site changes. |
| 2026-03-28 | Do NOT align delegates to Fleet's PROJ-210 property pattern | User explicitly chose to keep ShipInstance's facade-method pattern. Aligning would change 40+ call sites — too disruptive for this project. |
| 2026-03-28 | Phase order: dead code → minor fixes → serializer → bridge | Safest sequence. Dead code removal is zero-risk. Minor fixes clean up before extraction. Serializer has simpler deps (no cross-layer imports) so proves the pattern before tackling the more complex bridge. |
