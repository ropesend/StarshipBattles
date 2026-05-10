# Findings: Documentation Consistency

## FND-DOC-001 [MAJ]: PROJ-372 decisions.md cross-link has 5→4 migration count drift (also FND-MIG-003)

See `findings/phase2_migration_review.md` FND-MIG-003 for full analysis. Briefly: PROJ-372 decisions.md row 38 says "5 of 14" migrations including superweapon_order_processor, but the actual count is 4 of 14 (superweapon_order_processor reverted).

## FND-DOC-002 [MIN]: PROJ-372 decisions.md deferred-site listing omits superweapon_order_processor

The PROJ-372 decisions.md row 38 lists deferred Class B sites as: `game_session`, `handlers/base`, `fleet_navigation_service`, `strategy_superweapons`, `planet_slice`. But the deferred set also includes `superweapon_order_processor` (site #3, reverted). The listing of 8 deferred sites should include it.

## FND-DOC-003 [INFO]: plan.md and PROJ-377 decisions.md are internally consistent

PROJ-377's own `plan.md` (line 25: "4 of 14") and `decisions.md` (row 2026-05-07: "4 sites (#10, #11, #12, #14)") agree on the migration count. The `pathfinding.py` docstring correctly references "PROJ-377 decisions.md" for the deferred-site set.

## FND-DOC-004 [INFO]: pathfinding.py docstring rewrite is accurate

The rewritten docstring (lines 1-17) correctly:
- Explains the shim's role as "permanent test-patch transparency surface"
- References the AST guard at `tests/unit/strategy/data/test_pathfinding_shim_scope.py`
- Explains `_intercept_for` always constructs a fresh calculator (test-patch transparency)
- No longer says "deprecated" or references PROJ-376 (superseded by PROJ-377)

## FND-DOC-005 [MIN]: plan.md Current State says "All phases complete; ready for review" but PROJ-372 decisions.md has the 5→4 drift

The plan states readiness for review, but the cross-project documentation inconsistency (FND-DOC-001) should be resolved before the project is fully closed.
