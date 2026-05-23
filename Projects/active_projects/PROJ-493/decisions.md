# PROJ-493 Decisions Log

## Decisions

| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-05-23 | Scope to ONLY the SuperweaponValidator seam (Task 3.14) | Codex planning consult: "PROJ-493 will sprawl if it is seeded with speculative 'others'. On current evidence, only 3.14 is a confirmed missing production seam." Other deferred tasks are either test-side mechanical (PROJ-491) or already have the seam (Task 3.32). |
| 2026-05-23 | Use the existing lazy-default pattern (mirror `_get_empire_mutator` / `_get_nav_service`) | `SuperweaponOrderProcessor` already uses this pattern for 2 of its 3 deps (`game/strategy/engine/superweapon_order_processor.py:81-94`). Consistency with existing class style. Avoids forcing all production callers to pass the validator. |
| 2026-05-23 | Do NOT modify `SuperweaponValidator.find_ship_with_ability` signature | If it's currently `@staticmethod`, instance calls still work. Avoid scope creep into validator-class refactor. |
| 2026-05-23 | Extract `StubValidator` to a module-level helper in the test file | Avoids 16 copies. Will not move to a shared fixture unless other test files need it (YAGNI). |
| 2026-05-23 | This project may grow if PROJ-491 Phase 4 routes Task 3.20 second bullet here | Per PROJ-491 phase_4_checklist.md, the `_per_player_ui_state.load(...)` claim is unverified. If investigation confirms a real seam gap, add a Phase 3 here. |

## Reconciliation Notes (My Proposal vs Codex)

My initial proposal had PROJ-493 = "CAT-6 production DI seam introduction (SuperweaponValidator, ActionTimeResolver dispatch, others)". Codex pushed back hard on two points:

1. **ActionTimeResolver doesn't need new DI — seam already exists.** Task 3.32 belongs in PROJ-491 (test rewrite only). Documented in PROJ-491 decisions.md.

2. **Don't pre-seed with "others".** Be specific. Only Task 3.14 has file:line evidence of a missing seam. Speculative "others" expand scope without justification.

I accepted both. PROJ-493 is intentionally narrow: one production class change, ~16 test migrations. If more seams are found later, they get their own project or get added here with explicit evidence.
