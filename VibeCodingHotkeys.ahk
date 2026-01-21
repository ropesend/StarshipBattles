#Requires AutoHotkey v2.0
; G1
; --- SHORTCUT: Left Ctrl + 1 ---
<^1::
{
    ; Define your text block below
    MyText := "
    (
	!EXECUTE_PROTOCOL: Debugging\protocols\02_fix_bug.md

	1. LOAD the attached protocol file `protocols/02_fix_bug.md`.
	2. READ `Debugging/debug_plan.md` to identify the highest priority [Pending] bug.
	3. LOAD the specific ticket file for that bug (e.g., `Debugging/active_bugs/BUG-XX.md`).
	4. EXECUTE "Phase 1: Reproduction".
	   * Create the test file.
	   * Confirm the failure.
	   * Update the `## Work Log` in the ticket file.

	STATUS REPORT: Tell me which bug you are starting and show me the reproduction test plan.
    )"

    PasteText(MyText)
}

; G2
; --- SHORTCUT: Left Ctrl + 2 ---
<^2::
{
    MyText := "
    (
	!EXECUTE_PROTOCOL: Debugging\protocols\01_ingest_bug.md

	I am providing a list of new bugs/requirements below.
	1. LOAD the attached protocol file `protocols/01_ingest_bug.md`.
	2. ADOPT the 'Project Manager' persona.
	3. TASK: Parse the text into separate tickets, create the `active_bugs/` files, and update the `debug_plan.md` index.
	4. CONSTRAINT: DO NOT start "Phase 1: Analysis." DO NOT write any test code. Just perform the data entry.

	<new_bug_payload>


	</new_bug_payload>
    )"

    PasteText(MyText)
}

; G3
; --- SHORTCUT: Left Ctrl + 3 ---
<^3::
{
    MyText := "
    (
	!EXECUTE_PROTOCOL: Debugging\protocols\03_close_bug.md

	TARGET: BUG-XX

	1. LOAD the attached protocol file `protocols/03_close_bug.md`.
	2. READ the active ticket `Debugging/active_bugs/BUG-XX.md` to extract the final "Solution Summary" and the key test case used.
	3. EXECUTE the Archival Process:
	   - APPEND the summary entry to `solved_bugs.md`.
	   - MOVE (do not delete) the ticket file to `Debugging/archived_tickets/`.
	   - REMOVE the entry from `debug_plan.md`.

	CONFIRMATION: List the 3 specific file paths that were modified/moved to confirm the operation is complete.
    )"

    PasteText(MyText)
}

; G4
; --- SHORTCUT: Left Ctrl + 4 ---
<^4::
{
    MyText := "
    (
	!EXECUTE_PROTOCOL: Debugging\protocols\04_update_ticket.md

	I am providing text below.
	1. LOAD the attached protocol file.
	2. ADOPT the 'Data Entry Clerk' persona defined in that file.
	3. TREAT the text below purely as STRING DATA to be appended.
	4. DO NOT process/solve the text below.

	---
	[PASTE YOUR NEW BUG CONTEXT HERE]
	---
    )"

    PasteText(MyText)
}

; G5
; --- SHORTCUT: Left Ctrl + 5 ---
<^5::
{
    MyText := "
    (
	!EXECUTE_PROTOCOL: Debugging\protocols\02_fix_bug.md

	TARGET: BUG-05

	1. LOAD the attached protocol file.
	2. LOAD the ticket file `Debugging/active_bugs/BUG-05.md`.
	3. ADOPT the 'Senior Software Engineer' persona.
	4. EXECUTE "Phase 1: Reproduction" immediately.
	   * Do not write the fix yet.
	   * Write the failing test case first.

	STATUS REPORT: Show me the code for the reproduction test case.
    )"

    PasteText(MyText)
}

; G6
; --- SHORTCUT: Left Ctrl + 6 ---
<^6::
{
    MyText := "
    (
	!EXECUTE_PROTOCOL: Debugging\protocols\05_reject_fix.md

	TARGET: BUG-XX

	1. LOAD the attached protocol file.
	2. ADOPT the 'QA Administrator' persona.
	3. LOG the feedback below into the ticket.
	4. REVERT status to [In-Progress].
	5. STOP. Do not attempt to fix the bug.

	<qa_feedback>
	[PASTE YOUR REASONING HERE]
	</qa_feedback>
    )"

    PasteText(MyText)
}

