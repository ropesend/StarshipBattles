# PROJ-25: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-01-27 | Project initialized | Starting point for Consolidate Dual AI Implementations |
| 2026-01-27 | Use simulation layer (`controller.py`) as canonical | Modern, refactored, modular, documented, uses ShipControllableAdapter, better test support with reset()/clear() methods |
| 2026-01-27 | Delete `game/ai/core/` entirely after migration | No need for compatibility shim; direct migration is cleaner and reduces maintenance burden |
| 2026-01-27 | Use `StrategyManager.instance().strategies` directly | No magic proxy dict; explicit access pattern is clearer and more maintainable |
| 2026-01-27 | Move root test files to `tests/integration/` | Consistent test organization; `test_formation_attack.py` and `test_formation_flight.py` should be in proper test directory |
| 2026-01-27 | Wait for PROJ-24 completion | Interface migration must complete before legacy code can be removed; PROJ-24 removes the `__getattr__`/`__setattr__` delegation that legacy code relies on |
