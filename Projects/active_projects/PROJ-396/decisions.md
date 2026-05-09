# PROJ-396: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-08 | Project initialized | Starting point for PROJ-382 remediation — review CRITICAL + MAJOR + Task 5.4 deferred (static-guard blind spot, GameSession.from_dict mutators, superweapon_order_processor decomp) |
| 2026-05-08 | Phase 3: chose Option B (state-bag-via-explicit-processor-parameter) over Option A (registry-restructuring) for `superweapon_order_processor.py` decomp | Per review MAJ-005: Option A is a registry-restructuring project (would pull behavior into the pure-data `SuperweaponSpec` class and force simulation-internal imports into the spec layer). Option B mirrors the pattern Phase 5 already shipped for `battle_setup.py` / `boundary_enforcement.py` / `attack_processor.py`: free functions in a `superweapon_handlers/` package taking the processor as explicit first parameter. Closes the LOC ceiling with no new dependencies and zero behavior change. |
