# PROJ-491 Source Review

## Source PROJ-479 Deferred List

Direct pointers to the deferred tasks this project carries:

- **PROJ-479 Phase 3 NEEDS_REWORK tasks** (test-side subset):
  `Projects/active_projects/PROJ-479/phase_3_checklist.md`
  Tasks 3.1, 3.2, 3.4, 3.5, 3.6, 3.7, 3.9, 3.10, 3.11, 3.12, 3.13, 3.15, 3.16, 3.20 (both bullets), 3.21, 3.22, 3.23, 3.24, 3.25, 3.29, 3.30, 3.31, 3.32, 3.33
- **PROJ-479 audit finding F2** (Task 3.32 wrongly deferred):
  `Projects/active_projects/PROJ-479/findings/audit_verification.md:9`
- **PROJ-479 plan Current State** (Deferred work list):
  `Projects/active_projects/PROJ-479/plan.md:29-35`

## Codex Planning Consult

The project structure (split into PROJ-491 / PROJ-492 / PROJ-493) was decided via a planning consult with Codex:

- Request: `AgentCoordination/Scratchpad/Consult/20260523T125621Z_plan-PROJ-479-followthrough/request.md`
- Response: `AgentCoordination/Scratchpad/Consult/20260523T125621Z_plan-PROJ-479-followthrough/response.md`

Key Codex evidence (file:line citations from response):
- `bypass_init` canonical seam: `tests/fixtures/ui_widget_factory.py:20-28`
- ActionExecutionEngine DI seam (Task 3.32): `game/strategy/engine/action_execution_engine.py:55-68,183-192`
- Test-side patterns in deferred files: `tests/unit/ui/screens/test_orders_window.py:34,51-59`; `tests/unit/ui/screens/test_build_queue_list_window.py:24,38`; `tests/unit/ui/screens/test_empire_build_queue_window.py:72-88`; `tests/unit/ui/test_race_browser_dialog.py:79,107,133,159,173,187,209,234,268,291,316,334,374`

## Related Discovered Issues

- DI-2026-05-23-003 — Task 3.32 was wrongly deferred (production DI seam already exists). This project addresses the test rewrite in Phase 3.

## Source PROJ-479 Test Review

The original third-party test review that PROJ-479 was created from:
`Reviews/results/2026-05-20_210550_test-review/`
