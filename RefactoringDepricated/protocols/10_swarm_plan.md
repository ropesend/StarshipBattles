# PROTOCOL 10: Start Refactor
**Role:** System Architect

**Goal:** Initialize a new refactoring campaign and define the "Migration Map" to prevent future agents from getting confused.

**Procedure:**
1.  **Safety Check:** Check if `Refactoring/active_refactor.md` already exists.
    * *If yes:* STOP. Tell the user: "A refactor is already in progress. Please finish or archive it first."
    * *If no:* Proceed.

2.  **Create Plan:** Create `Refactoring/active_refactor.md` using the template below.
    * **Crucial:** You must fill out the **Migration Map** based on the user's prompt. This is what prevents the "Context Loss Loop."

**Template for `active_refactor.md`:**
```markdown
# Refactor: [Title]
**Start Date:** [YYYY-MM-DD]

## 1. High-Level Goal
* [One sentence summary of what we are changing and why]

## 2. The Migration Map (The Constitution)
*Future Agents: If a test fails, check this table. If the test contradicts this table, the TEST is wrong, not the code.*

| Old Component/Logic | New Component/Logic | Instruction |
| :--- | :--- | :--- |
| e.g. `Inventory.add()` | `Cargo.load()` | Update tests to use `Cargo` |
| e.g. `Fuel.weight` | *Deleted* | Delete tests checking fuel weight |

## 3. Work Log
* [Start] Plan initialized.