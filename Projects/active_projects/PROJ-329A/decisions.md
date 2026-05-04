# PROJ-329A: Decisions Log

> Add decisions as they're made. Future agents reference this for "why".

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-04 | Project initialized | Tier 5 of PROJ-321..328 audit consensus plan. User-approved scope (`C:\Users\rossr\.claude\plans\noble-stirring-galaxy.md`) — first of three sequential PROJ-329 batches plus parallel-safe PROJ-330. |
| 2026-05-04 | **D-001:** Apply PROJ-328 Phase A recipe verbatim | Don't re-litigate the pattern. The recipe is proven (6 classes already done) and documented as `docs/02_PATTERNS.md` §33. Per-class commit; characterization-test parity. |
| 2026-05-04 | **D-002:** DesignWorkshopScreen → document deferral, do not refactor | Inventory found it's NOT a UIWindow subclass — uses factory pattern via `app.py`. Audit (PROJ-322 Task 5.10) miscategorized it. Retrofit would need separate factory-pattern project. Document in `docs/known-issues.md`. |
| 2026-05-04 | **D-003:** SettingsWindow → defer until coverage exists | Raw `pygame_gui.elements.UIWindow`, 109 LOC, no tests found. Retrofit value is proportional to existing test coverage; refactoring untested code adds risk without locking behavior. Document in `docs/known-issues.md`; reassess if SettingsWindow gains tests. |
| 2026-05-04 | **D-004:** TDD-first for previously-untested classes | FleetSelectionWindow, PlanetSelectionWindow, MoveChoiceWindow, PlanetTargetEditor have no tests. Write characterization tests against current `__new__` bypass first; verify they pass; then refactor. Per audit consensus discipline. |
| 2026-05-04 | **D-005:** Reuse `UiBuilder[ScreenT]` Protocol from audit S4.5 | New builder pairs (5 in this project) type against `tests/fixtures/ui_builder_protocol.py`. Avoids inventing a new abstraction; pins the contract. |
| 2026-05-04 | **D-006:** Inventory matrix is the canonical artefact | `findings/uiwindow_inventory.md` is the source of truth subsequent projects (329B/C/330) reference. Keep it updated as classes ship. |
| 2026-05-04 | **D-007:** Per-class commit | Each retrofitted class lands in its own commit so bisect/revert is per-class. Inventory + Phase 0 docs land as separate setup commits. |
