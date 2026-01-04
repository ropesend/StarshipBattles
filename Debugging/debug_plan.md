# 🐞 Active Debugging Plan

## 1. Context Handoff Summary
*(State of the system for the next agent)*
*System initialized. TDD Workflow active. Queue populated from recent conversation history.*

## 2. Bug Queue
| ID | Date Found | Description | Status | Test File |
| :--- | :--- | :--- | :--- | :--- |
| BUG-07 | 2026-01-03 15:46 | Crash in Weapons Panel (AttributeError) | [Awaiting Confirmation] | `tests/repro_issues/test_bug_07_crash.py` |
| BUG-08 | 2026-01-03 16:00 | Fuel Storage validation fails despite Fuel Tank presence | [In-Progress] | [`tests/repro_issues/test_bug_08_fuel_validation.py`](file:///c:/Dev/Starship%20Battles/tests/repro_issues/test_bug_08_fuel_validation.py) |

| BUG-11 | 2026-01-03 18:27 | Confirm Refit Dialog too small (scrolling required) | [Pending] | [`Debugging/active_bugs/BUG-11.md`](Debugging/active_bugs/BUG-11.md) |
| BUG-12 | 2026-01-03 18:27 | Generator not generating energy (shows 0 instead of 25/s) | [Pending] | [`Debugging/active_bugs/BUG-12.md`](Debugging/active_bugs/BUG-12.md) |

## 3. Current Focus: [BUG-08]
* **Root Cause Hypothesis:** 
    * `ClassRequirementsRule` (vehicle class validation) checks for `FuelStorage` ability, but `Fuel Tank` provides `ResourceStorage(fuel)`. Stats calculator wasn't aliasing the resource storage to the specific name expected by the rule.
* **Attempt Log (CRITICAL):**
   * *[2026-01-03 18:15] BUG-08 FAILED:* QA Rejected. Previous fix (aliasing) insufficient. Fuel Storage still not recognized despite presence of Fuel Tank.
