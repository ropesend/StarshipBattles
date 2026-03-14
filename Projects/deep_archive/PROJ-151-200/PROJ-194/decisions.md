# PROJ-194: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Project initialized | Starting point for Builder & Workshop Duck Typing Elimination |
| 2026-02-24 | Include GUI panel hasattr (Cat 4) in scope | Fix by ensuring panels always initialized, not Protocols |
| 2026-02-24 | Include self-attribute checks (Cat 6) in scope | Ensure all attrs declared in __init__ |
| 2026-02-24 | Dynamic resource attrs → typed accessor method | User wants C#/C++/Rust portability; `ship.get_resource_stat()` |
| 2026-02-24 | Keep StatDefinition.get_value() getattr | Intentional generic dispatch pattern (2 instances) |
| 2026-02-24 | No IBuilderShip/IBuilderComponent Protocols needed | Ship/Component APIs are stable; attrs always present |
| 2026-02-24 | Pygame event hasattr (Cat 5) out of scope | Framework boundary, not project code |
