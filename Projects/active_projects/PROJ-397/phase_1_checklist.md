# Phase 1: CRITICAL — reclaim 4 BattleScreen Combat Lab dead vars (F-01)

**Status:** Not Started
**Objective:** Close the CRITICAL finding F-01 from the PROJ-393 OpenCode review. PROJ-393 deferred LEG-03-023 claiming "actively used"; the review proved 4 of 6 vars are dead code.

---

## Tasks

### Task 1.1: Delete dead Combat Lab instance vars
**File:** `game/ui/screens/battle_screen.py:117-125`
**Tests:** `pytest tests/ -k "battle_screen" -v`

- [ ] Delete the 5 dead vars: `test_mode`, `test_scenario`, `test_tick_count`, `test_completed`, `headless_start_time`
- [ ] Keep `headless_mode` (set via `:157` from `config.headless`; read at `:302`, `run_loop.py:216` — genuinely active)
- [ ] Delete the `# NOQA: legacy-retained` comment block above them (no longer needed)

### Task 1.2: Fix dead branch in `is_battle_over()`
**File:** `game/ui/screens/battle_screen.py:487-492`
**Tests:** `pytest tests/ -k "battle_screen and (is_battle_over or end)"`

- [ ] Remove the `if self.test_mode:` branch at line 490 (dead)
- [ ] The live detection `self._battle_service.is_battle_over()` at line 492 becomes the only path

### Task 1.3: Fix dead branch in `print_headless_summary()`
**File:** `game/ui/screens/battle_screen.py:677-687`
**Tests:** `pytest tests/ -k "headless"`

- [ ] Remove the `if self.test_mode:` block (always None per F-01 analysis)
- [ ] Verify `headless_mode` summary path is intact

### Task 1.4: Delete dead result-capture in test_lab
**File:** `game/ui/screens/test_lab/screen.py:334-356`
**Tests:** `pytest tests/ -k "test_lab"`

- [ ] Delete the `if scenario := getattr(battle_screen, 'test_scenario', None):` block (always None — `test_scenario` is dead)

### Task 1.5: Verify
**Tests:** `pytest tests/ -k "battle_screen or test_lab" --testmon`

- [ ] Focused test passes
- [ ] `grep -rn "test_mode\|test_scenario\|test_tick_count\|test_completed\|headless_start_time" game/ tests/ combat_lab/` returns ZERO production hits

---

## Phase Completion Checklist
- [ ] All 5 dead vars deleted from `battle_screen.py`
- [ ] All dead branches removed
- [ ] Update plan.md phase table row to `Complete`

_Source review: `Reviews/results/2026-05-09_002247_code_proj-393-test-injection-legacy-fallbacks-comment-c_req-req_20260509_002246_bca19e/`, finding F-01_
