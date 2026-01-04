# 🐞 Active Debugging Plan

## 1. Context Handoff Summary
*(State of the system for the next agent)*
*System initialized. TDD Workflow active. Queue populated from recent conversation history.*

## 2. Bug Queue
| ID | Date Found | Description | Status | Test File |
| :--- | :--- | :--- | :--- | :--- |


| BUG-05 | 2026-01-03 15:24 | Stats Panel: Missing detailed Logistics (Max Cap, Gen/Use Rates, Endurance) for all resources | [Awaiting Confirmation] | tests/repro_issues/test_bug_05_logistics.py |
| BUG-06 | 2026-01-03 15:46 | Combat Propulsion Validation Error | [In-Progress] | TBD |
| BUG-07 | 2026-01-03 15:46 | Crash in Weapons Panel (AttributeError) | [Awaiting Confirmation] | `tests/repro_issues/test_bug_07_crash.py` |
| BUG-08 | 2026-01-03 16:00 | Fuel Storage validation fails despite Fuel Tank presence | [Awaiting Confirmation] | [`tests/repro_issues/test_bug_08_fuel_validation.py`](file:///c:/Dev/Starship%20Battles/tests/repro_issues/test_bug_08_fuel_validation.py) |
| BUG-09 | 2026-01-03 16:39 | Fuel Endurance Infinite Calculation Error | [Awaiting Confirmation] | [`Debugging/active_bugs/BUG-09.md`](file:///c:/Dev/Starship%20Battles/Debugging/active_bugs/BUG-09.md) |
| BUG-10 | 2026-01-03 16:39 | Ship Stats not updating for Ammo/Ordinance | [In-Progress] | [`Debugging/active_bugs/BUG-10.md`](file:///c:/Dev/Starship%20Battles/Debugging/active_bugs/BUG-10.md) |

## 3. Current Focus: [BUG-08]
* **Root Cause Hypothesis:** 
    * `ClassRequirementsRule` (vehicle class validation) checks for `FuelStorage` ability, but `Fuel Tank` provides `ResourceStorage(fuel)`. Stats calculator wasn't aliasing the resource storage to the specific name expected by the rule.
* **Attempt Log (CRITICAL):**
   * *[2026-01-03 18:15] BUG-08 Solved:* Fixed by adding logic to `ShipStatsCalculator.calculate_ability_totals` to alias `ResourceStorage` with `resource_type='fuel'` to `FuelStorage`. Verified with `test_bug_08_fuel_validation.py`.
