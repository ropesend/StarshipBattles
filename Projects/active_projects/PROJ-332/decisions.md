# PROJ-332: Decisions Log

> Add decisions as they're made. Future agents reference this for "why".

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Master plan `AgentCoordination/Scratchpad/plans/test_coverage_master_plan_v1.md` lists `turn_engine.py` (795 LOC, HIGH risk, ~1.5 sessions) as PROJ-332. Reference shape: PROJ-329A. |
| 2026-05-04 | **D-001:** Adopt master-plan characterization discipline | Pin observed behavior. No TDD-first, no production refactors, no architectural fixes for testability blockers. Tests document what the engine does today, not what it should do. |
| 2026-05-04 | **D-002:** Mock at boundaries via `MagicMock(spec=I*Engine)` | All 15 injectable engines have an `I*Engine` Protocol. Use `MagicMock(spec=...)` so signature drift surfaces as test failure. Matches the existing `test_dependency_injection.py` pattern. |
| 2026-05-04 | **D-003:** Reuse existing `conftest.py` fixtures | `tests/unit/strategy/turn_engine/conftest.py` already provides `turn_engine`, `mock_empire`, `mock_galaxy`. New test files use these directly. No parallel fixtures. |
| 2026-05-04 | **D-004:** Locally-constructed engines tested via `patch` at import site | `QualityEngine`, `AtmosphereEngine`, `WaterEngine` (in `process_turn`) and `PlanetModifierEffectEngine` (in `_process_tick`) are `import`ed and constructed inside their methods — they cannot be injected. Use `unittest.mock.patch('game.strategy.engine.turn_engine.QualityEngine')` etc. Documented as observation, not refactored (master-plan rule). |
| 2026-05-04 | **D-005:** Split into 7 focused test files | A single test file pinning all 27 gaps would exceed the 500-LOC ceiling. Split by behavior cluster: init precedence, lazy properties, phase timing, snapshot integration, end-of-turn order, PROJ-320 movement diff, validation. Each file <500 LOC. |
| 2026-05-04 | **D-006:** Per-test-file commit | Each of the 7 new files lands in its own commit. Bisect/revert per behavior cluster. Matches master-plan discipline. |
| 2026-05-04 | **D-007 (observation, NOT a fix):** End-of-turn engines + Phase 1.8 modifier-effects bypass `_time_phase` wrapping | The end-of-turn block (organics → happiness → population → quality → atmosphere → water) and Phase 1.8 (PlanetModifierEffectEngine in `_process_tick`) call engines outside `_time_phase`. Failures will not become `EnginePhaseError`, will not appear in the perf-log timing dict, and will not trigger snapshot rollback. **Pin as-observed.** Recorded here for separate ticket triage. |
| 2026-05-04 | **D-008 (observation):** Snapshot capture failure is silently swallowed | `process_turn` lines ~522–524 wrap snapshot capture in a broad `except Exception`, log an error, and continue with `snapshot=None` so the turn still runs without rollback capability. Pin this as-observed; do not propose making it fail-fast. |
| 2026-05-04 | **D-009:** Existing `test_turn_engine_config.py` is out of scope | That file covers the `TurnEngineConfig` frozen dataclass, not `TurnEngine` itself. Inventoried in `manifest.md` for completeness; no new tests planned for it under PROJ-332. |
| 2026-05-04 | **D-010:** One phase only — no `phase_0` | All work is characterization. PROJ-329A's multi-phase shape (phase_0..phase_3) does not apply; a single `phase_1_checklist.md` covers the project. |
