# PROTOCOL 10: Swarm Planning
**Role:** The Architect (Coordinator)
**Objective:** Decompose the user's goal into a Phased Engineering Plan.

**Phase 1: The Architect**
1. **Analyze Goal:** Read user input.
2. **Generate Manifest:** Create `Refactoring/swarm_manifests/plan_manifest.json`.
3. **Execute:** `python Refactoring/scripts/pack_swarm.py Refactoring/swarm_manifests/plan_manifest.json`
4. **STOP:** Wait for user to run swarm.

**Phase 2: The Synthesizer**
1. **Trigger:** Reports present in `Refactoring/swarm_reports/`.
2. **Synthesize:** Create `Refactoring/active_refactor.md`.
   * **Migration Map** (The Constitution)
   * **Test Triage Table** (Empty)
   * **Phased Schedule** (Phase 1 detailed, Phase 2+ placeholders)
