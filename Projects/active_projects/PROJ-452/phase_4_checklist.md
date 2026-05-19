# PROJ-452 Phase 4: Sweep — catalog-vs-hardcode residue in adjacent UI surfaces

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-452 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Audit-then-decide phase. With Phases 1-3 closing the three known DI/F-C findings, sweep the immediate UI neighbourhood of `stat_rows_dynamic.py` for any other hardcoded resource lists or display labels in the same anti-pattern. The phase ships either (a) additional fixes if hardcodes are found, or (b) an audit report in `decisions.md` confirming the surface is clean.

**Cross-bucket file-ownership rule:** This phase may touch additional UI files (per the audit), but stays entirely within `game/ui/screens/builder/` and `game/ui/panels/`. Do NOT touch any file PROJ-453 / PROJ-454 / PROJ-455 owns. Do NOT touch `game/ui/screens/transfer_dialog.py` or other UI files outside the resource-display scope.

**Source-of-truth findings:** [`findings/PROJ-452_findings.md`](findings/PROJ-452_findings.md) — read the "Sweep targets" section at the bottom of that file for the candidate list.

---

## Tasks

### Task 4.1: Sweep the rest of `stat_rows_dynamic.py` for hardcoded resource constants [Simple]
**File:** `game/ui/screens/builder/stat_rows_dynamic.py` (full file post-Phase-3)
**Tests:** `pytest tests/unit/ui/screens/builder/test_stat_rows_dynamic.py -v`

- [ ] After Phase 3, `LABEL_ABBREV` is retired. Read the full file end-to-end and identify any other hardcoded resource enumerations:
  - `get_logistics_rows` (lines 164-170): uses `_discover_resources(ship)` — dynamic discovery from the ship's actual resources; correct pattern. **Do not touch.**
  - `_get_strategic_abilities` (lines 197-243): iterates `layer_items` and discovers harvester/storage abilities from the components themselves; correct pattern. **Do not touch.**
  - The harvester/storage row builders at 256-274: iterate `info['harvesters']` / `info['storage']` which are dynamically populated; correct pattern. **Do not touch.**
- [ ] Run `rg -n '"metals"|"organics"|"vapors"|"radioactives"|"exotics"|"fuel"|"energy"|"ammo"' game/ui/screens/builder/stat_rows_dynamic.py` — any remaining match that's not part of a docstring, comment, or test fixture is a Phase 4 target.
- [ ] If a match is found that is the same anti-pattern, treat it as a Phase 4 fix: apply the same `ResourceCatalog.from_json()` iteration / `_label_for` helper used in Phase 3.
- [ ] If no matches survive, record the audit result in `decisions.md` as: `2026-XX-XX | stat_rows_dynamic.py audit | No hardcoded resource enumerations remain after Phase 3; the remaining ability-discovery loops are dynamic per ship component.`

**Notes:** [Filled during implementation.]

---

### Task 4.2: Audit `game/ui/panels/empire_treasury_panel.py` [Simple]
**File:** `game/ui/panels/empire_treasury_panel.py` (full file)
**Tests:** `pytest tests/unit/ui/panels/ -k empire_treasury -v`

- [ ] Read the full file. The known helper at line 32 (`return tuple(d.id for d in ResourceCatalog.from_json().by_display_group("planetary"))`) is already catalog-driven.
- [ ] `rg -n '"metals".*"organics"|RESOURCE_NAMES\b|RESOURCE_TYPES\b' game/ui/panels/empire_treasury_panel.py` — any hardcoded list is a Phase 4 target.
- [ ] Specifically check the panel render loop, the column / header definitions, and any `_format_*` helpers. PROJ-436 Phase 7 retired the worst offenders but the panel is large enough to re-audit.
- [ ] If a match is found, apply the same fix pattern.
- [ ] If clean, record in `decisions.md`: `empire_treasury_panel.py audit | catalog-driven end-to-end; no remaining hardcoded resource lists.`

