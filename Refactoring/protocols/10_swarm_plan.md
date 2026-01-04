# PROTOCOL 10: Swarm Planning
**Role:** The Architect (Coordinator)
**Objective:** Decompose the user's goal into a Phased Engineering Plan.

> [!IMPORTANT]
> **Planning Role Only:** This agent is responsible for STRATEGIC PLANNING.
> You must **NOT** write implementation code or modify project files directly (other than the plan itself).

**Phase 1: The Architect**
1. **Analyze Goal:** Read user input and goal.
2. **Generate Manifest:** Create `Refactoring/swarm_manifests/plan_manifest.json`.
3. **Execute:** `python Refactoring/scripts/pack_swarm.py Refactoring/swarm_manifests/plan_manifest.json`
4. **STOP:** Wait for user (or swarm orchestrator) to run the swarm agents.

**Phase 2: The Synthesizer**
1. **Trigger:** Reports present in `Refactoring/swarm_reports/`.
2. **Initialize Context:**
   * check if `Refactoring/active_refactor.md` exists.
   * If NOT, create it with a standard header (Goal, Status, Start Date).
   * **NOTE:** This file MUST remain in `Refactoring/` as the single source of truth.
3. **Synthesize:** Update `Refactoring/active_refactor.md`.
   * **Migration Map** (The Constitution)
   * **Test Triage Table** (Empty)
   * **Phased Schedule** (Phase 1 detailed, Phase 2+ placeholders)
4. **Handoff:** Request Protocol 11 (Execution).
