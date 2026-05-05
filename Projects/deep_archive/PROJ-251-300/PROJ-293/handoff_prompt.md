# Handoff: PROJ-293 — Phase 3, Task 3.2 (User Manual Smoke)

Resume **PROJ-293** at **Phase 3 Task 3.2**. The previous session completed all agent-doable Phase 3 work (label widths bumped, MEMORY.md updated, full sharded suite green at 15112/15112). Task 3.2 is a manual smoke that **must be performed by the user** — an agent cannot launch the game and visually verify warnings.

If the user is willing to run the smoke now, no new agent session is needed; the user can directly mark Task 3.2 complete in `Projects/active_projects/PROJ-293/phase_3_checklist.md` and archive. If a follow-up agent session is needed (e.g. to investigate a new warning that surfaces), use this prompt.

## Orientation (read BEFORE touching the project plan)

The instinct is to open `plan.md` first. Resist it. PROJ-293 sits inside the FACTOR_REGISTRY pattern (PROJ-283); a cold reader who hasn't internalized that contract will make short-sighted decisions.

### 1. Foundation docs (always read these first)
- [docs/README.md](../../../docs/README.md) — doc index + task-driven reading order
- [docs/01_ARCHITECTURE.md](../../../docs/01_ARCHITECTURE.md) — six-layer structure, dependency rules, package APIs
- [docs/02_PATTERNS.md](../../../docs/02_PATTERNS.md) — design patterns (Registry pattern is #4)
- [docs/03_CONVENTIONS.md](../../../docs/03_CONVENTIONS.md) — naming, file organization, test conventions

### 2. Task-specific docs
- [docs/systems/strategy_layer.md §7 (lines 1191-1349)](../../../docs/systems/strategy_layer.md#L1191-L1349) — Race Preferences & Habitability (PROJ-283), the FACTOR_REGISTRY pattern this project extended. Especially the "Adding a new factor" recipe at line 1273+ — PROJ-293 made that recipe truly single-edit.
- [CLAUDE.md](../../../CLAUDE.md) — Three Non-Negotiable Rules (TDD, docs check/update, clean-sheet design)
- Auto-memory topic file: `C:\Users\rossr\.claude\projects\c--Dev-Starship-Battles\memory\proj_293_display_contract.md` — the schema-extension detail (per-factor display table, format_value before/after).

### 3. Related code (read for context, even if not modifying)
- [game/strategy/data/habitability_factors.py](../../../game/strategy/data/habitability_factors.py) — `HabitabilityFactor` dataclass (the 12-field frozen dataclass + 2 PROJ-293 fields). Whole file is 350 lines, worth reading.
- [game/ui/widgets/preference_row.py](../../../game/ui/widgets/preference_row.py) — `PreferenceRow` widget. The data-driven `format_value()` at lines 73-94 is the new contract. Layout constants at lines 43-50.
- [game/ui/panels/race_environment_panel.py](../../../game/ui/panels/race_environment_panel.py) — the panel that constructs one `PreferenceRow` per factor (read for understanding the UI integration point).
- [game/ui/screens/race_setup_screen.py](../../../game/ui/screens/race_setup_screen.py) — the screen that hosts the race environment panel (this is what the user opens for the manual smoke).

### 4. Related tests (read so you know what "working" looks like)
- [tests/unit/strategy/data/test_habitability_factors.py](../../../tests/unit/strategy/data/test_habitability_factors.py) — `TestDisplayFields` (lines ~165-228) is the contract enforcement; `TestHabitabilityFactorDataclass.test_has_required_fields` enforces the schema.
- [tests/unit/ui/widgets/test_preference_row.py](../../../tests/unit/ui/widgets/test_preference_row.py) — `TestDisplayScaling` (lines ~176-260) covers existing + PROJ-293 new tests for tectonic, radiation, and a fake factor.
- [tests/unit/ui/test_race_environment_panel.py](../../../tests/unit/ui/test_race_environment_panel.py) — neighboring panel-level tests that exercise PreferenceRow indirectly.

## Only now: read the project files

1. [Projects/active_projects/PROJ-293/design.md](design.md) — display-contract mapping table; rationale for the 60→90 width bump
2. [Projects/active_projects/PROJ-293/decisions.md](decisions.md) — full decision log (especially: why keep storage `unit`, why `%` is glued, why 90 over 75)
3. [Projects/active_projects/PROJ-293/plan.md § Current State](plan.md) — authoritative handoff (see `**Last Action**` and `**Next Action**`)
4. [Projects/active_projects/PROJ-293/phase_3_checklist.md](phase_3_checklist.md) — Task 3.2 checklist
5. [Projects/active_projects/PROJ-293/manifest.md](manifest.md) — full file manifest

## First action

Run the user-only manual smoke:

```bash
python launcher.py
```

Then in-game:

1. Start a new game / quickstart that exposes the race editor (Setup → Custom Race, or the equivalent flow that surfaces the habitability sliders).
2. Capture stderr output during scroll. **Confirm none** of these 7 warnings appear (they were the original failure):
   - `Label Rect is too small for text: 101.3 kPa - size diff: (-3, 2)`
   - `Label Rect is too small for text: ±20.0 kPa - size diff: (-3, 2)`
   - `Label Rect is too small for text: 0.30 fraction - size diff: (-23, 2)`
   - `Label Rect is too small for text: ±0.20 fraction - size diff: (-31, 2)`
   - `Label Rect is too small for text: 0.00 shielding - size diff: (-35, 2)`
   - `Label Rect is too small for text: ±50.00 shielding - size diff: (-51, 2)`
   - `Label Rect is too small for text: ±10.0 kPa - size diff: (-3, 2)`
3. Confirm visual rendering:
   - tectonic shows `0.30` (not `0.30 fraction`)
   - radiation shows `0` (not `0.00 shielding`)
   - gravity shows `1.0 g`
   - temperature shows `288 K` (or whatever default — point is "K" suffix, integer)
   - water shows `50%`
   - pressure / gases show `kPa`
   - magnetic shows `EE`

## Watchouts (from the previous session)

- **Storage `unit` field is intentionally kept** — it's the canonical storage label, distinct from the new `display_unit`. Don't suggest "rename `unit` to `storage_unit`" — it would force migration of any code that reads it (extractors, scorers, future scientific calculations).
- **`%` is glued to the number ("50%"), all other units take a separating space ("1.0 g")** — this is a single deliberate special case in `format_value`. If a future factor wants a glued unit, extend the special case; don't redesign the function.
- **The label width 60→90 bump is generous on purpose** — the worst case I sized for was a hypothetical future factor with a 5-char `display_unit` and 2 decimals (`"±50.00 abcde"`). 75px would be tight; 90px gives margin. Don't shrink unless a factor with a guaranteed-narrow output range needs it.
- **MEMORY.md was at the size budget when I added the PROJ-293 entry** — I created a topic file (`proj_293_display_contract.md`) and added a one-line index entry. If the next agent adds more memory, they should follow the topic-file pattern rather than appending inline detail.
- **If a new `Label Rect` warning appears for a factor I missed**, the lever is the registry's `display_precision` — that's where to fix it. Don't widen the label further.
- **`HabitabilityFactor` is a frozen dataclass with no out-of-registry instantiation sites.** Adding the two new fields with defaults was backward-compatible; they don't break any existing constructors.

## Protocol

Follow [Projects/protocols/03a_continue_working.md](../../protocols/03a_continue_working.md). The remaining work is just user verification + the agent-side closeout of marking the user-gated tasks done. After user verifies:

1. Mark Task 3.2's 7 subtasks `[x]` in `phase_3_checklist.md`.
2. Mark items 4-5 of the Phase Completion Checklist `[x]`.
3. Update `phase_3_checklist.md` Status to `Complete`.
4. Update `plan.md` phase table: row 3 → `Complete`.
5. Update `plan.md` Current State to "Project complete — ready to archive".
6. Run `python Projects/scripts/validate_phase.py PROJ-293 3` — should be PASSED.
7. Run `python Projects/scripts/validate_close_ready.py PROJ-293`.
8. If green: `python Projects/scripts/archive_project.py PROJ-293`.