**Notes:** [Filled during implementation.]

---

### Task 4.3: Audit `game/ui/screens/build_queue_helpers.py` [Simple]
**File:** `game/ui/screens/build_queue_helpers.py` (full file)
**Tests:** `pytest tests/unit/ui/screens/ -k build_queue -v`

- [ ] Read the full file. The comment at line 14 ("`ResourceCatalog.from_json()` call that ran at import time, breaking ...") suggests the file was previously a hardcode site that's been migrated; verify by inspection.
- [ ] `rg -n '"metals".*"organics"|RESOURCE_NAMES\b|RESOURCE_TYPES\b' game/ui/screens/build_queue_helpers.py` — any hardcoded list is a target.
- [ ] If a match is found, apply the same fix pattern.
- [ ] If clean, record in `decisions.md`: `build_queue_helpers.py audit | catalog-driven; comment at line 14 is historical narration, no live residue.`

**Notes:** [Filled during implementation.]

---

### Task 4.4: Backstop grep across `game/ui/` and `game/strategy/` [Simple]
**Tests:** `pytest -q` for any file the grep identifies

- [ ] Run the backstop grep:
  ```powershell
  rg -n '"metals".*"organics".*"vapors"|RESOURCE_NAMES\b|RESOURCE_TYPES\b' game/ui/ game/strategy/
  ```
- [ ] For each match (excluding docstrings, comments, test fixtures, and already-fixed sites from Phases 1-3):
  - If the match is part of a hardcoded enumeration that controls behaviour, treat as in-scope and fix with the established pattern.
  - If the match is a comment / docstring narrating historical context, leave it.
  - If the match is in a test file, treat it as test-fixture data — leave it.
- [ ] Document each decision in `decisions.md`: `File:line | classification (residue / narration / test-data) | action taken (fixed / no-op).`

**Notes:** Phase 4 caps at a single sweep iteration. If the backstop grep surfaces a large cluster of residue (>5 sites), surface it for user discussion rather than expanding the phase. The Codex r4 redesign explicitly limited PROJ-452 to a "small" scope.

---

### Task 4.5: Phase 4 closure record [Simple]
**File:** `Projects/active_projects/PROJ-452/decisions.md`

- [ ] Aggregate the per-task audit results from Tasks 4.1-4.4 into a single Phase 4 closure entry in `decisions.md`. Shape:
  ```markdown
  | 2026-XX-XX | PROJ-452 Phase 4 closure | Audited stat_rows_dynamic.py, empire_treasury_panel.py, build_queue_helpers.py, plus backstop grep across game/ui/ + game/strategy/. Findings: [N production fixes applied / 0 residue found]. PROJ-452 scope closed. |
  ```
- [ ] If Phase 4 produced any production fixes, list them by file:line in the closure entry.

**Notes:**

---

## Phase Completion Checklist

When all tasks above are checked off:

- [ ] Sweep grep returns zero new residue (or all residue fixed)
- [ ] `decisions.md` carries the Phase 4 closure entry
- [ ] All affected test files green
- [ ] Full sharded suite green (`python Tools/test_sharded/test_sharded.py`)
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-452 4` — PASSED
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to "Project complete; awaiting end-of-project Codex consult per the standing workflow"

## Notes / Deferrals

- **Out-of-scope file families** — Phase 4 explicitly does NOT touch `game/ui/screens/transfer_dialog.py`, `game/ui/screens/orders_window.py`, or other UI screens whose residue is tracked by sibling future projects (UI shim retirement sweep — Codex r4 redesign job #8). PROJ-452 stays narrow on the resource-catalog boundary.
- **`game/strategy/`** matches in the backstop grep — production strategy code should already be catalog-driven post-PROJ-436. Any match is likely a docstring / historical narration; treat with care.
- **Future scope** — if Phase 4 discovers >5 residue sites, the right move is to surface this in the end-of-project Codex consult and let a future project absorb the larger sweep; do not expand PROJ-452 inline.
