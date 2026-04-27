# PROJ-308: Broad Exception Handler Justifications

> **WORKING ON THIS PROJECT:**
> - Run `python Projects/scripts/current_task.py PROJ-308` to see what to do next
> - Open the phase checklist file for your current phase
> - Check off tasks as you complete them
> - Update Current State before stopping work

> **STOPPING WORK:**
> - Run `python Projects/scripts/validate_phase.py PROJ-308 [phase]` before stopping
> - Update Current State with specific handoff context

## Quick Status
| Phase | Status | Checklist |
|-------|--------|-----------|
| 1. Triage every site (narrow vs justify vs delete) | Not Started | [phase_1_checklist.md](phase_1_checklist.md) |
| 2. Apply per-site action | Not Started | [phase_2_checklist.md](phase_2_checklist.md) |
| 3. Add convention to CLAUDE.md / 05_ERROR_HANDLING.md | Not Started | [phase_3_checklist.md](phase_3_checklist.md) |

## Current State
**Last Updated:** 2026-04-26
**Active Phase:** Planning (approved, ready for implementation)
**Last Action:** Project created from 2026-04-26 review remaining-items list. Verified site count: **24 broad `except Exception:` clauses across 18 files** (not 28 as originally claimed)
**Next Action:** Begin Phase 1 — read each of the 24 sites, decide per-site whether to narrow the type, justify with comment, or delete the handler entirely
**Blockers:** None
**Context for Next Agent:** 2 of the 24 sites already have intent comments ([game/ui/services/tkinter_utils.py:100](game/ui/services/tkinter_utils.py#L100) "Intentional: destroy may fail if already destroyed", [game/ui/screens/workshop_data_reloader.py:23](game/ui/screens/workshop_data_reloader.py#L23) "Intentional broad catch: Tkinter init is platform-dependent"). The other 22 are uncommented. The user wants WHY-comments on every broad except, not just bulk justification — this is a triage exercise per site.

## Overview
Address every broad `except Exception:` clause in production code (`game/`). Per CLAUDE.md "Long-Term Quality" rules, the preference order is:
1. **Narrow** to a specific exception type if the expected failure modes are known
2. **Justify** with a `# Intentional broad catch: <reason>` comment if narrowing isn't viable (e.g., third-party callbacks, platform-dependent init, fire-and-forget event emission)
3. **Delete** the handler if the catch was masking a real bug rather than handling a real failure

The user's directive: "I want reasons for the Broad excepts - these should be commented." Every broad except must end this project with either narrow types or a clear justification comment.

## Goals
- Triage all 24 broad-except sites
- Narrow types where possible, comment-justify where not, delete where the handler was the bug
- Establish the convention in `CLAUDE.md` / `docs/05_ERROR_HANDLING.md`: future broad excepts MUST carry a one-line `# Intentional broad catch: <reason>` comment

## Scope

**In:**
- All 24 `except Exception:` sites in `game/` (per verified grep 2026-04-26):

| File | Count | Sites |
|------|-------|-------|
| `game/core/event_logging.py` | 2 | lines 53, 87 |
| `game/core/roles.py` | 1 | line 233 |
| `game/ui/services/tkinter_utils.py` | 1 | line 100 (already commented — verify quality) |
| `game/ui/panels/system_tree_panel.py` | 2 | lines 393, 408 |
| `game/simulation/combat/telemetry.py` | 1 | line 312 |
| `game/simulation/combat/combat_events.py` | 1 | line 161 |
| `game/ui/panels/build_queue_controller.py` | 1 | line 217 |
| `game/ui/screens/food_allocation_editor.py` | 1 | line 109 |
| `game/ui/screens/battle_setup/controller.py` | 1 | line 56 |
| `game/ui/screens/battle_setup/fleet_hierarchy_editor.py` | 1 | line 190 |
| `game/ui/screens/builder/stats_config.py` | 1 | line 241 |
| `game/ui/screens/species_selector_mixin.py` | 1 | line 124 |
| `game/ui/screens/strategy_detail_fmt.py` | 2 | lines 319, 417 |
| `game/ui/screens/strategy_event_router.py` | 4 | lines 215, 317, 329, 360 |
| `game/ui/screens/strategy_fleet_command_router.py` | 1 | line 259 |
| `game/ui/screens/strategy_window_manager.py` | 1 | line 592 |
| `game/ui/screens/transfer_dialog.py` | 1 | line 426 |
| `game/ui/screens/workshop_data_reloader.py` | 1 | line 23 (already commented — verify quality) |
| **TOTAL** | **24 across 18 files** | |

- Convention update in CLAUDE.md and `docs/05_ERROR_HANDLING.md`

**Out:**
- `tests/` directory broad-except clauses (lower priority; tests can fail loudly)
- `Tools/` and `Reviews/` broad-except clauses (handled in PROJ-297 Phase 4)
- Bare `except:` clauses (already addressed in PROJ-297 Phase 4)

## Key Files
See the table above for the 18 files with broad-except sites. Convention files:
| Component | File Path |
|-----------|-----------|
| Convention enforcement | `CLAUDE.md` ("Long-Term Quality" / "Specific exceptions over broad catches") |
| Error handling guide | `docs/05_ERROR_HANDLING.md` |

## Related Documents
- [design.md](design.md) - Triage methodology
- [decisions.md](decisions.md) - Decisions log

## Verification
- [ ] All phase checklists complete
- [ ] Every remaining `except Exception:` in `game/` has an `# Intentional broad catch: <reason>` comment within 1-2 lines
- [ ] CLAUDE.md mentions the broad-catch comment requirement
- [ ] `docs/05_ERROR_HANDLING.md` documents the convention
- [ ] Full sharded suite passes (15389+ baseline)
- [ ] User verified
