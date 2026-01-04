# 🐞 Active Debugging Plan

## 1. Context Handoff Summary
*(State of the system for the next agent)*
*System initialized. TDD Workflow active. Queue populated from recent conversation history.*

## 2. Bug Queue
| ID | Date Found | Description | Status | Test File |
| :--- | :--- | :--- | :--- | :--- |


| BUG-04 | 2026-01-03 22:00 | Stats Panel: Initial Resource Display is "--". | [In-Progress] | `tests/repro_issues/test_bug_04_display.py` |
| BUG-05 | 2026-01-03 14:27 | Stats Panel: Missing detailed Logistics (Max Cap, Gen/Use Rates, Endurance) for all resources. | [Pending] | TBD |
| BUG-06 | 2026-01-03 15:46 | Combat Propulsion Validation Error | [Pending] | TBD |
| BUG-07 | 2026-01-03 15:46 | Crash in Weapons Panel (AttributeError) | [Pending] | TBD |
| BUG-08 | 2026-01-03 16:00 | Fuel Storage validation fails despite Fuel Tank presence | [Pending] | [`Debugging/active_bugs/BUG-08.md`](file:///c:/Dev/Starship%20Battles/Debugging/active_bugs/BUG-08.md) |

## 3. Current Focus: [BUG-02]
* **Root Cause Hypothesis:** 
    * `WeaponsReport` UI element likely accesses static attributes or doesn't have logic to calculate derived stats for Seekers (speed/endurance/turning) vs beams/projectiles.
* **Attempt Log (CRITICAL):**
   * *[2026-01-03 14:26] BUG-01 Solved:* Fixed circular import, list handling in `ship_stats.py`, and missing modifier keys in `modifiers.py`. Verified with `test_bug_01_crew_delay.py`.
