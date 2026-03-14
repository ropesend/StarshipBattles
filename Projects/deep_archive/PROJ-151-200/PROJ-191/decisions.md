# PROJ-191: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Project initialized | Starting point for Strategy Layer Duck Typing Elimination |
| 2026-02-24 | Use concrete types (not protocols) for intra-layer type hints | Strategy engines exclusively operate on Empire, Planet, Fleet — all in `game/strategy/data/`. No abstraction benefit to protocols within the same layer. Protocols are for cross-layer boundaries. |
| 2026-02-24 | Replace getattr with direct attribute access | All domain objects have well-defined __init__ / dataclass fields. The getattr defaults are never used in production — they only protect against unspec'd test mocks, which is a testing anti-pattern. |
| 2026-02-24 | Replace hasattr type discrimination with isinstance | `hasattr(obj, 'planet_type')` is fragile (multiple types could have same attr). `isinstance(obj, Planet)` is explicit and type-safe. Use concrete types since we're within the strategy layer. |
| 2026-02-24 | Keep getattr for comp_def dual-format access | Component definitions come as either dict (JSON) or Component (simulation). Both need `abilities` access. getattr is legitimate here — document with comments. |
| 2026-02-24 | Keep getattr in from_dict() deserialization | Save file compatibility requires handling missing fields. These are external data boundaries where getattr is appropriate. |
| 2026-02-24 | Update test mocks to use spec= parameter | Bare Mock() hides attribute errors. Mock(spec=Empire) ensures mocks match the real interface. Test_population_engine.py already uses real objects — gold standard. |
| 2026-02-24 | Use isinstance for cargo_transfer_service DTO discrimination | User approved: replace hasattr duck typing in get_inventory_items() with isinstance(obj_info, FleetInfo) / isinstance(obj_info, PlanetInfo) checks. |
