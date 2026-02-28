# PROJ-110: Decisions Log

> **LOG ALL DECISIONS HERE**
> When you make a design choice or the user specifies a preference, add it to this table.
> Future agents will reference this to understand why things were done a certain way.

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-02-11 | Project initialized | Starting point for Test Coverage - Core Systems |
| 2026-02-11 | 4 phases: Foundation, Simulation, Strategy, Minor | Layer-based organization matches dependency order. Foundation first since Simulation/Strategy depend on it. MINOR findings grouped in Phase 4 since they are low-risk edge cases. |
| 2026-02-11 | CRITICAL + MAJOR in phases 1-3, MINOR in phase 4 | CRITICAL/MAJOR findings represent real coverage gaps. MINOR findings are edge case expansions of already-tested code - lower priority. |
| 2026-02-11 | Pure function testing preferred over integration mocks | Many modules (hex_math, modifier_schema, physics) are pure functions. Testing with real inputs is simpler, faster, and more reliable than mock-heavy approaches. |
| 2026-02-11 | Move hex_math integration tests to unit test file | `test_hex_math_strategy.py` tests are really unit tests placed in integration dir. New `tests/unit/core/test_hex_math.py` should be the canonical location. |
| 2026-02-11 | Mock controller interface for behavior tests | All AI behaviors interact through `self.controller.ship.*` and `self.controller.navigate_to()`. Mock these interfaces rather than creating real Ship objects. |
| 2026-02-11 | Seeded RNG for all stochastic tests | Star generation, placement strategies, research service all use randomness. Tests should inject `random.Random(seed)` for deterministic verification. |
| 2026-02-11 | Test file per source module (1:1 mapping) | Each untested source file gets its own test file. Naming: `test_{source_module_name}.py`. Avoids "grab bag" test files. |
| 2026-02-11 | Facade tests use Mock session, not real GameSession | StrategySessionFacade is a thin delegation layer. Mock the session to test facade logic in isolation without needing full game setup. |
| 2026-02-11 | Skip TCG-STR-006 if test_engine_interfaces.py is sufficient | Need to verify existing coverage before adding duplicate tests. |
| 2026-02-11 | Screenshot manager tests mock pygame entirely | ScreenshotManager depends on pygame.display, pygame.image, Tkinter, subprocess. All must be mocked. Tests focus on control flow, not pixel output. |
