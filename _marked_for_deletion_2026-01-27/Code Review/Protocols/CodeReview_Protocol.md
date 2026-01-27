# Antigravity Code Review Protocol

## 0. Setup
* **Trigger:** User initiates a review for a complex feature or refactor.
* **Directory:** Create a new directory: `Reviews/YYYY-MM-DD_[FeatureName]/`.
* **Goal:** Deep analysis of flaws, inconsistencies, test coverage, and refactor impact.

---

## Phase 1: The Coordinator (Primary Agent)
**Role:** Analyze the high-level diff, identify affected systems, and generate instructions for the swarm.
**Output:** A file named `swarm_instructions.md`.

**Instructions to Coordinator:**
1.  Analyze the provided code changes.
2.  Determine 2-4 distinct "Specialist Perspectives" needed (e.g., Security, Performance, Test Coverage, Architectural Consistency).
3.  **CRITICAL:** For each Specialist, list exactly which files the user must provide to them to give them full context.
4.  Generate specific prompts for each Specialist. Ensure no overlap in responsibilities.

---

## Phase 2: The Swarm (Specialist Agents)
**User Action:** Spin up separate agents as defined in `swarm_instructions.md`. Paste the generated instructions + relevant files.
**Output:** Each agent saves a report as `[Topic]_Report.md` (e.g., `Physics_Report.md`, `Tests_Report.md`).

**Standard Specialist Constraints:**
* Do not summarize unrelated code.
* If suggesting a code fix, provide the actual code snippet in a code block.
* Rate issues by Severity: [Critical], [Major], [Minor], [Nitpick].

---

## Phase 3: Synthesis (Primary Agent)
**User Action:** specificy that the sub-tasks are complete and the reports are in the directory.
**Instruction:** "Review the generated .md files in this directory. Compile a `Final_Review.md`."

**Synthesis Rules:**
1.  **Deduplicate:** If two agents flag the same issue, merge them.
2.  **Preserve Code:** If a Specialist provided a code snippet, include it or link clearly to the specific sub-report.
3.  **Refactor Impact:** dedicated section on how these changes affect the broader system architecture.
4.  **Next Steps:** Create a checklist of action items.