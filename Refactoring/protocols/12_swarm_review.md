# PROTOCOL 12: Swarm Review
**Role:** The Auditor
**Objective:** Verify phase completion.

**Phase 1: The Auditor**
1. **Analyze:** Read `active_refactor.md` (Checklist & Triage).
2. **Generate Manifest:** Create `Refactoring/swarm_manifests/review_manifest.json`.
   * Roles: `Code_Reviewer`, `Plan_Adjuster`.
3. **Execute:** `python Refactoring/scripts/pack_swarm.py Refactoring/swarm_manifests/review_manifest.json`
4. **STOP.**

**Phase 2: The Synthesizer**
1. **Synthesize:** Read `Refactoring/swarm_reports/`.
2. **Update Master Plan:**
   * Mark Phase [Complete].
   * Detail Next Phase.
   * Confirm Deferrals.
