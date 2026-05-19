# PROJ-452 Phase 3: stat_rows_dynamic LABEL_ABBREV retirement (DI-004 + F-C-015)

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-452 3`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Close DI-2026-05-18-004 (IDs side, already closed-by-accident at line 177) + F-C-015 (labels side, still open) in one PR. Drop the two duplicated 5-entry `LABEL_ABBREV` dicts at `stat_rows_dynamic.py:178-181` and `:251-254`; replace with a single `_label_for(resource_id)` helper that wraps `ResourceCatalog.from_json().get(resource_id).name`.

**Cross-bucket file-ownership rule:** This phase touches only `game/ui/screens/builder/stat_rows_dynamic.py` and the matching test file. Do NOT touch any file PROJ-453 / PROJ-454 / PROJ-455 owns.

**Source-of-truth findings:** [`findings/PROJ-452_findings.md`](findings/PROJ-452_findings.md) — read DI-004 and F-C-015's full text. They describe the same two dicts; the framing differs (DI-004 = IDs-side, F-C-015 = labels-side). After this phase, both close.

---

## Tasks

### Task 3.1: Add `_label_for` helper and migrate `get_construction_rows` [Simple]
**File:** `game/ui/screens/builder/stat_rows_dynamic.py:173-192` (`get_construction_rows`)
**Tests:** `pytest tests/unit/ui/screens/builder/test_stat_rows_dynamic.py -v` (create the file if it doesn't exist)

- [ ] Read the current `get_construction_rows` at lines 173-192. Note:
  - Line 175: `from game.core.resources import ResourceCatalog`
  - Line 177: `PLANET_RESOURCE_NAMES = [d.id for d in ResourceCatalog.from_json().by_display_group("planetary")]` (already catalog-driven; do not touch)
  - Lines 178-181: `LABEL_ABBREV = {...}` (the dict to retire)
  - Line 189: `label=LABEL_ABBREV.get(res, res)` (the call site)
- [ ] **Audit catalog data first**: open `data/resources.json` and confirm the five planetary resources have `name` fields. The abbreviated names in `LABEL_ABBREV` (`"Metals"`, `"Organics"`, `"Vapors"`, `"Radact"`, `"Exotics"`) are slightly different from canonical full names. Decision: **adopt catalog `name`** per F-C-015's suggested action. If a test was specifically locking the abbreviated string `"Radact"`, that test was over-specifying — re-point it at the catalog value.
- [ ] **RED**: Add `test_construction_rows_use_catalog_display_names` to `tests/unit/ui/screens/builder/test_stat_rows_dynamic.py`. Build a stubbed ship with a `construction_cost` for `"radioactives"`; call `get_construction_rows(ship)`; assert the row labelled for `radioactives` matches `ResourceCatalog.from_json().get("radioactives").name` (canonical value). This test FAILS today because the row label is `"Radact"`, not the catalog name.
- [ ] **GREEN — add helper**: Add a module-level helper at the top of `stat_rows_dynamic.py` (above `get_construction_rows`):
  ```python
  def _label_for(resource_id: str) -> str:
      """Return the canonical display label for a resource id.
  
      Falls back to the raw id if the catalog isn't populated (defensive
      guard against partial-hydration test contexts).
      """
      from game.core.resources import ResourceCatalog
      try:
          definition = ResourceCatalog.from_json().get(resource_id)
          if definition is not None:
              return definition.name
      except Exception:  # Intentional broad catch: resource catalog may be unavailable in some test fixtures
          pass
      return resource_id
  ```
- [ ] **GREEN — migrate construction rows**: Delete the `LABEL_ABBREV` dict at lines 178-181. Replace `label=LABEL_ABBREV.get(res, res)` at line 189 with `label=_label_for(res)`.
- [ ] Run the RED test — confirm GREEN.
- [ ] Run `pytest tests/unit/ui/screens/builder/test_stat_rows_dynamic.py -v` to confirm no regression elsewhere.

**Notes:** [Filled during implementation.]

---

### Task 3.2: Migrate `get_strategic_rows` to use `_label_for` [Simple]
**File:** `game/ui/screens/builder/stat_rows_dynamic.py:246-274` (`get_strategic_rows`)
**Tests:** `pytest tests/unit/ui/screens/builder/test_stat_rows_dynamic.py -v`

- [ ] Read the current `get_strategic_rows` at lines 246-274. Note the duplicate `LABEL_ABBREV` dict at 251-254 and the two `LABEL_ABBREV.get(res, res)` call sites at 262 (harvester) and 272 (storage).
- [ ] **RED**: Add `test_strategic_harvester_row_labels_use_catalog_names` and `test_strategic_storage_row_labels_use_catalog_names`. Build a stubbed ship whose `_get_strategic_abilities(ship)` returns `{'harvesters': {'radioactives': 1.5}, 'storage': {'exotics': 100}, ...}`. Assert the harvester row label is `f"Harv {catalog.get('radioactives').name}"` and the storage row label is `f"Stor {catalog.get('exotics').name}"`. Both tests FAIL today.
- [ ] **GREEN**: Delete the duplicate `LABEL_ABBREV` dict at 251-254. Replace `LABEL_ABBREV.get(res, res)` at lines 262 and 272 with `_label_for(res)`. The `f"Harv {LABEL_ABBREV.get(res, res)}"` and `f"Stor {LABEL_ABBREV.get(res, res)}"` patterns become `f"Harv {_label_for(res)}"` and `f"Stor {_label_for(res)}"`.
- [ ] Run targeted tests — confirm GREEN.
- [ ] **Verify single source of truth**: `rg -n LABEL_ABBREV game/ui/screens/builder/stat_rows_dynamic.py` should return zero matches. The dict is now retired across the file.

**Notes:** [Filled during implementation.]

---

### Task 3.3: Update DI log + bucket-C closure [Simple]

- [ ] Update DI-2026-05-18-004 in `AgentCoordination/discovered_issues/log.jsonl` with `"status": "resolved"` and `"resolution_note": "Updated 2026-XX-XX PROJ-452 Phase 3: LABEL_ABBREV dicts at stat_rows_dynamic.py:178-181 and :251-254 retired in favour of _label_for(resource_id) helper wrapping ResourceCatalog.from_json().get(rid).name. F-C-015 (labels-side companion) closed in same PR."` (substitute the actual date).
- [ ] F-C-015 is not in `log.jsonl`; it's in `Projects/archived_projects/PROJ-446/findings/bucket_c_ui_core_tests_scan.md` (read-only). Record the closure in PROJ-452's own [decisions.md](decisions.md) as a row: `2026-XX-XX | F-C-015 closed in PROJ-452 Phase 3 alongside DI-004 (same two dicts, labels-side framing) | Single PR retires LABEL_ABBREV across both get_construction_rows and get_strategic_rows`.

**Notes:**

---

## Phase Completion Checklist

When all tasks above are checked off:

- [ ] DI-2026-05-18-004 marked `resolved` in `log.jsonl`
- [ ] F-C-015 closure recorded in `decisions.md`
- [ ] Three new tests in `test_stat_rows_dynamic.py` green
- [ ] `pytest tests/unit/ui/screens/builder/ -v` green
- [ ] `rg -n LABEL_ABBREV game/ui/screens/builder/stat_rows_dynamic.py` returns zero matches
- [ ] Full sharded suite green (`python Tools/test_sharded/test_sharded.py`)
- [ ] Run `python Projects/scripts/validate_phase.py PROJ-452 3` — PASSED
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 4

## Notes / Deferrals

- **Catalog `name` vs the legacy abbreviation `"Radact"`** — F-C-015 explicitly directs use of `ResourceDefinition.name` as the canonical source of truth. If a downstream UI test was locking the legacy abbreviation, it was over-specifying; re-point it at the catalog value.
- **Defensive `Exception` fallback in `_label_for`** — required because some test fixtures construct stub ships without a full registry hydration. The fallback returns the raw `resource_id` (same as the original `LABEL_ABBREV.get(res, res)` default), so the worst-case behaviour is unchanged.
- **Sweep targets in the rest of `stat_rows_dynamic.py`** — Phase 4 covers this. Phase 3 stays narrow.
