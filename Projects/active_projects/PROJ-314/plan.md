# PROJ-314: Unify Ship Theme Loader Schema

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-314` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-314 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status

| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Audit lock-in + canonical constants | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. New `game/ui/services/image/` service | Not Started | phase_2_checklist.md (TBD) |
| 3. Loader rewrite | Not Started | phase_3_checklist.md (TBD) |
| 4. Image generation tool + asset prep | Not Started | phase_4_checklist.md (TBD) |
| 5. Atomic schema migration | Not Started | phase_5_checklist.md (TBD) |
| 6. Cleanup + documentation | Not Started | phase_6_checklist.md (TBD) |

## Current State

**Last Updated:** 2026-04-28
**Active Phase:** Planning — awaiting user approval
**Last Action:** Plan finalised after Phase A (foundation docs + 3 review agents + clarifying Qs) and Phase B (7-agent swarm: Architecture, Dependency, Test Impact, Pattern, Risk, Data Flow, API).
**Next Action:** User reviews this plan; on approval, Phase 1 can begin in a new session via the "Continue Project" prompt.
**Blockers:** None
**Test baseline at plan time:** 15893 / 15893 passing (sharded suite, 65.8s wall).

## Overview

The Race Setup → Ships tab renders three different visual states across the
nine ship themes today because the project has drifted between two
`theme.json` schemas plus inconsistent portrait coverage. Federation +
seven others use a flat `images:` schema (skin only); Thoraliens uses a
richer `assets:` schema (skin + portrait per ship); Aetherwake has no
portrait directory at all. The loader at
[`game/ui/assets/ship_theme_manager.py:93`](../../../game/ui/assets/ship_theme_manager.py#L93)
reads only the legacy schema, and portrait paths are hardcoded by a
filename convention that's also duplicated in 4 non-loader sites.

This project unifies everything: one canonical `assets:` schema, one
loader, display-form ship-class keys across all themes, 2048×2048 PNG
art everywhere, AI-generated portraits backfilled where missing
(20 portraits via `gpt-image-2`), and 151 `.jpg`→`.png`
re-encodings. Filenames are normalised to `lowercase_with_underscores.png`
to fix a latent Linux-CI case-sensitivity bug. The project introduces
a new `game/ui/services/image/` service for the image-generation API
and pins the canonical 19-ship-class set in
`game/core/ship_classes.py`.

QA Session 20260428_052952 [05:36–05:37] surfaced the Aetherwake +
Thoraliens symptoms; this is the unified response per user direction.

## Goals

1. Replace legacy `images:` with `assets:` schema across all 9 themes
   (atomic migration, no shim — Rule 3).
2. Make portrait paths data-driven from `theme.json` everywhere; delete
   the hardcoded `<Class>_Portrait.jpg` convention from the loader and
   the 4 sites that duplicate it.
3. Standardise every skin and portrait at **2048×2048 PNG**.
4. Standardise ship-class keys at **display-form** (`"Battleship"`,
   `"Fighter (Medium)"`, etc.) — only Thoraliens needs migration.
5. Normalise filenames to `lowercase_with_underscores.png` across all
   themes (fixes Linux CI case-sensitivity).
6. Backfill missing portraits via `gpt-image-2` through a new
   `game/ui/services/image/` service.
7. Add image-size validation at load (warning, not rejection;
   never silent upscaling).
8. Fix the long-standing inconsistency between `load_image()` (always
   returns Surface) and `get_portrait_image()` (returns
   `Surface | None`) — both now return Surface with synthetic
   fallback.
9. Pin the canonical 19-ship-class set in
   `game/core/ship_classes.py::SHIP_CLASSES_WITH_VISUAL_THEMES` so
   schema validation has a single source of truth.

## Scope

**In:**
- `game/ui/assets/ship_theme_manager.py` rewrite.
- 9 `theme.json` files migrated to the new schema.
- 322+ asset files (171 skins + 151 portraits + 20 new portraits) brought
  to 2048×2048 PNG with normalised filenames.
- New `game/ui/services/image/` service (provider, openai_provider,
  null_provider, factory, defaults, types, background) + tests.
- New `Tools/regenerate_ship_portraits/` CLI + audit script.
- New `game/core/ship_classes.py` constant.
- `Paths.SHIP_THEMES_TARGET_SIZE` constant.
- 4 hardcoded-convention sites updated:
  [`design_image_helper.py:72-74`](../../../game/ui/screens/design_image_helper.py#L72-L74),
  [`builder/right_panel.py:262-263`](../../../game/ui/screens/builder/right_panel.py#L262-L263),
  [`utils/portraits.py:98-114`](../../../game/ui/utils/portraits.py#L98-L114),
  plus the codex-skill at
  [`.agents/skills/codex-ship-theme-creator/scripts/theme_common.py:31`](../../../.agents/skills/codex-ship-theme-creator/scripts/theme_common.py#L31).
- Tests: 9 deleted (private-method tests), ~8 rewritten, ~12 new
  contract tests, 2 integration smoke tests. Net +6.
- Doc updates to `docs/01_ARCHITECTURE.md` and `docs/03_CONVENTIONS.md`.

**Out:**
- Caption sidecar generation (`theme.caption.json`) for new portraits
  — handled separately.
- Adding new ship classes or themes.
- Changing `Race Setup → Ships` UI layout.
- Migrating component / planet / star / flag art systems.
- Moving `ShipThemeManager` from `game/ui/assets/` to `game/assets/`
  (separate follow-up project).

## Key Files

| Component | File Path |
|-----------|-----------|
| Theme loader (rewrite) | `game/ui/assets/ship_theme_manager.py` |
| Canonical ship-class set (NEW) | `game/core/ship_classes.py` |
| Path constants (extend) | `game/core/paths.py` |
| Portrait-convention duplicate site #1 | `game/ui/screens/design_image_helper.py` |
| Portrait-convention duplicate site #2 | `game/ui/screens/builder/right_panel.py` |
| Portrait-convention duplicate site #3 | `game/ui/utils/portraits.py` |
| Portrait-convention duplicate site #4 (external skill) | `.agents/skills/codex-ship-theme-creator/scripts/theme_common.py` |
| New image service | `game/ui/services/image/` (7 files) |
| New regen CLI | `Tools/regenerate_ship_portraits/` |
| Theme JSONs (×9) | `assets/ShipThemes/<Theme>/theme.json` |
| Tests (rewrite) | `tests/unit/ui/test_ship_theme_logic.py`, `tests/unit/ui/test_theme_discovery.py` |
| Tests (NEW) | `tests/unit/ui/services/image/`, `tests/integration/ui/test_race_setup_ships_smoke.py` |
| Triage findings (audit table source) | [findings/ship_themes_unified_schema_migration.md](findings/ship_themes_unified_schema_migration.md) |
| Docs to update | `docs/01_ARCHITECTURE.md`, `docs/03_CONVENTIONS.md` |

## Decisions Log Snapshot

See [decisions.md](decisions.md) for the full log. Locked decisions:

| Decision | Choice |
|---|---|
| Image model | `gpt-image-2` (confirmed via OpenAI developer docs) |
| Naming case | Display-form |
| Image size | 2048×2048 standardised, both skin and portrait |
| Image format | PNG only (per `docs/03_CONVENTIONS.md` §285–288) |
| Filename convention | `lowercase_with_underscores.png` |
| Schema migration | Atomic single commit, no shim |
| Caption sidecars | Out of scope |
| Image service location | `game/ui/services/image/` (UI consumers only) |
| `get_portrait_image` return | `Surface` with fallback (never `None`) |
| `ImageResult.size` | actual returned size; callers validate; never silent upscale |
| Ship-class constant | `game/core/ship_classes.py::SHIP_CLASSES_WITH_VISUAL_THEMES` |
| Test isolation | `NullImageProvider` default in `create_test()` |

## Top Risks

1. **Cross-platform filename case mismatch.** Mixed-case filenames in
   4 themes work on Windows, break on Linux CI. Phase 5 normalises;
   add CI lint as safety net.
2. **Unmocked `ImageProvider` hits real OpenAI API.** `NullImageProvider`
   is the default in tests; fixture asserts no test silently uses the
   real provider.
3. **`gpt-image-2` 2048×2048 might not be natively supported.** Verify
   on first API call in Phase 4. Protocol's "actual size" policy makes
   the failure visible; regenerator decides whether to upscale via PIL
   or accept lower size.

See `findings/ship_themes_unified_schema_migration.md` and the swarm
findings in [design.md](design.md) for full risk discussion.

## Related Documents

- [design.md](design.md) — Architecture analysis, swarm findings, API
  specifications
- [decisions.md](decisions.md) — Full decisions log
- [manifest.md](manifest.md) — File manifest for parallel execution
- [findings/ship_themes_unified_schema_migration.md](findings/ship_themes_unified_schema_migration.md)
  — Original triage doc + per-theme audit table
- [findings/assets/](findings/assets/) — Three QA screenshots showing
  Federation (working baseline), Aetherwake (no portraits), Thoraliens
  (empty placeholders)

## Verification

- [ ] All 6 phase checklists complete
- [ ] All 9 themes render skin + portrait side-by-side in Race Setup → Ships
- [ ] `pytest tests/` — full suite passes (target: 15893 + ~6 = ~15899)
- [ ] All asset files lowercase-with-underscores PNG at 2048×2048
- [ ] `Tools/regenerate_ship_portraits/audit.py` reports zero
      coverage gaps and zero filename-case violations
- [ ] `docs/01_ARCHITECTURE.md` and `docs/03_CONVENTIONS.md` updated
      and `Last verified` bumped
- [ ] User verified end-to-end smoke test
