# PROJ-223: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-03-24 | Project initialized | Starting point for Save/Load Round-Trip Verification Framework |
| 2026-03-24 | Live state comparison harness included in scope | User wants QA sessions to have automated save/load verification |
| 2026-03-24 | Breadth-first approach: cover all 28 types before deepening | Catches widest class of regressions early |
| 2026-03-24 | Tests + light refactoring allowed | Optional @register_serializable decorator and Empire.built_ship_designs ordering fix |
| 2026-03-24 | Tests go in `tests/integration/save_load/test_roundtrip_*.py` | Existing conftest provides fixtures; round-trip is inherently integration-level |
| 2026-03-24 | Deep compare utility in `tests/infrastructure/deep_compare.py` | Follows existing pattern (session_cache.py is there); test infrastructure, not fixture |
| 2026-03-24 | Factory functions in `tests/fixtures/strategy_entities.py` | Follows established create_test_ship() pattern; function-based, not class-based |
| 2026-03-24 | @register_serializable in `game/core/json_utils.py` | Core layer is the right home; backward-compatible, optional decorator |
| 2026-03-24 | BattleState serialization out of scope | Separate concern, already has 1400+ lines of dedicated tests |
| 2026-03-24 | 6 phases: Infrastructure → Leaf → Compound → DI/Refs → Full → Live | Each phase builds on previous; can ship partial value at any phase boundary |
