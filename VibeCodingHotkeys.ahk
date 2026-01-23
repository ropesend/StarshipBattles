#Requires AutoHotkey v2.0
; G1
; --- SHORTCUT: Left Ctrl + 1 ---
; Debug Next Bug
<^1::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\Debugging\Prompts\Debug Next Bug.txt")
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
; --- SHORTCUT: Left Ctrl + 2 ---
; Add Bug
<^2::
{
     ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\Debugging\Prompts\Add Bug.txt")
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
; --- SHORTCUT: Left Ctrl + 3 ---
; Update Bug Ticket
<^3::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\Debugging\Prompts\Update Bug Ticket.txt")
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
; --- SHORTCUT: Left Ctrl + 4 ---
; Fix Specific Bug
<^4::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\Debugging\Prompts\Fix Specific Bug.txt")
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
; --- SHORTCUT: Left Ctrl + 5 ---
; Close Bug
<^5::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\Debugging\Prompts\Close Bug.txt")
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
; --- SHORTCUT: Left Ctrl + 6 ---
; Reject Bug Fix
<^6::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\Debugging\Prompts\Reject Bug Fix.txt")
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
; --- SHORTCUT: Left Ctrl + 7 ---
; Continue Debugging
<^7::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\Debugging\Prompts\Continue Debugging.txt")
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
; --- SHORTCUT: Left Ctrl + 8 ---
; Batch Close Bugs
<^8::
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

; G9
; --- SHORTCUT: Left Ctrl + 9 ---
; Deep Dive Bug
<^9::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\Debugging\Prompts\Deep Dive Bug.txt")
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

; G0
; --- SHORTCUT: Left Ctrl + 0 ---
<^0::
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
; --- SHORTCUT: Left Ctrl + LeftShift + 1 ---
<+<^1::
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
; --- SHORTCUT: Left Ctrl + LeftShift + 2 ---
<+<^2::
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
; --- SHORTCUT: Left Ctrl + LeftShift + 3 ---
; Start Project
<+<^3::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\Projects\Prompts\Start Project.txt")
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
; --- SHORTCUT: Left Ctrl + LeftShift + 4 ---
; Revise Project
<+<^4::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\Projects\Prompts\Revise Project.txt")
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
; No Prompt
<+<^5::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\Projects\Prompts\No Prompt.txt")
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
; Continue Project
<+<^6::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\Projects\Prompts\Continue Project.txt")
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
; Audit Project
<+<^7::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\Projects\Prompts\Audit Project.txt")
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
; Close Project
<+<^8::
{
    ; Save your current clipboard so you don't lose it
    SavedClip := A_Clipboard
    A_Clipboard := "" ; Clear clipboard for detection

    ; Read the file directly into the clipboard
    try
        A_Clipboard := FileRead("C:\Dev\Starship Battles\Projects\Prompts\Close Project.txt")
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

