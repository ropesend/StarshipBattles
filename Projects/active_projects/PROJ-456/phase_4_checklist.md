# PROJ-456 Phase 4: transfer_dialog cluster + characterization sweep

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-456 4`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Depends on:** None (write scope disjoint from Phases 1-3, but recommend running after Phase 1 so the F-C-002 marker change lands in this file first).
**Review Mode:** standard
**Objective:** Four-pronged `transfer_dialog.py` cleanup. The file is already 448 LOC at HEAD (re-measured 2026-05-19; under the 500-LOC ceiling). After this phase, LOC drops further to ~390-420 by retiring the shim cluster. **DI-2026-05-18-002 closes because the shim residue (the underlying motivation of the original "LOC overflow" framing) is gone — not because the LOC drops under the ceiling, which already happened.**

**Source-of-truth findings:** F-C-003, F-C-011, F-C-029, DI-2026-05-18-002 in [`findings/PROJ-456_findings.md`](findings/PROJ-456_findings.md).

**Codex r4 risk flag:** "Job 8 is still the biggest review burden in the new plan. If the diff starts looking like 'every UI screen changed', cut it into two PRs by feature family." → Phase 4 is the largest single PR in the project. Operator may split into 4a (F-C-003 + F-C-011 — small) and 4b (F-C-029 — 69-ref sweep) if review burden warrants.

---

## Tasks

### Task 4.1: F-C-003 — Retire 3 method shims [Simple]
**File:** `game/ui/screens/transfer_dialog.py:279-286`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog_characterization.py -q`

- [ ] Read the three method shims at transfer_dialog.py:279-286. Confirm each delegates trivially:
  - `_extract_dropdown_value(value)` → `TransferGridRenderer.extract_dropdown_value(value)` (static)
  - `_format_pending(amount)` → `self.view_model.format_pending(amount)`
  - `_discover_pod_designs()` → `self._controller.discover_pod_designs(self.scene)`
- [ ] Find characterization-test sites: `rg -n "dialog\._extract_dropdown_value|dialog\._format_pending|dialog\._discover_pod_designs" tests` (expect 2-3 hits per finding).
- [ ] **RED**: Migrate each test site to call the underlying canonical surface directly. Example: `dialog._format_pending(amount)` → `dialog.view_model.format_pending(amount)`. Run; tests pass with same semantics.
- [ ] **GREEN**: Delete the three method shims + the comment block at lines 274-277 (~13 lines total).
- [ ] **Verify**: `rg -n "_extract_dropdown_value|_format_pending|_discover_pod_designs" game tests` returns hits only on the canonical-surface definitions (TransferGridRenderer / TransferViewModel / TransferController), not on the dialog.
- [ ] Check `_on_source_changed` at line 292 — it uses `self._extract_dropdown_value(label)`. Migrate that internal call to `TransferGridRenderer.extract_dropdown_value(label)`.
- [ ] Run targeted tests.

---

