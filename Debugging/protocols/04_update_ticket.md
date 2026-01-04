# PROTOCOL 04: Update Ticket Context
**Role:** Data Entry Clerk (Non-Technical)

**Goal:** Append new text to an existing file.

**CRITICAL CONSTRAINTS:**
1.  **DO NOT** analyze the content of the update.
2.  **DO NOT** attempt to fix the bug.
3.  **DO NOT** write any code or tests.
4.  **DO NOT** change the status of the bug.
5.  Your ONLY output should be a confirmation that the file was modified.

**Procedure:**
1.  **Target File:** Locate `Debugging/active_bugs/[BUG-ID].md`.
2.  **Append:** Add the following formatted block to the end of the "Description" section:

    ```markdown
    ---
    ### 📝 User Update [YYYY-MM-DD HH:MM]
    [Insert User's Text/Images Verbatim]
    ---
    ```

3.  **Notification:**
    * If the bug is currently assigned to an agent, you may simply note "Context updated" in the Work Log.
    * Do not evaluate the update.

4.  **Termination:** Stop immediately after saving the file.