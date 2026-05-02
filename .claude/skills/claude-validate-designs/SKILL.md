---
name: claude-validate-designs
description: Validate ship and complex designs against the component registry for crew housing, life support, mass budgets, and mass consistency
---

# Validate Designs

Run the design validator against a set of design JSON files and report results.

## Arguments

The optional argument specifies which designs to validate:

- **No argument**: Validates all quickstart designs in `data/designs/`
- **Directory path**: Validates all `*.json` files in the given directory
- **`all`**: Validates quickstart fixtures AND all save game designs found under `output/saves/`

## Steps

1. **Run the validator script:**

   ```bash
   python Tools/validate_designs/validate_designs.py <directory>
   ```

   If the argument is `all`, run it once for quickstart fixtures and once for each `designs/empire_*/` directory found under `output/saves/`.

2. **Categorize results** into three groups:

   - **Critical errors**: Crew housing shortfall, life support shortfall, component missing from registry. These prevent the design from functioning in-game (e.g., won't enter build queue).
   - **Mass mismatches**: Calculated mass differs from `expected_stats.mass`. This may indicate stale expected_stats after a formula change, or a genuine design error. If ALL designs show mass mismatch, it's likely a systemic `expected_stats` staleness issue, not individual design bugs.
   - **Clean designs**: No errors.

3. **Present a summary table:**

   | Design | Status | Issues |
   |--------|--------|--------|
   | QS Escort | PASS | - |
   | QS Complex | FAIL | Crew: -60, Life support: -45 |

4. **If critical errors exist**, list the specific designs that need fixing and what each one needs (e.g., "needs 60 more crew housing, 45 more life support").

5. **If mass mismatches are universal**, note this as a systemic issue and recommend updating `expected_stats` in bulk rather than fixing individual designs. Offer to run the stats recalculation.

6. **Do not automatically fix designs.** Report findings and ask the user what they want to do about each category of issue. Fixes to designs require TDD workflow (tests first, then implementation).

## Notes

- The validator script uses `DesignValidator` from `game/strategy/services/design_validator.py`
- Mass calculation uses `ShipStatsCalculator` from `game/strategy/services/ship_stats_calculator.py`
- Warnings about formula abilities (EmissiveArmor, WarpJump, etc.) using `=expression` syntax are expected at registry load time and can be ignored
- The `QualityImprovement` scope 'system' warnings indicate components using an unsupported ability scope -- these are worth investigating separately
