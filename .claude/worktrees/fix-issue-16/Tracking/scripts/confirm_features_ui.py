#!/usr/bin/env python3
"""
Tkinter UI for confirming implemented features.

Displays checkboxes for all features with status "Awaiting Confirmation".
User selects which features they've verified, then writes the list to confirmed_features.txt.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import re
from pathlib import Path


TRACKING_DIR = Path(__file__).parent.parent
FEATURE_PLAN_PATH = TRACKING_DIR / "feature_plan.md"
ACTIVE_FEATURES_DIR = TRACKING_DIR / "features" / "active"
OUTPUT_FILE = TRACKING_DIR / "confirmed_features.txt"


def parse_feature_plan():
    """
    Parse feature_plan.md to find features with status 'Awaiting Confirmation'.

    Returns list of dicts: [{"id": "FEAT-01", "description": "...", "status": "..."}]
    """
    if not FEATURE_PLAN_PATH.exists():
        return []

    content = FEATURE_PLAN_PATH.read_text(encoding="utf-8")
    features = []

    # Match table rows: | FEAT-XX | date | description | status | link |
    table_pattern = re.compile(
        r"^\|\s*(FEAT-\d+)\s*\|\s*[\d-]+\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*\[.*?\]\(.*?\)\s*\|$",
        re.MULTILINE
    )

    for match in table_pattern.finditer(content):
        feat_id = match.group(1)
        description = match.group(2).strip()
        status = match.group(3).strip()

        if "Awaiting Confirmation" in status:
            features.append({
                "id": feat_id,
                "description": description,
                "status": status
            })

    return features


def get_feature_title(feat_id):
    """
    Read the feature ticket file and extract the title from the H1 line.
    Falls back to feat_id if file not found or parsing fails.
    """
    ticket_path = ACTIVE_FEATURES_DIR / f"{feat_id}.md"
    if not ticket_path.exists():
        return feat_id

    try:
        content = ticket_path.read_text(encoding="utf-8")
        # Match: # FEAT-XX: Title
        match = re.search(r"^#\s*FEAT-\d+:\s*(.+)$", content, re.MULTILINE)
        if match:
            return match.group(1).strip()
    except Exception:
        pass

    return feat_id


class FeatureConfirmationApp:
    def __init__(self, root, features):
        self.root = root
        self.features = features
        self.checkboxes = {}
        self.checkbox_vars = {}

        self.root.title("Confirm Implemented Features")
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
            text="Select features you have verified as implemented:",
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

        # Create checkboxes for each feature
        if not self.features:
            no_features_label = ttk.Label(
                self.scrollable_frame,
                text="No features awaiting confirmation.",
                font=("TkDefaultFont", 10, "italic")
            )
            no_features_label.pack(anchor=tk.W, pady=20)
        else:
            for feature in self.features:
                var = tk.BooleanVar(value=False)
                self.checkbox_vars[feature["id"]] = var

                # Get full title from ticket file
                title = get_feature_title(feature["id"])
                label_text = f'{feature["id"]}: {title}'

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
                self.checkboxes[feature["id"]] = cb

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
        selected_features = [
            feat_id for feat_id, var in self.checkbox_vars.items() if var.get()
        ]

        if not selected_features:
            messagebox.showwarning(
                "No Selection",
                "Please select at least one feature to confirm."
            )
            return

        # Write to confirmed_features.txt
        try:
            OUTPUT_FILE.write_text("\n".join(selected_features) + "\n", encoding="utf-8")
            messagebox.showinfo(
                "Confirmed",
                f"Confirmed {len(selected_features)} feature(s).\n\n"
                f"Run archive_confirmed.py to archive them."
            )
            self.root.destroy()
        except Exception as e:
            messagebox.showerror(
                "Error",
                f"Failed to write confirmed_features.txt:\n{e}"
            )


def main():
    features = parse_feature_plan()

    root = tk.Tk()
    app = FeatureConfirmationApp(root, features)
    root.mainloop()


if __name__ == "__main__":
    main()
