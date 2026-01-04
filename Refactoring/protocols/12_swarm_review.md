# PROTOCOL 12: Swarm Review
**Role:** The Auditor
**Objective:** Verify phase completion.

**Phase 1: The Auditor**
1. **Analyze:** Read `Refactoring/active_refactor.md` (Checklist & Triage results).
2. **Generate Manifest:** Create `Refactoring/swarm_manifests/review_manifest.json`.
   * Roles: `Code_Reviewer`, `Plan_Adjuster`.
3. **Execute:** `python Refactoring/scripts/pack_swarm.py Refactoring/swarm_manifests/review_manifest.json`
4. **STOP.**

**Phase 2: The Synthesizer**
1. **Synthesize:** Read `Refactoring/swarm_reports/`.
2. **Decision Point:**
   * **Issues Found?** -> Return to Protocol 11 (Execute fixes).
   * **Phase Complete?** ->
     * **Update Plan:** Mark current phase [Complete].
     * **Next Phase:** **Append** DETAILED IMPLEMENTATION SPECS for the Next Phase (file paths, signatures, etc.).
     * **Do NOT** use placeholders. The plan must be actionable now.
     * **History Preservation:** Do NOT remove completed phases or the original goal.
     * **ALL PHASES DONE?** -> **Proceed to Protocol 13 (Archive).**
