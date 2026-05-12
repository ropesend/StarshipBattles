# BUG-61: Species Setup - Aptitude Range and Cost Curve

## Description

In the Species Setup the Aptitudes should be 1 to 100, base 50, and it should be linear to 50, but exponentially expensive beyond 50

## Priority
Medium

## Status
Awaiting Confirmation

## Work Log

### Fix Applied (2026-02-07)

**Root Cause:** Aptitudes were on a 1-10 scale with base 5 and linear cost. Needed to expand to 1-100 with base 50 and exponential cost above 50.

**Changes:**

1. **`game/strategy/data/race_config.py`**:
   - Changed all aptitude defaults from 5 to 50
   - Changed validation range from 1-10 to 1-100
   - Updated `from_dict` defaults from 5 to 50

2. **`game/strategy/data/race_point_budget.py`**:
   - Changed `APTITUDE_BASE` from 5 to 50
   - Added `_single_aptitude_cost()` method with exponential formula above base
   - Below 50: linear (1 point per step, negative = refund)
   - Above 50: each step costs `max(1, int(2^((v-50)/10)))` cumulatively
   - Cost examples: value 51=1pt, 53=3pt, 55=5pt, 60=11pt, 70=37pt, 80=92pt, 100=440pt

3. **`game/ui/panels/race_aptitudes_panel.py`**:
   - Changed slider range from (1,10) to (1,100)
   - Updated label text to "Aptitudes (1-100, base 50):"
   - Cost display uses new `_single_aptitude_cost()` method

4. **`game/strategy/engine/population_engine.py`**:
   - Changed growth rate formula from `0.005 * aptitude` to `0.0005 * aptitude`
   - Scale: aptitude 1=0.05%, 50=2.5%, 100=5.0% per turn

5. **`game/ui/screens/race_validator.py`**:
   - Changed validation range from 1-10 to 1-100

6. **Tests updated:**
   - `test_race_config.py` - defaults 5->50, validation boundary 10->100
   - `test_race_point_budget.py` - all aptitude values and expected costs updated for 1-100 scale
   - `test_population_engine.py` - growth rate boundaries and aptitude defaults updated
   - `test_race_aptitudes_panel.py` - slider init checks and budget display tests updated
   - `test_race_validator.py` - validation ranges and over-budget test values updated

**Result:** Aptitudes now use 1-100 scale with base 50. Linear cost below 50, exponential cost above 50 that makes extreme values very expensive.

**Tests:** All 6519 tests pass.
