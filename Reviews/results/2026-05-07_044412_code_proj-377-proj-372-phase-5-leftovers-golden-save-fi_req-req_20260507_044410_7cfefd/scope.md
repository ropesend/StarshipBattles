# Review Scope: PROJ-377 PROJ-372 Phase 5 Leftovers
**Type:** code (delegated by Claude Code)
**Request ID:** req_20260507_044410_7cfefd
**Scope:** Commits on branch feat/03c-phase-aware-execution:
- 3b8370f7a PROJ-377 phase 1: golden-save JSON fixtures
- 83a31662f PROJ-377 phase 2: migrate 5 pathfinding-shim Class A sites
- 9cb543f4c PROJ-377 phase 3: AST shim-scope guard + revert site #3

Files reviewed:
- tests/fixtures/saves/_capture_baseline.py (NEW)
- tests/fixtures/saves/galaxy_proj372_baseline.json (NEW)
- tests/fixtures/saves/galaxy_proj372_populated.json (NEW)
- tests/integration/strategy/test_save_round_trip.py (modified)
- game/ui/screens/strategy_screen.py (modified)
- game/ui/screens/strategy_colonization.py (modified)
- game/strategy/engine/superweapon_order_processor.py (reverted — net unchanged)
- tests/unit/strategy/data/test_pathfinding_shim_scope.py (NEW)
- game/strategy/data/pathfinding.py (docstring rewrite)
- Projects/active_projects/PROJ-377/{plan,decisions,design}.md
- Projects/active_projects/PROJ-372/decisions.md (cross-link)

**Instructions:** Review PROJ-377 against design.md. Focus on 8 areas: golden-fixture correctness, capture-script idempotence, Phase 2 migrations, Site #3 revert, AST guard scope, plan-vs-implementation drift, test-patch transparency, PROJ-372 cross-link consistency.

**Context:** PROJ-377 closes PROJ-372 review MAJ-001 (golden-save fixture) and MIN-002 (pathfinding shim sweep — partial). Final migration count: 4 of 14; surviving shim pinned by AST guard.