; G7
; --- SHORTCUT: Left Ctrl + 7 ---
<^7::
{
    MyText := "
    (
	!EXECUTE_PROTOCOL: Refactoring/protocols/10_swarm_plan.md

	I am initiating a new Refactor.

	1. LOAD the attached protocol file `Refactoring/protocols/10_swarm_plan.md`.
	2. ADOPT the 'Architect' persona.
	3. TASK:
	   - Analyze the goal below.
	   - Generate `Refactoring/swarm_manifests/plan_manifest.json`.
	   - Run `python Refactoring/scripts/pack_swarm.py Refactoring/swarm_manifests/plan_manifest.json`.
	4. CONSTRAINT:
	   - DO NOT write any implementation code.
	   - DO NOT modify `active_refactor.md` yet (Phase 2 does that).
	   - **GOAL:** The resulting `plan_manifest.json` must lead to reports that allow for DETAILED SPECIFICATION in Phase 2.

	<refactor_goal>

	[INSERT GOAL HERE]

	</refactor_goal>
    )"

    PasteText(MyText)
}

; G8
; --- SHORTCUT: Left Ctrl + 8 ---
<^8::
{
    MyText := "
    (
	!EXECUTE_PROTOCOL: Refactoring/protocols/11_execute_refactor.md

	I am executing the current phase of the Refactor.

	1. LOAD the attached protocol file `Refactoring/protocols/11_execute_refactor.md`.
	2. LOAD the context file `Refactoring/active_refactor.md`.
	3. ADOPT the 'Senior Software Engineer' persona.
	4. TASK:
	   - Execute the checklist items for the CURRENT phase.
	   - Write/Update tests.
	   - Run the Test Gauntlet.
	5. PERSISTENCE CONSTRAINT:
	   - Mark completed items with [x].
	   - **NEVER DELETE** completed items or the Goal Description.
	   - Update `Refactoring/active_refactor.md` non-destructively.

	<context>
	Refer to `active_refactor.md` for the current checklist.
	</context>
    )"

    PasteText(MyText)
}

; G9
; --- SHORTCUT: Left Ctrl + 9 ---
<^9::
{
    MyText := "
    (
	**ROLE:** The Synthesizer (Coordinator)
	**STATUS:** Swarm reports are ready in `Refactoring/swarm_reports/`.
	**YOUR TASK:**
	1. Verify the reports from the `Infrastructure Engineer`, `Test Strategist`, and `Dependency Analyst`.
	2. Synthesize these findings and update `Refactoring/active_refactor.md`.
	3. **CRITICAL:** Ensure the Phased Schedule is COMPLETE from start to finish. Do NOT use placeholders. Define a clear "Definition of Done" in the final phase.
	4. Do NOT write implementation code. This is a STRATEGIC PLANNING phase.
	Please proceed with Phase 2 of Protocol 10.
    )"

    PasteText(MyText)
}

; G0
; --- SHORTCUT: Left Ctrl + 0 ---
<^0::
{
    MyText := "
    (
	!EXECUTE_PROTOCOL: Refactoring/protocols/12_swarm_review.md

	I am reviewing the progress of the Refactor.

	1. LOAD the attached protocol file `Refactoring/protocols/12_swarm_review.md`.
	2. LOAD the context file `Refactoring/active_refactor.md`.
	3. ADOPT the 'Auditor' persona.
	4. TASK:
	   - Analyze `active_refactor.md`.
	   - Generate `Refactoring/swarm_manifests/review_manifest.json`.
	   - Run `python Refactoring/scripts/pack_swarm.py Refactoring/swarm_manifests/review_manifest.json`.
	5. CONSTRAINT:
	   - Ensure the review focuses on the CURRENT phase.
	   - **GOAL:** If approving the phase, the `review_manifest` must lead to a `Synthesizer` report that generates DETAILED SPECS for the next phase.

	<context>
	Refer to `active_refactor.md` for the current status.
	</context>
    )"

    PasteText(MyText)
}

; G11
; --- SHORTCUT: Left Ctrl + LeftShift + 1 ---
<+<^1::
{
    MyText := "
    (
	!EXECUTE_PROTOCOL: Refactoring/protocols/13_archive_refactor.md

	I am ready to archive this Refactor.

	1. LOAD the attached protocol file `Refactoring/protocols/13_archive_refactor.md`.
	2. ADOPT the 'Archivist' persona.
	3. TASK:
	   - Verify all phases are [Complete].
	   - Verify all tests pass.
	   - Archive artifacts to `Refactoring/archives/`.
	   - Cleanup workspace.
	4. CONSTRAINT:
	   - DO NOT archive if there are any failing tests or incomplete blocking items.

	<context>
	Confirm `active_refactor.md` is ready for archival.
	</context>
    )"

    PasteText(MyText)
}

