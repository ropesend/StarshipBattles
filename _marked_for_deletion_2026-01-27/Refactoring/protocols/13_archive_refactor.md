# PROTOCOL 13: Archive Refactor
**Role:** The Archivist (Project Manager)
**Objective:** Formalize the completion of the refactor and archive artifacts.

**Procedure:**
1. **Verification:**
   * Confirm `active_refactor.md` shows ALL phases as [Complete].
   * Confirm NO blocking items in the "Test Triage Table".
   * Run ALL tests one last time. passing = mandatory.

2. **Archive Creation:**
   * Create directory: `Refactoring/archives/YYYY-MM-DD_RefactorName/`.
   * Move the following files into it:
     * `active_refactor.md`
     * `active_phase_log.md` (if exists)
     * `swarm_reports/*.md`
     * `swarm_manifests/*.json` (optional, if specific to this run)
     * `swarm_prompts/*.txt`

3. **Cleanup:**
   * Delete `swarm_reports/*.md` (if not moved).
   * Delete `swarm_prompts/*.txt` (if not moved).

4. **Reset:**
   * Ensure `Refactoring/active_refactor.md` is gone (since it was moved).
   * Ready for next Protocol 10 start.

5. **Notification:**
   * Inform User: "Refactor Archived Successfully."
