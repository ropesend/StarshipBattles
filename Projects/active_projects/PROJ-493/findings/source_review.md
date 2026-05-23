# PROJ-493 Source Review

## Source PROJ-479 Deferred List

- **PROJ-479 Phase 3 Task 3.14:**
  `Projects/active_projects/PROJ-479/phase_3_checklist.md:107-111`
  > Replace deep patching of `SuperweaponValidator.find_ship_with_ability` across 10+ tests (lines 131, 166, 201, 622, 669, 708, 748, 909, 1049, 1132) with dependency-injected stub validator at constructor level.

## Codex Planning Consult

- Request: `AgentCoordination/Scratchpad/Consult/20260523T125621Z_plan-PROJ-479-followthrough/request.md`
- Response: `AgentCoordination/Scratchpad/Consult/20260523T125621Z_plan-PROJ-479-followthrough/response.md`
- Relevant findings: Finding 1 (project breakdown), Finding 3 (CAT-6 split), Risks (PROJ-493 sprawl warning)

Key Codex evidence:
- Production class missing seam: `game/strategy/engine/superweapon_order_processor.py:62-79`
- Existing static call: `game/strategy/engine/superweapon_order_processor.py:275-282`
- 16 patch sites in test file (more than the original 10+ noted by PROJ-479):
  `tests/unit/strategy/engine/test_superweapon_order_processor.py:131,166,201,622,669,708,749,786,854,910,1009,1049,1098,1132,1181,1239`
  (Note: PROJ-479's task description listed lines 748, 909 — Codex audit found the current lines are 749, 910 due to file drift.)

## Production Code References (DI Pattern)

- Constructor injection guidance: `docs/02_PATTERNS.md:22,88,106,678`
- Architecture seam definitions: `docs/01_ARCHITECTURE.md:58,175,437-438`
- Existing lazy-default examples (mirror these): `game/strategy/engine/superweapon_order_processor.py:81-94`

## Source PROJ-479 Test Review

`Reviews/results/2026-05-20_210550_test-review/` — original CAT-6 finding identification.
