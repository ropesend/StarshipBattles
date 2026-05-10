#!/usr/bin/env python3
"""
Tkinter UI for confirming fixed bugs.

Displays checkboxes for all bugs with status "Awaiting Confirmation".
User selects which bugs they've verified, then writes the list to confirmed_bugs.txt.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
from pathlib import Path


TRACKING_DIR = Path(__file__).parent.parent
DEBUG_PLAN_PATH = TRACKING_DIR / "debug_plan.md"
ACTIVE_BUGS_DIR = TRACKING_DIR / "bugs" / "active"
OUTPUT_FILE = TRACKING_DIR / "confirmed_bugs.txt"


def parse_debug_plan():
    """
    Parse debug_plan.md to find bugs with status 'Awaiting Confirmation'.

    Returns list of dicts: [{"id": "BUG-31", "description": "...", "status": "..."}]
    """
    if not DEBUG_PLAN_PATH.exists():
        return []

    content = DEBUG_PLAN_PATH.read_text(encoding="utf-8")
    bugs = []

    # Match table rows: | BUG-XX | date | description | status | link |
    # Use regex to handle potential pipes in description
    table_pattern = re.compile(
        r"^\|\s*(BUG-\d+)\s*\|\s*[\d-]+\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*\[.*?\]\(.*?\)\s*\|$",
        re.MULTILINE
    )

    for match in table_pattern.finditer(content):
        bug_id = match.group(1)
        description = match.group(2).strip()
        status = match.group(3).strip()

        if "Awaiting Confirmation" in status:
            bugs.append({
                "id": bug_id,
                "description": description,
                "status": status
            })

    return bugs


def get_bug_title(bug_id):
    """
    Read the bug ticket file and extract the title from the H1 line.
    Falls back to bug_id if file not found or parsing fails.
    """
    ticket_path = ACTIVE_BUGS_DIR / f"{bug_id}.md"
    if not ticket_path.exists():
        return bug_id

    try:
        content = ticket_path.read_text(encoding="utf-8")
        # Match: # BUG-XX: Title
        match = re.search(r"^#\s*BUG-\d+:\s*(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
    except Exception:
        pass

    return bug_id


class BugConfirmationApp:
    def __init__(self, root, bugs):
        self.root = root
        self.bugs = bugs
        self.checkboxes = {}
        self.checkbox_vars = {}

        self.root.title("Confirm Fixed Bugs")
        self.root.geometry("700x500")
        self.root.minsize(500, 300)

        self._create_widgets()

    def _create_widgets(self):
        # Main frame with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title label
        title_label = ttk.Label(
            main_frame,
            text="Select bugs you have verified as fixed:",
            font=("TkDefaultFont", 11, "bold")
        )
        title_label.pack(anchor=tk.W, pady=(0, 10))

        # Select All / Deselect All buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(0, 10))

        select_all_btn = ttk.Button(
            button_frame,
            text="Select All",
            command=self._select_all
        )
        select_all_btn.pack(side=tk.LEFT, padx=(0, 5))

        deselect_all_btn = ttk.Button(
            button_frame,
            text="Deselect All",
            command=self._deselect_all
        )
        deselect_all_btn.pack(side=tk.LEFT)

        # Count label
        self.count_label = ttk.Label(button_frame, text="")
        self.count_label.pack(side=tk.RIGHT)
        self._update_count()

        # Scrollable frame for checkboxes
        canvas_frame = ttk.Frame(main_frame)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        canvas = tk.Canvas(canvas_frame, highlightthickness=0)
        scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL, command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor=tk.NW)
        canvas.configure(yscrollcommand=scrollbar.set)

        # Enable mouse wheel scrolling
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Create checkboxes for each bug
        if not self.bugs:
            no_bugs_label = ttk.Label(
                self.scrollable_frame,
                text="No bugs awaiting confirmation.",
                font=("TkDefaultFont", 10, "italic")
            )
            no_bugs_label.pack(anchor=tk.W, pady=20)
        else:
            for bug in self.bugs:
                var = tk.BooleanVar(value=False)
                self.checkbox_vars[bug["id"]] = var

                # Get full title from ticket file
                title = get_bug_title(bug["id"])
                label_text = f'{bug["id"]}: {title}'

                # Truncate if too long
                if len(label_text) > 80:
                    label_text = label_text[:77] + "..."

                cb = ttk.Checkbutton(
                    self.scrollable_frame,
                    text=label_text,
                    variable=var,
                    command=self._update_count
                )
                cb.pack(anchor=tk.W, pady=2)
                self.checkboxes[bug["id"]] = cb

        # Bottom buttons
        bottom_frame = ttk.Frame(main_frame)
        bottom_frame.pack(fill=tk.X, pady=(10, 0))

        cancel_btn = ttk.Button(
            bottom_frame,
            text="Cancel",
            command=self.root.destroy
        )
        cancel_btn.pack(side=tk.RIGHT, padx=(5, 0))

        confirm_btn = ttk.Button(
            bottom_frame,
            text="Confirm Selected",
            command=self._confirm_selected
        )
        confirm_btn.pack(side=tk.RIGHT)

    def _select_all(self):
        for var in self.checkbox_vars.values():
            var.set(True)
        self._update_count()

    def _deselect_all(self):
        for var in self.checkbox_vars.values():
            var.set(False)
        self._update_count()

    def _update_count(self):
        selected = sum(1 for var in self.checkbox_vars.values() if var.get())
        total = len(self.checkbox_vars)
        self.count_label.config(text=f"{selected} of {total} selected")

    def _confirm_selected(self):
        selected_bugs = [
            bug_id for bug_id, var in self.checkbox_vars.items() if var.get()
        ]

        if not selected_bugs:
            messagebox.showwarning(
                "No Selection",
                "Please select at least one bug to confirm."
            )
            return

        # Write to confirmed_bugs.txt
        try:
            OUTPUT_FILE.write_text("\n".join(selected_bugs) + "\n", encoding="utf-8")
            messagebox.showinfo(
                "Confirmed",
                f"Confirmed {len(selected_bugs)} bug(s).\n\n"
                f"Run archive_confirmed.py to archive them."
            )
            self.root.destroy()
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to write confirmed_bugs.txt:\n{e}"
            )


def main():
    bugs = parse_debug_plan()

    root = tk.Tk()
    app = BugConfirmationApp(root, bugs)
    root.mainloop()


if __name__ == "__main__":
    main()
