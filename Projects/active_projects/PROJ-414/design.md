# PROJ-414: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

- **Audit directory:** `Reviews/results/2026-05-13_194106_legacy-audit/`
- **Audit verified items:** 15 total across all sibling projects.
- **This bundle:** 1 verified, 0 uncertain (resolved), 0 INFO (resolved), 0 deferred.
- **Project siblings:** PROJ-413, PROJ-415, PROJ-416, PROJ-417, PROJ-418, PROJ-419, PROJ-420, PROJ-421.
- **Cluster identity:** `pathfinding_shim (PROJ-376)`.
- **Severity breakdown:** 1× MAJOR.

## Initial Analysis

The 2026-05-13 legacy audit ran a 4-shard scan over 776 production files in
`game/` (~165k LOC) and found 21 candidate items: 0 CRITICAL, 3 MAJOR, 11
MINOR, 7 INFO. No save-migration code, no module aliases, no genuine duplicate
systems. The codebase posture was assessed as "Clean / light drift."

A third-pass skeptical verification by this skill confirmed 15 items as
VERIFIED (zero REJECTED, one UNCERTAIN that was user-included), and flagged
the audit's only fabricated claim (LEG-02-001's "8 non-modal slots") which
the user chose to reframe rather than drop.

## Swarm Findings Summary

Combined analysis from `findings/verification_report.md`.

### Architecture
- Re-export shims in this codebase follow Pattern #36 (`docs/02_PATTERNS.md`),
  with documented migration intent. Removing them is mechanical caller migration
  followed by a single-PR shim deletion.
- Pattern #31 (`StrategyModalWindow`) supersedes the older Pattern #30
  (Registrar Close-Callback) and is the canonical modal-window cleanup mechanism.

### Key Patterns to Reuse
- **Pattern #36 (Re-Export Shim):** `docs/02_PATTERNS.md` — describes the canonical migration sweep used by PROJ-372 / PROJ-376.
- **Pattern #31 (StrategyModalWindow):** `game/ui/screens/strategy_modal_window.py:148-170` — `kill()` auto-deregisters via `wm.unregister_modal(self)`.

### Dependencies & Risks
1. **Caller-grep accuracy** — if `grep` misses a caller, the deletion breaks imports at runtime. Mitigation: grep for both `from <module> import` and `from <module>` forms; cross-check with `pytest tests/` before deletion. Fresh grep (2026-05-14) found 22 import statements across 18 distinct files (11 production / 11 test), not a simple "19" count — produce the definitive list in Phase 1a before implementing.
2. **Test patches (~30 sites)** — `mock.patch(...)` strings targeting `game.strategy.data.pathfinding.X` must be rewritten. There are approximately 30 such sites across 9 test files. Each patch target must move to the name actually looked up by the migrated production code — not to a single service class. Additionally, SUT-local patches (e.g. `patch('game.strategy.engine.superweapon_order_processor.get_system_at_hex')`) may need updating depending on how callers are migrated (PROJ-377 documented this blind spot). Do NOT add a new forwarding layer in any service — that recreates the shim under a different name.
3. **Guard test must be deleted** — `tests/unit/strategy/data/test_pathfinding_shim_scope.py` is an AST-based guard that pins the shim's function set and explicitly states the shim is "no longer slated for deletion." This guard test must be deleted (not updated) as part of the deletion PR. Attempting to delete `pathfinding.py` without deleting this guard test first will cause an immediate test failure.
4. **`intercept_calculator.py` shim routing is intentional** — Lines 121 and 169 of `game/strategy/services/intercept_calculator.py` deliberately import the shim (`from game.strategy.data import pathfinding as _pf_shim`) to route through it for test-patch transparency. Migrating these two lines away from the shim changes the test isolation semantics for all intercept tests. The correct new patch targets after migration depend on the exact code path; they are likely `game.strategy.services.intercept_calculator.project_fleet_path` and `GalaxyPathfindingService.find_hybrid_path`. Plan Phase 1a must enumerate and confirm these.
5. **PROJ-376 / PROJ-309 / PROJ-372 / PROJ-377 history** — PROJ-377 explicitly decided not to delete the shim; PROJ-414 must re-evaluate and supersede that decision. The PROJ-377 `decisions.md` and the guard test are the live authoritative record of what was deferred and why.

### Opportunities Discovered
- The verifier found stars.py's solar constants (`SOLAR_LUMINOSITY_W`, etc.) have **0** callers via the re-export path — they can be deleted from the shim in the same PR with no caller migration.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
