# Phase 7: Polish, MAX_LENGTH bump, docs, full sharded suite [Simple]

> **BEFORE MARKING THIS PHASE COMPLETE:**
> 1. Run `python Projects/scripts/validate_phase.py PROJ-299 7`
> 2. Only proceed if output shows PASSED
> 3. Update plan.md phase table AND Current State

**Status:** Complete
**Objective:** Bump MAX_LENGTH 500 → 5000. Widen char-count label. Update docs. Final sharded suite verification.

---

## Tasks

### Task 7.1: Bump `MAX_LENGTH` from 500 to 5000 [Simple]
**File:** `game/ui/panels/race_description_panel.py`
**Tests:** `pytest tests/unit/ui/test_race_description_panel.py`

- [x] Write failing test asserting MAX_LENGTH == 5000
- [x] Update Phase B Test Impact's 4 affected assertions in `test_race_description_panel.py` (display-format tests checking `"X/500"` → `"X/5000"`)
- [x] Update `MAX_LENGTH = 5000` in race_description_panel.py:29
- [x] Run tests, confirm pass

**Notes:**

### Task 7.2: Widen the character-count label [Simple]
**File:** `game/ui/panels/race_description_panel.py`
**Tests:** Visual / smoke

- [x] The current label is 80px wide; "5000/5000" + slash needs ~110px. Bump label width:
  - bio_char_label: width 80 → 110 in race_description_panel.py:69
  - socio_char_label: same in line 88
  - Adjust the `panel_width - 80` offset to `panel_width - 110` accordingly (same lines)
- [x] Smoke: visually inspect via the game launcher (or take a screenshot) — label should fit without overlap

**Notes:**

### Task 7.3: Update `docs/02_PATTERNS.md` Pattern #28 entry [Simple]
**File:** `docs/02_PATTERNS.md`
**Tests:** N/A

- [x] Add a "Reference consumer: PROJ-299 RaceDescriptionLLMController" line to Pattern #28 (Background Service Call). Brief — a sentence at the end of the section pointing to the controller as the canonical first consumer.

**Notes:**

### Task 7.4: Update `docs/systems/strategy_layer.md` [Simple]
**File:** `docs/systems/strategy_layer.md`
**Tests:** N/A

- [x] Add a brief mention of `race_description_prompt_builder.py` and `race_description_llm_controller.py` to the Services or Race Setup section. ~3-5 lines.

**Notes:**

### Task 7.5: Final full-suite verification [Simple]
**File:** N/A
**Tests:** `python Tools/test_sharded/test_sharded.py`

- [x] Run `python Tools/test_sharded/test_sharded.py`
- [x] Confirm: baseline 15273 + ~56 new ≈ 15329+ passing, 0 failures
- [x] Confirm wall time stays under ~60s
- [x] Document final test count in plan.md Current State

**Notes:**

### Task 7.6: User end-to-end smoke (USER TASK) [Simple]
**File:** N/A
**Tests:** Manual

These items require the user's machine + a DeepSeek API key. Implementation agent leaves UNCHECKED.

- [ ] With `DEEPSEEK_API_KEY` set, launch the game → Race Setup → Description tab → click Generate Bio → confirm description fills in within ~10-30s
- [ ] Click Generate Socio while bio is still running → confirm both run in parallel (status labels both show "Generating…")
- [ ] Click Re-roll Bio after first DONE → confirm bio replaced, socio unaffected
- [ ] Generate Bio + immediately click Cancel → confirm prior text restored
- [ ] (Optional) Manually delay or block network → see 30s dialog, "Keep Waiting" → 90s dialog → timeout popup

**Notes:** Manual smoke deferred to user. All automated tests pass (15328/15328).

---

## Phase Completion Checklist
- [x] All task checkboxes above are checked (except 7.6 which is the user)
- [x] All docs updated
- [x] Full sharded suite green
- [x] Update status at top of this file to `Complete`
- [x] Update `plan.md` phase table row to `Complete` (all 7)
- [x] Update `plan.md` Current State — implementation done, awaiting user verification
- [x] Update projects_index.md status to `Awaiting Verification`
