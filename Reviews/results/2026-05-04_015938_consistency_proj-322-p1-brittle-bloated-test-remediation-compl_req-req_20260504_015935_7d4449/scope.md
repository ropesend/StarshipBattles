# Review Scope: PROJ-322 P1 brittle/bloated test remediation — completion + continuation review
**Type:** consistency (delegated by Claude Code)
**Request ID:** req_20260504_015935_7d4449
**Scope:**
- PROJ-322 plan, design, decisions, manifest, all 6 phase checklists
- PROJ-322 findings (verification_report.md, source_review.md)
- docs/known-issues.md (UIWindow + LLM-thread blockers)
- tests/fixtures/ui_widget_factory.py + test
- tests/fixtures/cargo_mock_ship.py, yard_facility.py, mock_planet.py
- tests/unit/simulation/conftest.py (HLP-002)
- game/services/llm/background.py (LLMBackgroundCall thread blocker)
- game/ui/screens/race_setup/screen.py (RaceSetupScreen, lone non-UIWindow APC-001 deferral)
- tests/unit/ui/screens/test_fleet_report_window.py (UIWindow blocker site)
- tests/unit/services/llm/test_background.py (Task 4.3 deferred site)
- Reviews/results/2026-05-02_204633_test-review/SUMMARY.md (source candidates)
- tests/integration/ui/build_queue_screen/conftest.py (option-c precedent)
**Instructions:**
1. Are 25 deferrals genuinely blocked?
2. UIWindow unblocking path recommendation (a/b/c)
3. LLMBackgroundCall thread refactor analysis
4. Quality spot-check of completed work
5. make_ui_widget factory evaluation
6. Phase 6 shared-fixture decisions (DUP-001 + HLP-001)
7. Continuation work recommendations
**Context:** Part of 3-project chain review (PROJ-321/322/323). 322 completion review is highest-value.
