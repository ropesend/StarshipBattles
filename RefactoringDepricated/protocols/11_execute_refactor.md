### 📄 Protocol 11: Execute Refactor (`11_execute_refactor.md`)

This is the most important file. It explicitly overrides the agent's natural desire to "fix" code by reverting changes.

```markdown
# PROTOCOL 11: Execute Refactor
**Role:** Senior Software Engineer (Refactoring Specialist)

**CONTEXT WARNING:**
You are working inside an active Refactor. Standard TDD rules are suspended.
**The `active_refactor.md` file is the Supreme Authority.**

**The "Context Loss" Trap:**
Do not fall into the trap of seeing a failing test and "fixing" it by reverting the architecture to the old way.

**Procedure:**
1.  **Read the Constitution:**
    * Read `Refactoring/active_refactor.md` immediately.
    * Identify the **Migration Map**.

2.  **Analyze Failing Tests:**
    * If a test fails, ask: *Does this test expect the OLD behavior?*
    * **YES:** Update or Delete the test. **DO NOT change the code to match the test.**
    * **NO:** Then it is a real bug. Fix the code.

3.  **Update the Context:**
    * Before your turn ends, you MUST append a status update to `Refactoring/active_refactor.md`.
    * *Format:* "[Time] Modified `ship.py`. Updated 3 tests. 4 tests still failing (Type: Old Logic)."

4.  **Handoff Trigger:**
    * If you cannot finish, your log entry in Step 3 serves as the "Save Point" for the next agent.