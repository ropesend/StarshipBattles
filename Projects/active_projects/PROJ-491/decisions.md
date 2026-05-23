# PROJ-491 Decisions Log

## Decisions

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-23 | Split PROJ-479 deferred CAT-6 across two projects: PROJ-491 (test-side mechanical) and PROJ-493 (production DI seam) | Codex planning consult (20260523T125621Z) found PROJ-479's blanket "requires DI introduction" rationale was overbroad. Only Task 3.14 (SuperweaponValidator) is a confirmed production seam gap; the rest are test-side patterns that consume existing seams (e.g. `bypass_init`, `action_time_resolver`). |
| 2026-05-23 | Include Task 3.32 (ActionExecutionEngine) in PROJ-491, not PROJ-493 | PROJ-479 audit finding F2 + Codex verification: production DI seam already exists at `game/strategy/engine/action_execution_engine.py:55-68`. Only test rewrite of 3 methods needed. |
| 2026-05-23 | Include UI-window/panel migrations (3.6, 3.7, 3.11, 3.13, 3.16, 3.23, 3.25) in PROJ-491, not PROJ-493 | Canonical `bypass_init` fixture exists at `tests/fixtures/ui_widget_factory.py:20-28`. PROJ-458 / PROJ-470 already retrofitted 11 windows. Continuing the retrofit is mechanical test-side work; no production change. |
| 2026-05-23 | Treat Task 3.20 second bullet as INVESTIGATION (Phase 4), not pre-committed test rewrite | The claim that `_per_player_ui_state.load(...)` needs a "public state-restore API" is unverified. If production lacks such an API, this is a real seam gap and belongs in PROJ-493. Decide after looking at the actual class. |
| 2026-05-23 | Phase 1 task ordering by mechanical-pattern similarity, not source-file order | Grouping similar rewrites (behavior assertions, then UI bypass_init, then DI consumption) lets the agent build pattern fluency once and reuse it across tasks. |
| 2026-05-23 | Phase 4 routing: Task 3.20 second bullet → PROJ-493 (production accessor) | Investigation finding: ``PerPlayerUiState`` itself exposes fully public ``save/load/has/discard`` methods, but the manager owns the container behind a private attribute ``_per_player_ui_state``. The tests at lines 1287/1288/1307/1347/1456/1457/1480/1488 read through this private name. The minimal production change is a single ``@property`` on ``StrategyGameStateManager`` exposing the container as ``per_player_ui_state``. That is a production-side change (a small public accessor), so it belongs in PROJ-493 rather than PROJ-491. |

## Permanently Deferred Items (NOT in PROJ-491)

| Item | Why deferred permanently | Required user input |
|------|-------------------------|---------------------|
| PROJ-479 Phase 2 CAT-5 mutation-isolation (Tasks 2.1, 2.2, 2.3, 2.13) | Per Codex verification, these tests genuinely mutate live Ship/Empire/UIManager state; correct fix requires a snapshot/restore helper OR template-rebuild fixture pattern. Neither exists today. Both are architectural decisions about test infrastructure that the user has not approved. | User decides: build a snapshot/restore helper as a new test infrastructure project, or accept the per-test wall-clock cost permanently. |
| PROJ-479 Phase 2 Task 2.9 (test_battle_state_serialization.py) | Phase 2 notes explicitly: "the dataclass-construction cost is negligible; per-test build of a `ComponentState(component_id=...)` is essentially a dict literal." Low-ROI. | None — accepted as no-action. |
| PROJ-479 Phase 4 Task 4.2 sleeps | Codex audit confirmed these sleeps were correctly reclassified as polling micro-yields / absence-assertions. No work needed. | None. |

## Reconciliation Notes (My Proposal vs Codex)

My initial proposal had PROJ-491 = "CAT-6 test-side mechanical (incl Task 3.32)" without distinguishing behavior-rewrites from UI-bypass_init migrations. Codex confirmed this is correct in shape but added two refinements:

1. **Explicitly include UI-window migrations in PROJ-491** — my proposal was ambiguous about whether `bypass_init` migrations belong here or in PROJ-493. Codex's evidence that the seam already exists clarifies they belong in PROJ-491.

2. **Don't pre-seed PROJ-493 with speculative "others"** — my proposal said "PROJ-493 = CAT-6 production DI seam introduction (SuperweaponValidator, ActionTimeResolver dispatch, others)". Codex pushed back that only Task 3.14 is a confirmed seam gap on current evidence. I added Phase 4 (Task 3.20 investigation) to handle the one ambiguous case rather than pre-committing.

## Potential Future Project: CAT-5 Fixture-Bloat (Tractable Subset)

Per Codex's analysis, PROJ-479 Phase 2 has a tractable subset that doesn't need snapshot/restore — items 2.7, 2.11, 2.12, 2.15, 2.16, 2.17 are ordinary fixture-cascade / shared-ui_manager / scope-alignment work (`Projects/active_projects/PROJ-479/phase_2_checklist.md:63-64,91-92,98-99,119-133`). Not in PROJ-491/492/493 due to ID budget. Candidate for a future PROJ-XXX after these three close.

**Tracked via DI-2026-05-23-006** (logged 2026-05-23 from PROJ-491/492/493 scaffolding pass) so the backlog persists after PROJ-491/492/493 close. Per audit Finding 5, narrative-only mention is insufficient — the DI entry ensures triage will surface this when /claude-di-triage runs.
