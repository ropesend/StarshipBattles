# Swarm Protocol 01: Refactor Planning
**Objective:** Turn a high-level "Plan" or "Goal" into a detailed, executable Engineering Plan with validated checklists.

## 0. Setup
*   **Trigger:** User provides a `goal.md` or a rough "Implementation Plan".
*   **Target:** `Reviews/YYYY-MM-DD_Plan_[Topic]/`

---

## Phase 1: The Architect (Coordinator)
**Role:** Orchestration ONLY.
**Goal:** Decompose the high-level plan into specific "Planning Vectors" that need detailed expansion.
**Strict Protocol:**
1.  **Analyze:** Read the user's `goal.md`.
2.  **Identify Vectors:** What needs deep thought?
    *   *Dependencies:* (What breaks if we change X?)
    *   *Testing:* (How do we fail-fast?)
    *   *Migration:* (How do we handle old data?)
3.  **EXECUTE:** write `swarm_manifest.json` defining these roles.
4.  **EXECUTE:** run `pack_swarm.py`.
5.  **STOP.**

**Manifesto Structure (Example):**
```json
{
  "context_root": "./",
  "agents": [
    {
      "roles": "Dependency_Analyst",
      "focus": "Identify all files importing `GlobalState` and propose specific refactor patterns for each.",
      "primary_files": ["src/old_state.py", "goal.md"]
    },
    {
      "role": "Test_Strategist",
      "focus": "Design the 'Canary Tests' mentioned in the goal. Provide actual Python code for the tests.",
      "primary_files": ["tests/conftest.py", "goal.md"]
    }
  ]
}
```

---

## Phase 2: The Swarm (Planning Specialists)
**Mode:** Manual Execution (User drags prompts).
**Output:** Markdown files with *Concrete Details*.
*   *Bad Output:* "We should check dependencies."
*   *Good Output:* "File A, B, and C import X. Change them to use Provider Y."

---

## Phase 3: The Synthesizer
**Role:** Compiler.
**Action:**
1.  **Locate Reports:** Use `list_dir` to find all files in the `reports/` directory (sibling to `prompts/`).
2.  **Read Content:** Read all identified reports.
3.  **Synthesize:** Compile `Detailed_Implementation_Plan.md`.
4.  **Required Section:** "Validation Checklist" (A copy-pasteable markdown list for task tracking).
