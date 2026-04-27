# Phase 1: Triage every site (narrow vs justify vs delete)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-308 1`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Read each of the 24 broad-except sites and decide per-site: narrow / justify / delete. Output a triage table at `findings/triage.md`.

---

## Tasks

### Task 1.1: Read each site and decide [Medium]
**File:** `Projects/active_projects/PROJ-308/findings/triage.md` (NEW)
**Tests:** None — investigation step.

For each of the 24 sites listed in plan.md, do the following:
1. Read 10 lines before and 10 lines after the `except Exception:` line
2. Identify the function/method context — what is being attempted?
3. Identify the realistic failure modes
4. Choose: **narrow** (with new type list), **justify** (with reason text), or **delete**
5. Record in `findings/triage.md` with file:line, current code (1-2 lines), choice, and reasoning

Sites (each becomes a row in the triage table):
- [ ] `game/core/event_logging.py:53`
- [ ] `game/core/event_logging.py:87`
- [ ] `game/core/roles.py:233`
- [ ] `game/ui/services/tkinter_utils.py:100` (already commented — verify quality, possibly no action)
- [ ] `game/ui/panels/system_tree_panel.py:393`
- [ ] `game/ui/panels/system_tree_panel.py:408`
- [ ] `game/simulation/combat/telemetry.py:312`
- [ ] `game/simulation/combat/combat_events.py:161`
- [ ] `game/ui/panels/build_queue_controller.py:217`
- [ ] `game/ui/screens/food_allocation_editor.py:109`
- [ ] `game/ui/screens/battle_setup/controller.py:56`
- [ ] `game/ui/screens/battle_setup/fleet_hierarchy_editor.py:190`
- [ ] `game/ui/screens/builder/stats_config.py:241`
- [ ] `game/ui/screens/species_selector_mixin.py:124`
- [ ] `game/ui/screens/strategy_detail_fmt.py:319`
- [ ] `game/ui/screens/strategy_detail_fmt.py:417`
- [ ] `game/ui/screens/strategy_event_router.py:215`
- [ ] `game/ui/screens/strategy_event_router.py:317`
- [ ] `game/ui/screens/strategy_event_router.py:329`
- [ ] `game/ui/screens/strategy_event_router.py:360`
- [ ] `game/ui/screens/strategy_fleet_command_router.py:259`
- [ ] `game/ui/screens/strategy_window_manager.py:592`
- [ ] `game/ui/screens/transfer_dialog.py:426`
- [ ] `game/ui/screens/workshop_data_reloader.py:23` (already commented — verify quality)

**Notes:**

---

### Task 1.2: Sanity-check the triage [Simple]
**File:** `findings/triage.md`
**Tests:** None — review step.

- [ ] Count: how many narrow / justify / delete? Roughly: most should be **justify** (UI fire-and-forget, telemetry, callbacks); some should be **narrow** (file I/O, JSON parsing, specific framework calls); **delete** should be rare (1-3 max)
- [ ] If the distribution looks wildly skewed (e.g., 22 deletes), revisit — the implementer was probably too aggressive
- [ ] Skim every "justify" reason — does each one say something specific? Reject any that read like "general defensive code" or "third-party stuff"

**Notes:**

---

## Phase Completion Checklist
- [ ] All 24 sites triaged
- [ ] `findings/triage.md` is populated and reviewed
- [ ] Distribution looks reasonable (most justify, some narrow, few/zero delete)
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to next phase (Phase 2)
