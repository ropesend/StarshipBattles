# PROJ-318: PROJ-314 Closeout Remediations

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-318` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-318 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status

| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. R1 — Audit-gate hygiene | Complete | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. R6 — Architecture docs service-count fix | Complete | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. R3 — Delete legacy `<Class>_Portrait.jpg` helper | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |
| 4. R5 — `Tools/regenerate_ship_portraits/` conventions | Not Started | [phase_4_checklist.md](phase_4_checklist.md) |
| 5. R2 — Make audit + smoke test a real release gate | Not Started | [phase_5_checklist.md](phase_5_checklist.md) |
| 6. R4 — Migrate codex-ship-theme-creator skill to new schema | Not Started | [phase_6_checklist.md](phase_6_checklist.md) |

## Current State

**Last Updated:** 2026-04-28
**Active Phase:** Phase 3 — R3 delete legacy `<Class>_Portrait.jpg` helper
**Last Action:** Phase 2 complete. Stale service-count docs now say `ApplicationContext` manages 10 services, `ImageProvider` is documented, and the full sharded suite passed 15998/15998.
**Next Action:** Phase 3 audits and removes remaining legacy portrait helper functions and migrates production callers to `ShipThemeManager`.
**Blockers:** None
**Test baseline at plan time:** 15959 / 15959 passing (post-PROJ-314 baseline).

## Overview

PROJ-314 (Unify Ship Theme Loader Schema) shipped six commits to main
and was marked Complete in its plan. A subsequent independent audit
identified 8 closeout claims, 6 of which were verified or partially
verified by parallel verification agents. This project addresses
those 6 findings as a focused cleanup so PROJ-314 can be considered
genuinely complete.

**Scope is deliberately narrow:** no new features, no schema changes,
no AI image generation. Each phase resolves one of the 6 verified
findings and lands as one commit so each is reviewable independently.

The 8 audit claims and their verdicts:

| # | Claim | Severity | Verdict |
|---|-------|----------|---------|
| A | `validate_audit_ready.py PROJ-314` exits 1 with 8 errors | P1 | **VERIFIED** → Phase 1 (R1) |
| B | `audit.py` exits 0 despite 144 size mismatches; Aetherwake reported CLEAN | P2 | **VERIFIED** → Phase 5 (R2) |
| C | UI smoke test allows fallback as a pass condition | P1 | **PARTIAL** (literal text wrong; substantive concern valid) → Phase 5 (R2) |
| D | Legacy `<Class>_Portrait.jpg` helper still pinned with tests | P2 | **VERIFIED** → Phase 3 (R3) |
| E | Theme-creator skill scaffold + validator still write/expect legacy `images:` schema | P2 | **PARTIAL → mostly VERIFIED** (`theme_common.py` was updated; `create_manifest.py` + `validate_theme.py` were not) → Phase 6 (R4) |
| F | New tool missing README, missing from catalog, top-level `game.*` imports | P2 | **VERIFIED** → Phase 4 (R5) |
| G | Architecture docs still say "9 services" (actual is 10) | P2 | **VERIFIED** → Phase 2 (R6) |
| H | Edit-API default likely fails (`gpt-image-2` not edits-capable) | P2 | **REFUTED** — OpenAI docs confirm `gpt-image-2` supports both `/v1/images/generations` and `/v1/images/edits`. No remediation needed. |

## Goals

1. Restore audit-gate honesty: `validate_audit_ready.py PROJ-314`
   exits 0 (i.e. all 6 phase checklists exist with all-checked
   boxes and `Status: Complete`).
2. Update the 3 stale architecture docs to reflect 10 services and
   the new `ImageProvider`.
3. Eradicate the legacy `<Class>_Portrait.jpg` helper per Rule 3
   (System Migration Policy forbids backward-compat shims after a
   migration). Includes the dependent tests.
4. Bring `Tools/regenerate_ship_portraits/` up to project tool
   conventions: README, catalog entry, project-root bootstrap so it
   runs both ways (`python -m` and `python Tools/...`).
5. Make `audit.py` a real release gate: it must exit non-zero on
   any size mismatch or missing portrait, and it must report
   per-theme even when no portrait keys exist.
6. Migrate the codex-ship-theme-creator skill (`create_manifest.py`
   + `validate_theme.py`) to emit and expect the new `assets:`
   schema, so future themes don't recreate the schema drift.

## Scope

**In:**
- `Projects/active_projects/PROJ-314/phase_1_checklist.md` —
  retroactive box-checking + status update.
- `Projects/active_projects/PROJ-314/phase_{2,3,4,5,6}_checklist.md`
  — 5 new files documenting what each PROJ-314 commit accomplished.
- `docs/02_PATTERNS.md`, `docs/README.md`, `AGENTS.md` — service
  count update.
- `game/ui/utils/portraits.py` — delete `get_portrait_filename()` +
  any legacy `<Class>_Portrait.jpg` fallback in
  `get_portrait_search_paths()`.
- `tests/unit/ui/utils/test_portraits.py` — delete
  `TestGetPortraitFilename` (3 tests).
- `Tools/regenerate_ship_portraits/README.md` (NEW).
- `Tools/regenerate_ship_portraits/cli.py`,
  `Tools/regenerate_ship_portraits/audit.py` — add project-root
  bootstrap.
- `Tools/README.md` — add catalog entry.
- `tests/integration/ui/test_race_setup_ships_smoke.py` — add
  dimension assertion + fallback discrimination + explicit
  allowlist for known gaps.
- `Tools/regenerate_ship_portraits/audit.py` — flag missing
  portraits and exit non-zero on findings.
- `tests/unit/tools/test_regenerate_ship_portraits.py` — extend
  for new audit behaviour.
- `.agents/skills/codex-ship-theme-creator/scripts/create_manifest.py`
  — emit new `assets:` schema.
- `.agents/skills/codex-ship-theme-creator/scripts/validate_theme.py`
  — expect new `assets:` schema, 2048×2048 PNG.

**Out:**
- AI portrait generation for the 20 missing portraits (Aetherwake +
  Atlantians Light Cruiser). User runs the CLI with their
  `OPENAI_API_KEY`. The new audit gate will surface remaining gaps
  but won't fix them.
- Re-encoding the 144 size-mismatched portraits (Voidforged 1024,
  Thoraliens 640). The new audit gate will fail on these; user
  decides whether to regenerate or accept.
- Touching Claim H (edit-API model default) — refuted by OpenAI
  docs.
- Any new functionality. Pure cleanup.

## Key Files

| Component | File Path | Phase |
|-----------|-----------|-------|
| PROJ-314 plan to align with | [Projects/active_projects/PROJ-314/plan.md](../PROJ-314/plan.md) | 1 |
| PROJ-314 phase 1 checklist (retro-check) | [Projects/active_projects/PROJ-314/phase_1_checklist.md](../PROJ-314/phase_1_checklist.md) | 1 |
| PROJ-314 phase 2-6 checklists (NEW) | `Projects/active_projects/PROJ-314/phase_{2,3,4,5,6}_checklist.md` | 1 |
| Validation script | [Projects/scripts/validate_audit_ready.py](../../scripts/validate_audit_ready.py) | 1 |
| Architecture pattern docs | [docs/02_PATTERNS.md](../../../docs/02_PATTERNS.md) | 2 |
| Docs index | [docs/README.md](../../../docs/README.md) | 2 |
| Agent guidance | [AGENTS.md](../../../AGENTS.md) | 2 |
| Legacy helper | [game/ui/utils/portraits.py](../../../game/ui/utils/portraits.py) | 3 |
| Helper tests | `tests/unit/ui/utils/test_portraits.py` | 3 |
| Production callers | [game/ui/panels/build_queue_portraits.py](../../../game/ui/panels/build_queue_portraits.py), [game/ui/panels/design_report_panel.py](../../../game/ui/panels/design_report_panel.py) | 3 |
| Tool README (NEW) | `Tools/regenerate_ship_portraits/README.md` | 4 |
| Tool catalog | [Tools/README.md](../../../Tools/README.md) | 4 |
| Tool entry points | [Tools/regenerate_ship_portraits/cli.py](../../../Tools/regenerate_ship_portraits/cli.py), [Tools/regenerate_ship_portraits/audit.py](../../../Tools/regenerate_ship_portraits/audit.py) | 4, 5 |
| Bootstrap precedent | `Tools/process_components/check_orphans.py:8-19` | 4 |
| Smoke test | [tests/integration/ui/test_race_setup_ships_smoke.py](../../../tests/integration/ui/test_race_setup_ships_smoke.py) | 5 |
| Audit tests | `tests/unit/tools/test_regenerate_ship_portraits.py` | 5 |
| Skill scaffolder | [.agents/skills/codex-ship-theme-creator/scripts/create_manifest.py](../../../.agents/skills/codex-ship-theme-creator/scripts/create_manifest.py) | 6 |
| Skill validator | [.agents/skills/codex-ship-theme-creator/scripts/validate_theme.py](../../../.agents/skills/codex-ship-theme-creator/scripts/validate_theme.py) | 6 |
| Skill schema reference (already updated) | [.agents/skills/codex-ship-theme-creator/scripts/theme_common.py](../../../.agents/skills/codex-ship-theme-creator/scripts/theme_common.py) | 6 (read-only) |
| Theme.json shape reference | [assets/ShipThemes/Federation/theme.json](../../../assets/ShipThemes/Federation/theme.json) | 6 (read-only) |
| Verification findings (this project's basis) | [design.md](design.md) | All |

## Decisions Snapshot

See [decisions.md](decisions.md) for the full log. Locked decisions:

| Decision | Choice |
|---|---|
| Sequencing | R1 (audit gate) → R6 (docs) → R3 (legacy helper) → R5 (tool conventions) → R2 (real gates) → R4 (skill migration). Quick wins first. |
| Phase commit style | One commit per phase; each phase is independently reviewable. |
| Audit-gate fix approach | Approach A1b: create the 5 missing checklist files retroactively, set Phase 1 status to `Complete`, check all 34 boxes. Lighter than re-running full TDD per task. |
| Smoke-test allowlist | Hard-coded constant `EXPECTED_PORTRAIT_GAPS = {("Aetherwake", "*"), ("Atlantians", "Light Cruiser")}` — known gaps the user will fill via the regenerator CLI. Explicit, easy to shrink. |
| Audit script exit codes | `0` = no findings, `2` = size mismatches, `3` = missing portraits, `1` = unexpected error (script crash). User can decide which to gate CI on. |
| Out-of-scope | Generating the 20 missing portraits (requires user's `OPENAI_API_KEY`); re-encoding 144 size-mismatched portraits. Audit will surface them; user fixes. |
| Claim H | Refuted; no remediation. Documented in this project's design.md and decisions.md so future agents don't relitigate it. |

## Top Risks

1. **Removing the legacy helper breaks an unfound caller.** Phase 3
   greps for callers of `get_portrait_filename` and
   `get_portrait_search_paths` then deletes both function and
   tests. Mitigation: run the targeted UI test suite before the
   phase commit; spot-check Race Setup → Ships, Build Queue panel,
   and Workshop's Design Report panel manually after.
2. **Tightening the smoke test exposes more pre-existing gaps than
   expected.** Phase 5 may surface failures beyond the 144 known
   size mismatches and 20 missing portraits. If so, expand the
   allowlist to keep the test green; document each new entry in
   `decisions.md`. Genuine bugs get filed separately.
3. **Skill scaffolder migration could break theme creation
   end-to-end.** Phase 6 produces a fake theme via the migrated
   `create_manifest.py` and walks it through `validate_theme.py` +
   `ShipThemeManager.discover_themes()` as smoke. If the round trip
   fails, the phase doesn't ship until it passes.

## Verification

End-to-end: after all 6 phases land,
```bash
python Projects/scripts/validate_audit_ready.py PROJ-314    # → exit 0
python -m Tools.regenerate_ship_portraits.audit               # → exit 2 or 3 (still has known gaps), exits non-zero
python Tools/test_sharded/test_sharded.py                     # → 15959 + delta passing, 0 failures
pytest tests/integration/ui/test_race_setup_ships_smoke.py    # → passes WITH dimension/fallback assertions enforced
```

`docs/02_PATTERNS.md`, `docs/README.md`, `AGENTS.md` mention 10
services and `ImageProvider`.

`Tools/regenerate_ship_portraits/cli.py --help` runs without
manual `cd` to repo root.

`grep -r "get_portrait_filename\|_Portrait\.jpg" game/ tests/` →
no matches in `game/`; no matches in `tests/` except in the
audit-script `last_run.json` paths if any.

`.agents/skills/codex-ship-theme-creator/scripts/create_manifest.py`
generates `theme.json` files that pass `ShipThemeManager`
discovery.

## Related Documents

- [design.md](design.md) — Verification findings (8 claims with
  verdicts and supporting evidence) that motivated each phase.
- [decisions.md](decisions.md) — Full decisions log.
- [manifest.md](manifest.md) — File manifest for parallel execution.
