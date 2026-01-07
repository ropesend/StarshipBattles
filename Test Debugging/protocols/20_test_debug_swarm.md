# Protocol 20: Test Debug Swarm
**Role:** The Diagnostician (Coordinator)
**Objective:** Identify the cause of a difficult-to-resolve unit test failure.

## 1. Overview
The Test Debug Swarm is triggered when a single agent is unable to solve a failing unit test. It uses a "Wide Search" approach to explore unlikely areas of the codebase.

## 2. Phase 1: The Diagnostician
1. **Analyze Failure:** Read the `pytest` output and the failing test code.
2. **Identify Zones:** Determine 5-10 "Exploration Zones" outside the immediate module under test.
   - *Example Zones:* `conftest.py`, `BaseClass.py`, `data/*.json`, `RegistryManager`, `MockObjects`.
3. **Generate Manifest:** Create `Test Debugging/swarm_manifests/debug_manifest.json`.
4. **Pack Swarm:** Run `python "Test Debugging/scripts/pack_debug_swarm.py" "Test Debugging/swarm_manifests/debug_manifest.json"`.
5. **Wait:** Stop and allow the swarm agents to run.

## 3. Phase 2: The Scouts (Specialists)
Each Scout agent is given a specific zone and a restricted set of files.
- **Goal:** Find evidence or anomalies in their zone.
- **Output:** Save a report to `Test Debugging/swarm_reports/{Role}_Report.md`.

## 4. Phase 3: The Synthesizer
1. **Review Reports:** Read all generated reports.
2. **Determine Signal:** Separate useful clues from "No issues found" reports.
3. **Strategy:** Propose the next investigation step for the main agent.
