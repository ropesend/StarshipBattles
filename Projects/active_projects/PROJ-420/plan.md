# PROJ-420: Legacy removal — lazy-init registry cache consolidation (2026-05-13)

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-420` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-420 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Introduce shared registries-cache helper and migrate 3 modules | Complete | [phase_1_checklist.md](phase_1_checklist.md) |

## Current State
**Last Updated:** 2026-05-13
**Active Phase:** Phase 1 (Complete)
**Last Action:** All Phase 1 tasks implemented and committed. Helper `game/core/registry_cache.py` introduced; 4 UI modules migrated (3 lazy-cache consolidations + 1 dead-code deletion); cache invalidation wired into `set_default_registry_manager`, `clear_registry`, and `conftest.py`'s `reset_game_state`. New tests in `tests/unit/core/test_registry_cache.py` (7 passing). All targeted tests green; full `pytest tests/ --testmon` showed only an unrelated `QS Battleship` metadata failure (20313 passed, 1 unrelated fail).
**Next Action:** Audit ready
**Blockers:** None

## Overview
Consolidates 3 duplicate `global`-keyword lazy-init caches (`_cached_registries` × 2, `_ship_factory` × 1) into a single shared helper. Two unrelated caches in the audit list (production-rates JSON load, portrait thumbnails, replay-store pointer) are confirmed distinct and excluded.

Source: legacy audit `2026-05-13_194106_legacy-audit`, verified items in this bundle = 1.
Removal cluster: `lazy_cache_consolidation`.

### Notable callouts
_(no special callouts)_

## Goals
- Introduce shared registries-cache helper and migrate 3 modules

## Scope
**In:** removal cluster `lazy_cache_consolidation` — items LEG-02-004.
**Out:** other clusters' contents (siblings: PROJ-413, PROJ-414, PROJ-415, PROJ-416, PROJ-417, PROJ-418, PROJ-419, PROJ-421); REJECTED and OUT_OF_SCOPE findings (none in this run; see `findings/verification_report.md`).

## Key Files
| File | Type | Action | Notes |
|------|------|--------|-------|
| `game/core/registry_cache.py` | Production | Edit | New shared helper for lazy GameRegistries cache |
| `game/ui/services/ship_io.py` | Production | Edit | Drop local `_cached_registries` global; use helper |
| `game/ui/screens/strategy_build_queue_manager.py` | Production | Edit | Drop local `_cached_registries` global; use helper |
| `game/ui/screens/setup_data_io.py` | Production | Edit | Drop local `_ship_factory` global; use helper |
| `game/ui/screens/setup_screen.py` | Production | Edit | Delete dead `_ship_factory` / `_get_ship_factory()` block (defined but never called) |

## Related Documents
- [design.md](design.md) — architecture analysis and design rationale
- [decisions.md](decisions.md) — full decisions log
- [findings/verification_report.md](findings/verification_report.md) — third-pass verification output
- [findings/source_audit.md](findings/source_audit.md) — pointer to the originating audit
- [findings/bundling_decisions.md](findings/bundling_decisions.md) — Phase D interactive bundling record

## Verification
- [ ] All phase checklists complete
- [ ] All tests passing
- [ ] Audit passed
- [ ] User verified
