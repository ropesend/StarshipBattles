# Protocol 10: Manage Refactor Plan

This protocol defines the standard procedures for adding, removing, updating, and reordering projects in the master `refactor_plan.md`.

---

## 1. Add a New Project

**Goal:** Add a new project from `active_projects` to the Master Task List.

### Steps:
1. **Verify Project Existence:**
   - Check that `Projects/active_projects/PROJ-XX/plan.md` exists.
   - Read the plan to get: Title, Total Phases, Current Status.

2. **Locate Insertion Point:**
   - Determine priority relative to existing projects.
   - High priority projects go to the top of the incomplete list.
   - Dependencies must come *before* dependent projects.

3. **Format the Entry:**
   Use this exact template:
   ```markdown
   - [ ] **PROJ-XX: Project Title**
     - **Phases:** N | **Status:** Ready | **Priority:** High
     - **Plan:** [Projects/active_projects/PROJ-XX/plan.md](file:///C:/Dev/Starship%20Battles/Projects/active_projects/PROJ-XX/plan.md)
     - **Audit:** Not Started | **Cycles:** 0/5
     - **Dependencies:** None
   
   ---
   ```

4. **Insert:**
   - Add the block at the chosen location.
   - Ensure `---` separators are maintained between projects.

---

## 2. Remove or Archive a Project

**Goal:** Remove a project that is cancelled, deferred, or erroneously added.

### Steps:
1. **Confirm Intent:**
   - **Delete:** For projects that never started or are duplicates.
   - **Archive (Comment out):** For projects deferred to a later date.
   - **Mark Skipped:** Change `[ ]` to `[~]` for projects skipped in the loop.

2. **Execute:**
   - **To Delete:** Remove the entire bullet point block and the trailing `---`.
   - **To Archive:** Wrap the block in `<!-- -->`.
   - **To Skip:** Change `[ ]` to `[~]`.

---

## 3. Update Project Details

**Goal:** Sync the master plan with changes in the project's individual plan.

### Steps:
1. **Read Source:** Read `Projects/active_projects/PROJ-XX/plan.md`.
2. **Update Fields:**
   - **Phases:** Update count if phases were added/removed.
   - **Status:** Update (e.g., Planning -> Ready).
   - **Priority:** Update if changed.
   - **Dependencies:** Update if new dependencies discovered.

---

## 4. Reorder Projects

**Goal:** Change the execution order of the automated loop.

### Steps:
1. **Review Dependencies:**
   - Ensure no project is moved *above* its dependencies.
   - `PROJ-43` (Layer Violations) is often a dependency for others.

2. **Move Block:**
   - Cut the entire block (bullet point through to the `---` separator).
   - Paste in the new location.

3. **Verify:**
   - Check that the list structure is intact.
   - Check that the first `[ ]` is truly the project you want to run next.

---

## 5. Verification Checklist

After any change, verify:
- [ ] Markdown syntax is valid (checkboxes render correctly).
- [ ] File paths in links are absolute/valid.
- [ ] Separators `---` are present between each project.
- [ ] No "orphan" text outside of project blocks.
- [ ] The "Next Project" (first empty checkbox) is the intended one.
