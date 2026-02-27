# PROJ-190: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-24 | Project initialized | Starting point for Core Simulation Duck Typing Elimination |
| 2026-02-25 | Scope: game/simulation/ only (~97 instances) | User chose focused scope. Other layers (ai, strategy, ui) will be separate future projects. |
| 2026-02-25 | Comprehensive replacement (not targeted) | User's goal is language portability to C#/C++/Rust. ALL contracts must be explicit since those languages require it. |
| 2026-02-25 | Protocols in game/simulation/interfaces/ | Maintains layer separation. Follows existing pattern (IAIController already lives there). |
| 2026-02-25 | formula_system.py builtins check exempt | `hasattr(builtins, name)` is legitimate Python introspection for safe formula evaluation. No C#/Rust equivalent needed — this is a Python-specific security pattern. |
| 2026-02-25 | 15 protocols across 3 new files | Grouped by domain: ability_protocols.py (9), component_protocols.py (1), entity_protocols.py (5). Avoids mega-file, maintains logical separation. |
| 2026-02-25 | Protocol composition via inheritance | IWeaponAbility extends IAbility, ISeekerWeaponAbility extends IWeaponAbility. Maps directly to C# interface inheritance and Rust trait bounds. |
| 2026-02-25 | Lazy init → Optional fields in __init__ | Replace `hasattr(self, '_field')` with `self._field: Optional[T] = None` and `is None` checks. This is the standard C#/Rust pattern (nullable/Option). |
| 2026-02-25 | Test mock updates in dedicated Phase 5 | ~50-80 test failures expected from stricter typing. Isolate mock updates to avoid mixing behavioral changes with test changes. |
| 2026-02-25 | @runtime_checkable on all protocols | Enables isinstance() checks at runtime, not just type-checking time. Matches existing codebase pattern. |
| 2026-02-25 | TypeGuard helper functions for each protocol | Following established pattern in game/core/protocols.py where every protocol has an `is_X()` TypeGuard. |
