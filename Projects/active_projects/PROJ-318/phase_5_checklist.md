# Phase 5: R2 — Make audit + smoke test a real release gate

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-318 5`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Not Started
**Objective:** Replace silent-pass behaviour in two quality
artifacts:
- `Tools/regenerate_ship_portraits/audit.py` exits 0 today even with
  144 size-mismatch warnings and Aetherwake reported CLEAN despite 0
  portraits.
- `tests/integration/ui/test_race_setup_ships_smoke.py` accepts the
  synthetic-fallback Surface as a pass.

After this phase, both will fail loudly on real coverage gaps.

---

## Tasks

### Task 5.1: Audit script — flag missing portraits per theme [Medium]
**File:** `Tools/regenerate_ship_portraits/audit.py`
**Tests:** `pytest tests/unit/tools/test_regenerate_ship_portraits.py -n 12`

- [ ] Read the current portrait-gating logic at lines 129-142 (or wherever the conditional is)
- [ ] Replace `if portrait_rel:` gating with logic that ALWAYS records a finding:
  - If a portrait key is declared, audit the file (existing behavior)
  - If a portrait key is missing, record a `missing_portrait` finding for that theme/ship-class
- [ ] Aggregate per-theme: how many ships have portraits declared, how many don't, how many size mismatches
- [ ] In the report, no theme with zero portraits should be reported "CLEAN"

**Notes:**

### Task 5.2: Audit script — differentiate exit codes [Simple]
**File:** `Tools/regenerate_ship_portraits/audit.py`
**Tests:** Same as 5.1.

- [ ] Use exit codes per the decisions log:
  - `0` = no findings of any kind
  - `2` = size mismatches only (no missing portraits)
  - `3` = missing portraits (regardless of mismatches)
  - `1` = unexpected error (script crash)
- [ ] Print a single summary line at the end: `EXIT 2 — 144 size mismatches, 0 missing portraits` or similar
- [ ] Document the exit-code table at the top of the file in a docstring

**Notes:**

### Task 5.3: Audit-script tests [Medium]
**File:** `tests/unit/tools/test_regenerate_ship_portraits.py` (extend; create if missing)
**Tests:** Self.

- [ ] Test: clean theme → exit 0
- [ ] Test: size mismatch only → exit 2
- [ ] Test: missing portrait → exit 3
- [ ] Test: missing portrait + size mismatch → exit 3 (precedence: missing > mismatch)
- [ ] Test: Aetherwake (zero portraits) is reported as 19 missing-portrait findings, not CLEAN
- [ ] Use temp-dir fixtures with synthetic theme.json + synthetic PNG files (PIL produces 100×100 trivially); no real assets touched

**Notes:**

### Task 5.4: Smoke test — define the allowlist constant [Simple]
**File:** `tests/integration/ui/test_race_setup_ships_smoke.py`
**Tests:** Self.

- [ ] At the top of the file, add the allowlist constant:
  ```python
  EXPECTED_PORTRAIT_GAPS: frozenset[tuple[str, str]] = frozenset({
      *(("Aetherwake", cls) for cls in SHIP_CLASSES_WITH_VISUAL_THEMES),
      ("Atlantians", "Light Cruiser"),
  })
  ```
- [ ] Add `EXPECTED_SIZE_MISMATCHES` if needed (e.g., for Voidforged 1024×1024 and Thoraliens 640×640) — list either at theme level or per-ship level. Document why each entry is allowed.
- [ ] Add a docstring explaining: "These are known gaps the user is expected to fill via `python -m Tools.regenerate_ship_portraits.cli ...`. As the user fills them, this set should shrink. Tests fail when a NEW gap appears."

**Notes:**

### Task 5.5: Smoke test — assert dimension correctness [Medium]
**File:** `tests/integration/ui/test_race_setup_ships_smoke.py`
**Tests:** Self.

- [ ] Add a new test `test_every_portrait_is_2048x2048_or_in_allowlist`:
  - Iterate every `(theme, ship_class)` in `SHIP_CLASSES_WITH_VISUAL_THEMES × theme_data.keys()`
  - Skip pairs in `EXPECTED_PORTRAIT_GAPS` and `EXPECTED_SIZE_MISMATCHES`
  - For each remaining pair, load the portrait via PIL `Image.open(portrait_path)`
  - Assert `(width, height) == (2048, 2048)`
  - Assert mode is RGB or RGBA, not P (palettised)
- [ ] Add a similar test for skins: `test_every_skin_is_2048x2048`
- [ ] Run the test; it should fail on the existing 144 size mismatches if they're not in the allowlist; expand the allowlist OR fix the assets (out of scope here)

**Notes:**

### Task 5.6: Smoke test — discriminate fallback Surfaces [Medium]
**File:** `tests/integration/ui/test_race_setup_ships_smoke.py`
**Tests:** Self.

- [ ] Add a new test `test_every_portrait_is_real_or_in_allowlist`:
  - Get the synthetic-fallback Surface from ShipThemeManager (e.g. via a private helper or by calling `get_portrait_image()` on a non-existent theme)
  - For each `(theme, ship_class)` not in `EXPECTED_PORTRAIT_GAPS`:
    - Call `manager.get_portrait_image(theme, ship_class)`
    - Assert the returned Surface IS NOT the synthetic fallback (compare via identity, hash, or pixel-comparison — pick the cheapest reliable signal)
- [ ] Run the test; expect pass for the 7 themes with full portrait coverage (Federation/Klingons/Ossivine/Prismsteel/Romulans/Thoraliens/Voidforged) and expected fail-then-allowlist for the 2 themes with gaps

**Notes:**

### Task 5.7: Run full test suite [Simple]
**File:** None.
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [ ] Confirm net delta is `+5` (or as expected) tests passing
- [ ] No pre-existing tests broken
- [ ] Targeted: `python -m Tools.regenerate_ship_portraits.audit` exits non-zero (2 or 3)
- [ ] Targeted: `pytest tests/integration/ui/test_race_setup_ships_smoke.py -v` shows the new tests passing with the allowlist

**Notes:**

---

## Phase Completion Checklist
- [ ] All task checkboxes above are checked
- [ ] `python -m Tools.regenerate_ship_portraits.audit` exits 2 or 3 with a clear summary
- [ ] `pytest tests/integration/ui/test_race_setup_ships_smoke.py` passes with the new dimension/fallback assertions
- [ ] Full sharded suite passes
- [ ] Update status at top of this file to `Complete`
- [ ] Update plan.md phase table row to `Complete`
- [ ] Update plan.md Current State to point to Phase 6
- [ ] Commit: `feat(PROJ-318 Phase 5): real release gates for ship-theme audit + smoke test`
