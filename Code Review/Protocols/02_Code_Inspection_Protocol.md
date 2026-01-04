# Swarm Protocol 02: Code Inspection
**Objective:** Deep analysis of specific code artifacts for bugs, security, and performance.

## 0. Setup
*   **Trigger:** User provides a diff, a specific file, or a pull request.
*   **Target:** `Reviews/YYYY-MM-DD_Review_[Topic]/`

---

## Phase 1: The Architect (Coordinator)
**Role:** Orchestration ONLY.
**Goal:** Assign "Lenses" to look at the code.
**Strict Protocol:**
1.  **Analyze:** Read the code to be reviewed.
2.  **Identify Lenses:**
    *   *Logic:* (Does it do what it says?)
    *   *Safety:* (Null checks, Type safety, Race conditions)
    *   *Performance:* (Loops, O(n), Memory)
3.  **EXECUTE:** write `swarm_manifest.json`.
4.  **EXECUTE:** run `pack_swarm.py`.
5.  **STOP.**

**Manifesto Structure (Example):**
```json
{
  "context_root": "./",
  "agents": [
    {
      "roles": "Safety_Inspector",
      "focus": "Race conditions in the new RegistryManager. Look for basic dictionary operations unprotected by locks.",
      "primary_files": ["game/core/registry.py"]
    },
    {
        "role": "Interface_Critic",
        "focus": "Does the new API match the old one? specific check for 'load_components' signature.",
        "primary_files": ["game/core/registry.py", "game/simulation/components/component.py"]
    }
  ]
}
```

---

## Phase 2: The Swarm (Inspectors)
**Mode:** Manual Execution.
**Output:** `[Lens]_Report.md`.
**Constraint:** Must cite line numbers. Must provide code fixes for bugs.

---

## Phase 3: The Adjudicator
**Role:** Judge.
**Action:**
1.  **Locate Reports:** Use `list_dir` to find all files in the `reports/` directory.
2.  **Read:** Read all reports.
3.  **Filter:** Ignore strict stylistic preferences unless they violate project standards.
4.  **Prioritize:** Blocking Bugs > Safety Issues > Performance > Nitpicks.
5.  **Output:** `Review_Report.md`.