### Task 4.2: F-C-011 — Retire sentinel + layout-constant class re-exports [Simple]
**File:** `game/ui/screens/transfer_dialog.py:58-86`
**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog.py tests/unit/ui/screens/test_transfer_dialog_characterization.py tests/unit/ui/screens/test_transfer_dialog_enhanced.py -q`

- [ ] Read sentinel re-exports at transfer_dialog.py:58-62 (`MAX_LOAD`, `MAX_DROP`) and the 18 layout-constant re-exports at lines 64-86 (`ROW_HEIGHT` through `TARGET_AMT_W`).
- [ ] Confirm canonical homes by reading:
  - `game/ui/screens/transfer_view_model.py` — should define `MAX_LOAD` and `MAX_DROP`.
  - `game/ui/screens/transfer_grid_renderer.py` — should define the 18 layout constants.
- [ ] Audit importers: `rg -n "TransferDialog\.(MAX_LOAD|MAX_DROP|ROW_HEIGHT|NAME_X|NAME_W|SOURCE_AMT_X|MAX_LOAD_X|LOAD_ARROWS_X|PENDING_X|ZERO_BTN_X|DROP_ARROWS_X|MAX_DROP_X|TARGET_AMT_X)" game tests`. For each, migrate to the canonical-home class (`TransferViewModel.MAX_LOAD`, `TransferGridRenderer.ROW_HEIGHT`, etc.).
- [ ] **GREEN**: Delete the sentinel + layout-constant blocks at lines 58-86 (~29 lines including comments and gaps).
- [ ] Run targeted tests; sharded suite green for the touched files.

**Notes:** If any internal use of these constants exists inside `transfer_dialog.py` itself, replace with the canonical-class reference (e.g. `TransferGridRenderer.ROW_HEIGHT` instead of `self.ROW_HEIGHT`).

---

### Task 4.3: F-C-029 — 69-ref characterization-test sweep [Medium]
**Files:**
- `tests/unit/ui/screens/test_transfer_dialog_characterization.py` (61 refs)
- `tests/unit/ui/screens/test_transfer_dialog.py` (5 refs)
- `tests/unit/ui/screens/test_transfer_dialog_enhanced.py` (3 refs)
- `game/ui/screens/transfer_dialog.py` (delete 6 dialog-level property shims)

**Tests:** `pytest tests/unit/ui/screens/test_transfer_dialog_characterization.py tests/unit/ui/screens/test_transfer_dialog.py tests/unit/ui/screens/test_transfer_dialog_enhanced.py -q`

- [ ] Locate the 6 dialog-level property shims in transfer_dialog.py. Use `rg -n "Back-compat property shims" game/ui/screens/transfer_dialog.py` to find the comment header. The shims cover:
  - `available_sources` → `view_model.available_sources`
  - `available_targets` → `view_model.available_targets`
  - `pending_transfers` → `view_model.pending_transfers`
  - `_row_data` → `view_model.row_data`
  - `_filter_empty` → `view_model.filter_empty`
  - `_current_source` / `_current_target` → `view_model.current_source` / `view_model.current_target`
- [ ] **RED**: For each test file, do the mechanical sweep (sed-style, but verify by hand each block):
  - `dialog._current_source` → `dialog.view_model.current_source` (read & write)
  - `dialog._current_target` → `dialog.view_model.current_target`
  - `dialog._row_data` → `dialog.view_model.row_data`
  - `dialog._filter_empty` → `dialog.view_model.filter_empty`
  - `dialog.available_sources` → `dialog.view_model.available_sources`
  - `dialog.available_targets` → `dialog.view_model.available_targets`
  - `dialog.pending_transfers` → `dialog.view_model.pending_transfers`
- [ ] Run each test file individually after migration.
- [ ] **GREEN**: Delete the 6 dialog-level property shim block + its comment header in transfer_dialog.py.
- [ ] **Verify (PowerShell-safe)**: `rg -n "dialog\.(_current_source|_current_target|_row_data|_filter_empty|available_sources|available_targets|pending_transfers)" tests` returns 0 hits.
- [ ] Run all 3 transfer_dialog test files; sharded suite green.

**Notes:** This is the most LOC-intensive single migration in the project. If split into a separate PR (4b), it can land independently of 4.1 + 4.2 because the property shims and the method/constant shims are distinct surfaces.

---

### Task 4.4: DI-2026-05-18-002 — verify natural close + update DI log [Simple]
**Files:** `game/ui/screens/transfer_dialog.py` (verify LOC), `AgentCoordination/discovered_issues/log.jsonl` (append resolution_note).

- [ ] Run (PowerShell-safe): `(Get-Content game/ui/screens/transfer_dialog.py | Measure-Object -Line).Lines`. Expected: ~390-420 LOC (current HEAD 448 minus ~13 from Task 4.1 minus ~29 from Task 4.2 minus the 6 dialog-level property shim block from Task 4.3). The file is already under the 500-LOC ceiling pre-phase per 2026-05-19 re-measurement.
- [ ] Append a `resolution_note` to the `transfer_dialog.py`-anchored DI-2026-05-18-002 entry (dated 2026-05-18T16:57:38Z; the second of two DI-2026-05-18-002 entries in the log — **key on `file: game/ui/screens/transfer_dialog.py` to disambiguate from the already-resolved CommandRegistry entry at registry.py:327**). Set `status: resolved` and add note like `Closed 2026-05-XX PROJ-456 Phase 4 — F-C-003 + F-C-011 + F-C-029 retired the back-compat shim surface; LOC dropped from 448 (pre-phase HEAD) to <FINAL>; original "LOC overflow" framing was already stale at pre-phase HEAD.`
- [ ] If still over 500: do NOT mark resolved. Investigate which shim cluster did not actually drop the expected LOC; record in `decisions.md`. The DI entry remains open for future structural extraction (likely PROJ-457 territory if the overage is structural).
- [ ] Use `Tools/agent_coordination/triage_discovered_issues.py --update DI-2026-05-18-002` (or the established edit pattern — read the README at `AgentCoordination/discovered_issues/README.md` if unfamiliar).

---

## Phase Completion Checklist

When all 4 tasks are checked off:
- [ ] F-C-003, F-C-011, F-C-029, DI-2026-05-18-002 flipped to `Status: resolved` in `findings/PROJ-456_findings.md`.
- [ ] DI-2026-05-18-002 marked resolved in `AgentCoordination/discovered_issues/log.jsonl` (or noted as still-open with a documented reason).
- [ ] `transfer_dialog.py` under 500 LOC.
- [ ] Run `python Tools/test_sharded/test_sharded.py` — full sharded suite green.
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-456 4` — PASSED.
- [ ] Update status at top of this file to `Complete`.
- [ ] Update plan.md phase table row to `Complete`.
- [ ] Update plan.md Current State to point to Phase 5.
- [ ] Commit message: `PROJ-456 Phase 4: retire transfer_dialog shim cluster (F-C-003, F-C-011, F-C-029); LOC 448 -> <FINAL>; DI-2026-05-18-002 closed (shim-residue framing, not LOC overflow which was already stale)`.
- [ ] No new entries in `AgentCoordination/discovered_issues/log.jsonl` unless they are genuine out-of-scope discoveries.
