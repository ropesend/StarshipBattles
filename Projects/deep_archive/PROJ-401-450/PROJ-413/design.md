# PROJ-413: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Source Audit

- **Audit directory:** `Reviews/results/2026-05-13_194106_legacy-audit/`
- **Audit verified items:** 15 total across all sibling projects.
- **This bundle:** 2 verified, 0 uncertain (resolved), 0 INFO (resolved), 0 deferred.
- **Project siblings:** PROJ-414, PROJ-415, PROJ-416, PROJ-417, PROJ-418, PROJ-419, PROJ-420, PROJ-421.
- **Cluster identity:** `stars_galaxy_reexports (PROJ-372 vestige)`.
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
1. **Caller-grep accuracy** — if `grep` misses a caller, the deletion breaks imports at runtime. Mitigation: grep for both `from <module> import` and `from <module>` forms; also search for multiline import blocks (a single-line grep misses `test_stars.py:12-18` which spans multiple lines). Cross-check with `pytest tests/` before deletion. Avoid using a broad `SOLAR_` grep pattern — it overmatches canonical references in `game/core/spectrum_math.py` and `game/strategy/generation/star_generator.py`.
2. **`Star.from_dict` uses `Spectrum` internally** — `stars.py` calls `Spectrum.from_dict` inside `Star.from_dict`. Deleting the top-level `from game.strategy.data.spectrum import Spectrum` re-export without preserving an internal import will break deserialization. The shim retirement strategy must replace the public symbol with a private import (e.g. `from game.strategy.data.spectrum import Spectrum as _Spectrum`) rather than simply removing the import line.
3. **Partial shim removal is not retirement** — removing only `__all__` entries while `__getattr__` or the top-level global still exposes the symbol leaves the legacy import path alive. Per Pattern #36, retirement occurs when the legacy import path has zero remaining call sites under `game/`. Ensure `__all__`, the top-level import, and `__getattr__` entries are all cleaned up together.
4. **Test patches** — `mock.patch(...)` strings targeting the shim module path need rewriting alongside production imports. (No mock.patch strings targeting `game.strategy.data.stars` or `game.strategy.data.galaxy` were found in the current codebase.)
5. **Test asserting re-export behavior** — `tests/unit/strategy/data/test_spectrum.py::test_stars_module_re_exports_spectrum` explicitly asserts `stars.Spectrum is Spectrum`. This test must be deleted or updated as part of Phase 1.
6. **PROJ-376 / PROJ-309 / PROJ-372 history** — coordinate with prior project plans if they still track related work.

### Opportunities Discovered
- The verifier found stars.py's solar constants (`SOLAR_LUMINOSITY_W`, etc.) have **0** callers via the re-export path — they can be deleted from the shim in the same PR with no caller migration.

## Design Decisions
See [decisions.md](decisions.md) for the full log with rationale.