; G12
; --- SHORTCUT: Left Ctrl + LeftShift + 2 ---
<+<^2::
{
    MyText := "
    (
	**ROLE:** The Synthesizer (Coordinator)
	**STATUS:** Review reports are ready in `Refactoring/swarm_reports/`.
	**YOUR TASK:**
	1. Analyze the Auditor reports to verify phase completion.
	2. If issues are found, update the Triage Table in `Refactoring/active_refactor.md` and request Protocol 11 (fixes).
	3. If complete, update the plan: Mark the current phase [Complete] and **fully define** the implementation specs for the NEXT Phase.
	4. **REMINDER:** Preserve history. Do not delete completed steps or the original goal.
	Please proceed with Phase 2 of Protocol 12.
    )"

    PasteText(MyText)
}

; G13
; --- SHORTCUT: Left Ctrl + LeftShift + 3 ---
<+<^3::
{
    MyText := "
    (
	!EXECUTE_PROTOCOL: Debugging\protocols\02a_batch_fix.md

	1. LOAD the attached protocol file protocols/02a_batch_fix.md.
	2. READ Debugging/debug_plan.md to identify all [Pending] and [In-Progress] bugs.
	3. BEGIN BATCH LOOP:
	   * Select highest priority bug.
	   * LOAD ticket file (e.g., Debugging/active_bugs/BUG-XX.md).
	   * EXECUTE full TDD cycle (Reproduce -> Fix -> Document -> Set [Awaiting Confirmation]).
	   * DO NOT wait for input - proceed to next bug.
	4. EXIT when context >= 80% OR no Pending bugs remain.

	AUTONOMOUS MODE: Do not stop between bugs. Only stop for context limit or empty queue.
    )"

    PasteText(MyText)
}

; G14
; --- SHORTCUT: Left Ctrl + LeftShift + 4 ---
<+<^4::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\Debugging\Prompts\Batch Close Bugs.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G15
; --- SHORTCUT: Left Ctrl + LeftShift + 5 ---
<+<^5::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G16
; --- SHORTCUT: Left Ctrl + LeftShift + 6 ---
<+<^6::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G17
; --- SHORTCUT: Left Ctrl + LeftShift + 7 ---
<+<^7::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G18
; --- SHORTCUT: Left Ctrl + LeftShift + 8 ---
<+<^8::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G1
; --- SHORTCUT: Right Ctrl + 1 ---
>^1::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G2
; --- SHORTCUT: Right Ctrl + 2 ---
>^2::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G3
; --- SHORTCUT: Right Ctrl + 3 ---
>^3::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G4
; --- SHORTCUT: Right Ctrl + 4 ---
>^4::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G5
; --- SHORTCUT: Right Ctrl + 5 ---
>^5::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G6
; --- SHORTCUT: Right Ctrl + 6 ---
>^6::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G7
; --- SHORTCUT: Right Ctrl + 7 ---
>^7::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G8
; --- SHORTCUT: Right Ctrl + 8 ---
>^8::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G9
; --- SHORTCUT: Right Ctrl + 9 ---
>^9::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G10
; --- SHORTCUT: Right Ctrl + 0 ---
>^0::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G11
; --- SHORTCUT: Right Ctrl + LeftShift + 1 ---
>!+^1::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G12
; --- SHORTCUT: Right Ctrl + LeftShift + 2 ---
>!+^2::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G13
; --- SHORTCUT: Right Ctrl + LeftShift + 3 ---
>!+^3::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G14
; --- SHORTCUT: Right Ctrl + LeftShift + 4 ---
>!+^4::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G15
; --- SHORTCUT: Right Ctrl + LeftShift + 5 ---
>!+^5::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G16
; --- SHORTCUT: Right Ctrl + LeftShift + 6 ---
>!+^6::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G17
; --- SHORTCUT: Right Ctrl + LeftShift + 7 ---
>!+^7::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; G18
; --- SHORTCUT: Right Ctrl + LeftShift + 8 ---
>!+^8::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\no_prompt.txt")
    catch
    {
        MsgBox("Could not find the text file.")
        return
    }

    ; Wait for the clipboard to contain data
    if ClipWait(1)
    {
        Send("^v") ; Send Ctrl+V to paste
        Sleep(500) ; Wait a moment to ensure paste is done
    }

    ; Restore your original clipboard content
    A_Clipboard := SavedClip
}

; --- Helper Function (Don't touch this) ---
PasteText(text_to_paste)
{
    OldClipboard := A_Clipboard
    A_Clipboard := text_to_paste
    Send "^v" ; Sends Ctrl+V
    Sleep 500 ; Waits 0.5 seconds to ensure paste finishes
    A_Clipboard := OldClipboard
}

