# PROTOCOL 02: Bug Resolution (TDD)
**Role:** Senior Software Engineer

**CRITICAL CONSTRAINT:** You do NOT have the authority to mark a bug as [Solved]. You do NOT have the authority to move files to `archived_tickets/`. Your authority ends at [Awaiting Confirmation] or [Needs Clarification].

**ANTI-REVERSION RULES (applies to ALL phases):**
- NEVER undo a recent refactor to fix a bug. Fix forward.
- If a bug was CAUSED by a refactor, the fix must work WITHIN the new architecture.
- If you cannot find a forward-fix, escalate to `[Needs Clarification]`.
- Check `git log` on affected files. If a PROJ-XX commit touched them in the last 60 days, read that project's design docs before coding anything.
- A fix that increases tech debt requires explicit justification in the Work Log.
- Refer to CLAUDE.md principles: "When a new system replaces an old one, ERADICATE the old system completely." Your fix must not resurrect eradicated code.

**Selection Logic:**
* **If User Specified a Bug ID:** Load that specific ticket.
* **If No ID Specified:** Read `Debugging/debug_plan.md`, pick the top "Pending" item.

**Execution Steps:**

1.  **Context Loading:** * Read `Debugging/active_bugs/[BUG-ID].md`.
    * Update `Debugging/debug_plan.md`: Set status to `[In-Progress]`.

2.  **Phase 0: Deep Review & Architectural Context:**

    **Step 0a: Architectural Context Gathering (MANDATORY)**

    Before assessing fix approach, gather context from these sources:

    1. **Git History Check:** Run `git log --oneline -20 -- <affected_files>` for each file implicated in the bug. Note any commits in the last 60 days that are refactors, renames, or part of a PROJ-XX project.
    2. **Active Project Check:** Scan `Projects/active_projects/` for any PROJ-XX whose `plan.md` or phase checklists reference the affected files or modules. If found, read that project's `design.md` to understand design intent.
    3. **Architecture Doc Check:** Review `CLAUDE.md` (Key Conventions, Architecture Principles) and `docs/architecture/ARCHITECTURE.md` (Layer Structure, Dependency Rules) for any principles relevant to the affected code area.
    4. **Document Findings:** Append to `## Work Log`:
       ```
       ### Phase 0: Architectural Context
       **Recent refactors:** [list relevant commits or "None found"]
       **Active projects touching this code:** [PROJ-XX or "None"]
       **Relevant architecture rules:** [brief list or "None specific"]
       ```

    **Step 0b: Ambiguity & Conflict Assessment**

    * **Assess** whether the correct architectural fix is clearcut or ambiguous.
    * **ANTI-REVERSION CHECK:** If git history shows the affected code was recently refactored (within last 60 days) as part of a project or intentional redesign, the fix MUST NOT revert that refactor. Instead:
      - Understand WHY the refactor was done (read the project plan/design docs)
      - Fix FORWARD: find a solution that preserves the refactored architecture
      - If no forward-fix is apparent, escalate to `[Needs Clarification]`
    * **Decision gate:**
      * **If clearcut AND no architectural conflicts:** Proceed to Phase 1 (Reproduction).
      * **If ambiguous OR fix would conflict with recent refactors:**
        1. Add a `## Questions for User` section to `active_bugs/[BUG-ID].md` with specific questions about the intended behavior or architectural direction.
        2. In the `## Work Log`, note what was reviewed and why escalation is needed.
        3. Update `Debugging/debug_plan.md`: Set status to `[Needs Clarification]`.
        4. **STOP.** Do not attempt a fix. Inform the user: "Bug requires clarification before a fix can be attempted. Questions have been posted in the ticket."

3.  **Phase 1: Reproduction (Red):**
    * Create a test case that fails.
    * Update `active_bugs/[BUG-ID].md` `## Work Log` with the failing test output.

4.  **Phase 2: The Fix (Green):**
    * Modify code to pass the test.
    * Run regression tests to ensure no breaks.

5.  **Phase 2.5: Post-Fix Integrity Check (MANDATORY GATE):**

    Before documenting, verify the fix maintains architectural integrity:

    1. **Reversion Check:** Run `git diff HEAD` and compare against the Phase 0 git history findings. Does the diff UNDO any recent refactor commits? Specifically:
       - Does it re-introduce code that was deliberately deleted?
       - Does it restore old API signatures that were intentionally changed?
       - Does it add backward-compatibility shims or fallback paths?
       If YES to any: **STOP. Do not proceed.** Set status to `[Needs Clarification]` with explanation: "Proposed fix would revert [commit hash / PROJ-XX change]. Needs architectural guidance."

    2. **Layer Boundary Check:** Does the fix introduce any forbidden dependency? (e.g., Core importing from Strategy, Simulation importing from UI) If YES: Rework the fix to respect layer boundaries.

    3. **Convention Check:** Does the fix follow CLAUDE.md conventions?
       - Proper refactor over quick fix?
       - Root cause fix over workaround?
       - No magic numbers, no broad exception catches?
       If NO: Rework the fix before proceeding.

    4. **Tech Debt Assessment:** Does this fix reduce, maintain, or increase tech debt? A fix that increases tech debt requires justification documented in the Work Log. Prefer fixes that actively reduce tech debt.

    * **If all checks pass:** Proceed to Phase 3 (Documentation).
    * **If reversion detected:** Set `[Needs Clarification]`, document the conflict, **STOP**.
    * **If layer/convention issues found:** Rework fix, re-run tests, then re-check.

6.  **Phase 3: Documentation:**
    * Append your technical approach to `active_bugs/[BUG-ID].md` `## Work Log`.
    * State clearly which files were modified.

7.  **Phase 4: The Stop Sign (Gatekeeper):**
    * **Update Dashboard:** In `Debugging/debug_plan.md`, change status to `[Awaiting Confirmation]`.
    * **Action:** STOP. Do not update `solved_bugs.md`. Do not move the file.
    * **Output:** Inform the user: "Bug is fixed locally and passing tests. Status set to Awaiting Confirmation. Please Verify."

**The Handoff Rule:**
If you run out of context or get stuck, write a summary in the Work Log and ask for a restart.