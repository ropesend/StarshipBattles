# PROJ-416: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

- **Audit directory:** `Reviews/results/2026-05-13_194106_legacy-audit/`
- **Audit verified items:** 15 total across all sibling projects.
- **This bundle:** 2 verified, 0 uncertain (resolved), 0 INFO (resolved), 0 deferred.
- **Project siblings:** PROJ-413, PROJ-414, PROJ-415, PROJ-417, PROJ-418, PROJ-419, PROJ-420, PROJ-421.
- **Cluster identity:** `proj309_vestige`.
- **Severity breakdown:** 2× MINOR.

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
1. **Caller-grep accuracy** — if `grep` misses a caller, the deletion breaks imports at runtime. Mitigation: grep for both `from <module> import` and `sys.modules` injection forms; cross-check with `pytest tests/` before deletion.
2. **Test patches** — `mock.patch(...)` strings AND `sys.modules` injections targeting the shim module path need rewriting alongside production imports. The `sys.modules` injection in `tests/unit/test_screen_router.py:283-287` is in scope even though it uses a different mechanism.
3. **Shim contract test deletion** — `tests/unit/ui/screens/test_race_setup_screen_public_api.py` is a sentinel for the shim's contract. It must be deleted, not migrated; migrating it would produce redundant smoke tests.
4. **Phase 2 production scope** — `Game.running` is not confined to `__init__`. Three production write/read sites exist: `_request_shutdown()` (line ~266), `_handle_strategy_action("quit_game")` (line ~452), and `run()` (lines ~502-507 bridge). All must be removed; the plan originally only identified the `__init__` declaration.
5. **PROJ-376 / PROJ-309 / PROJ-372 history** — coordinate with prior project plans if they still track related work.
6. **Stale `app.py:522` claim** — Shard 04 claimed `game/app.py` imports `RaceSetupScreen` from the shim; this is false. The shim's own docstring contains a stale `app.py:522` reference. The actual production importers are `screen_router.py` and `new_game_setup_controller.py`. Callers confirmed by grep; 2 production callers is correct.
7. **Docs/comments cleanup** — `docs/02_PATTERNS.md` lists the shim as current; `race_setup/__init__.py` and `race_setup/screen.py` contain docstrings pointing to the shim as still-valid. All must be updated in Phase 1.

### Opportunities Discovered
- The verifier found stars.py's solar constants (`SOLAR_LUMINOSITY_W`, etc.) have **0** callers via the re-export path — they can be deleted from the shim in the same PR with no caller migration.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
