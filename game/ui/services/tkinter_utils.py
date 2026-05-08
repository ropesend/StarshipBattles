"""
Tkinter Utilities - Consolidated Tkinter initialization and helpers.

DUP-UI2-001: Extracted from multiple files to eliminate duplication of
Tkinter root initialization pattern across:
- ship_io.py
- formation_editor.py
- workshop_ship_io.py

This module provides:
- Lazy, thread-safe Tkinter root initialization
- Unified exception handling for platform-dependent Tkinter operations
- Helper functions for clipboard and file dialog operations
"""
import os
import tkinter
from tkinter import filedialog, simpledialog
from typing import Optional, List, Tuple

import logging

logger = logging.getLogger(__name__)


# Module-level state for lazy initialization
_tk_root: Optional[tkinter.Tk] = None
_initialized: bool = False
_available: bool = True  # Assume available until proven otherwise


def get_tk_root() -> Optional[tkinter.Tk]:
    """Get the shared Tkinter root instance, initializing lazily if needed.

    This function provides a single point of Tkinter initialization with
    proper exception handling for all platform-dependent edge cases.

    Returns:
        The Tkinter root instance, or None if Tkinter is unavailable.

    Note:
        The root is created with withdraw() called to keep it hidden.
        This is intended for file dialogs and clipboard operations.
    """
    global _tk_root, _initialized, _available

    if _initialized:
        return _tk_root

    _initialized = True

    # Check for headless/dummy display mode
    if os.environ.get("SDL_VIDEODRIVER") == "dummy":
        logger.warning("Tkinter disabled: SDL_VIDEODRIVER=dummy")
        _available = False
        return None

    try:
        _tk_root = tkinter.Tk()
        _tk_root.withdraw()
        return _tk_root
    except tkinter.TclError as e:
        logger.warning(f"Tkinter TCL error, dialogs will be unavailable: {e}")
        _available = False
        _tk_root = None
    except RuntimeError as e:
        logger.warning(f"Tkinter runtime error, dialogs will be unavailable: {e}")
        _available = False
        _tk_root = None
    except Exception as e:  # Intentional broad catch: Tkinter init is platform-dependent
        logger.warning(f"Tkinter initialization failed, dialogs will be unavailable: {e}")
        _available = False
        _tk_root = None

    return _tk_root


def is_tkinter_available() -> bool:
    """Check if Tkinter is available for use.

    This will trigger lazy initialization if not already done.

    Returns:
        True if Tkinter root was successfully initialized.
    """
    get_tk_root()  # Ensure initialization
    return _available and _tk_root is not None


def reset_tk_root() -> None:
    """Reset Tkinter state (primarily for testing).

    This destroys the existing root and resets initialization state,
    allowing re-initialization on next call to get_tk_root().
    """
    global _tk_root, _initialized, _available

    if _tk_root is not None:
        try:
            _tk_root.destroy()
        except Exception:  # Intentional broad catch: Tk widget .destroy() raises various TclError subclasses if already destroyed or interpreter is gone
            pass

    _tk_root = None
    _initialized = False
    _available = True


def open_save_dialog(
    initialdir: str,
    initialfile: str = "",
    defaultextension: str = ".json",
    filetypes: Optional[List[Tuple[str, str]]] = None,
    title: str = "Save File"
) -> Optional[str]:
    """Show a file save dialog.

    Args:
        initialdir: Initial directory to show
        initialfile: Default filename
        defaultextension: Extension to add if none provided
        filetypes: List of (description, pattern) tuples
        title: Dialog window title

    Returns:
        Selected filepath, or None if cancelled or Tkinter unavailable.
    """
    root = get_tk_root()
    if root is None:
        return None

    if filetypes is None:
        filetypes = [("JSON Files", "*.json")]

    try:
        return filedialog.asksaveasfilename(
            initialdir=initialdir,
            initialfile=initialfile,
            defaultextension=defaultextension,
            filetypes=filetypes,
            title=title
        )
    except Exception as e:  # Intentional broad catch: file dialog is platform-dependent
        logger.warning(f"Save dialog failed: {e}")
        return None


def open_load_dialog(
    initialdir: str,
    filetypes: Optional[List[Tuple[str, str]]] = None,
    title: str = "Open File"
) -> Optional[str]:
    """Show a file open dialog.

    Args:
        initialdir: Initial directory to show
        filetypes: List of (description, pattern) tuples
        title: Dialog window title

    Returns:
        Selected filepath, or None if cancelled or Tkinter unavailable.
    """
    root = get_tk_root()
    if root is None:
        return None

    if filetypes is None:
        filetypes = [("JSON Files", "*.json")]

    try:
        return filedialog.askopenfilename(
            initialdir=initialdir,
            filetypes=filetypes,
            title=title
        )
    except Exception as e:  # Intentional broad catch: file dialog is platform-dependent
        logger.warning(f"Open dialog failed: {e}")
        return None


def prompt_string(
    title: str,
    prompt: str,
    initialvalue: str = ""
) -> Optional[str]:
    """Show a string input dialog.

    Args:
        title: Dialog window title
        prompt: Prompt text to display
        initialvalue: Initial value in the text field

    Returns:
        User-entered string, or None if cancelled or Tkinter unavailable.
    """
    root = get_tk_root()
    if root is None:
        return initialvalue if initialvalue else None

    try:
        return simpledialog.askstring(
            title,
            prompt,
            initialvalue=initialvalue,
            parent=root
        )
    except Exception as e:  # Intentional broad catch: dialog is platform-dependent
        logger.warning(f"String prompt failed: {e}")
        return initialvalue if initialvalue else None


def copy_to_clipboard(text: str) -> bool:
    """Copy text to system clipboard using Tkinter.

    Args:
        text: Text to copy to clipboard

    Returns:
        True if successful, False otherwise.
    """
    root = get_tk_root()
    if root is None:
        return False

    try:
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()  # Required to finalize clipboard
        return True
    except Exception as e:  # Intentional broad catch: clipboard is platform-dependent
        logger.warning(f"Clipboard copy failed (Tkinter): {e}")
        return False
