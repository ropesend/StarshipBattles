# Phase 4: Strategic — Pattern doc-adds

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-382 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Promote two undocumented but recurring patterns into `docs/02_PATTERNS.md`: the Re-Export Shim migration pattern (4+ confirmed sites) and the Strategy Config Singleton Accessor variant (a third config flavor that coexists with `@lru_cache` and `DEFAULT_*` dict patterns under Pattern #12).

---

## Tasks

### Task 4.1: Document the Re-Export Shim Pattern in `docs/02_PATTERNS.md`
**File:** `docs/02_PATTERNS.md`
**Pattern:** New entry (post-#35 or inline as a Pattern #12 sibling — design choice during Phase 4)
**Tests:** N/A (doc-only)

- [x] Add a new pattern entry titled "Re-Export Shim" after the current Pattern #35 (or wherever the doc structure best accommodates a migration-pattern category).
- [x] Cite the four confirmed sites:
  - `game/ui/screens/race_setup_screen.py` (31 LOC) — re-exports `RaceSetupScreen`, `RaceRandomizer`, `RaceBrowserDialog` from `game.ui.screens.race_setup/`.
  - `game/ui/screens/test_lab/test_run_details.py` (12 LOC) — re-exports `TestRunDetailsPanel` from `game.ui.screens.test_lab.details`.
  - `game/simulation/components/component.py:395-405` — re-exports from `component_loader.py`.
  - `game/strategy/engine/command_handlers.py` — re-export shim for `CommandHandlerRegistry` from `handlers/base.py`.
- [x] Document the pattern: thin module preserving a historical import path while the canonical implementation lives elsewhere; a temporary scaffold tied to a tracked decomposition project; should be removed when all consumers migrate.
- [x] Add `> **Last verified:**` blockquote with today's date per the doc convention enforced by PROJ-307.

### Task 4.2: Document the Strategy Config Singleton Accessor variant under Pattern #12
**File:** `docs/02_PATTERNS.md`
**Pattern:** #12 (Configuration Classes)
**Tests:** N/A (doc-only)

- [x] Find the Pattern #12 entry. Add a new subsection or table row covering the `_default = None` + `get_default_*()` / `set_default_*()` accessor pattern as a third valid config-class flavor (alongside the existing `@lru_cache` and `DEFAULT_*` dict patterns).
- [x] Cite `game/strategy/config/economy_config.py:136-149` as the canonical example. Quote the in-file justification: "Chose this over `@lru_cache` (as used by `ClassificationConfig`) because CLAUDE.md's module-accessor form gives tests a clean swap API without poking `.cache_clear()`."
- [x] Note: only one site uses this variant today, but the audit treats it as a third valid pattern worth documenting so future authors can pick it intentionally rather than reinvent it. The user has approved the doc-add despite the <3-site bar, since the variant has explicit in-code justification.
- [x] Update the `> **Last verified:**` timestamp.

### Task 4.3: Phase verification
**File:** N/A
**Pattern:** doc-add only
**Tests:** N/A

- [x] Both new doc entries render correctly under the doc convention.
- [x] `> **Last verified:**` blockquote present on every changed pattern entry.
- [x] Re-run `Tools/pattern_audit/pattern_audit.py` (if present) — the Re-Export Shim and Strategy Config Singleton sites no longer flag as undocumented patterns.

---

## Phase Completion Checklist
When all tasks above are done:
- [x] All task checkboxes above are checked
- [x] Update status at top of this file to `Complete`
- [x] Update plan.md phase table row to `Complete`
- [x] Update plan.md Current State to point to next phase

_Source audit: `Reviews/results/2026-05-07_220452_pattern-audit/`. See `findings/source_audit.md` for the link._
