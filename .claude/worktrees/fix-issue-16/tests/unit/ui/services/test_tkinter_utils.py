"""Tests for tkinter_utils module.

Note: pytest conftest.py sets SDL_VIDEODRIVER=dummy globally for headless mode.
Tests must patch os.environ to override this for testing successful init cases.
"""
import os
from unittest.mock import MagicMock, patch

import pytest

# Import the module - we'll patch at the module level
from game.ui.services import tkinter_utils


@pytest.fixture(autouse=True)
def reset_tkinter_state():
    """Reset tkinter_utils state before and after each test."""
    tkinter_utils.reset_tk_root()
    yield
    tkinter_utils.reset_tk_root()


class TestGetTkRoot:
    """Tests for get_tk_root function."""

    def test_returns_none_when_sdl_dummy(self):
        """Should return None when SDL_VIDEODRIVER is dummy.

        Note: SDL_VIDEODRIVER=dummy is set by conftest.py, so this tests
        the actual test environment behavior.
        """
        # Verify the environment is set (by conftest.py)
        assert os.environ.get("SDL_VIDEODRIVER") == "dummy"

        result = tkinter_utils.get_tk_root()
        assert result is None
        assert not tkinter_utils.is_tkinter_available()

    def test_handles_tcl_error(self):
        """Should handle TclError gracefully."""
        import tkinter

        # Must clear SDL_VIDEODRIVER to bypass that check
        with patch.dict(os.environ, {"SDL_VIDEODRIVER": ""}, clear=False):
            with patch.object(tkinter_utils, "tkinter") as mock_tk_module:
                mock_tk_module.Tk.side_effect = tkinter.TclError("Test error")
                mock_tk_module.TclError = tkinter.TclError
                result = tkinter_utils.get_tk_root()

        assert result is None
        assert not tkinter_utils.is_tkinter_available()

    def test_handles_runtime_error(self):
        """Should handle RuntimeError gracefully."""
        import tkinter as real_tkinter

        with patch.dict(os.environ, {"SDL_VIDEODRIVER": ""}, clear=False):
            # Must reset AFTER patching env to clear SDL dummy detection
            tkinter_utils.reset_tk_root()
            with patch.object(tkinter_utils, "tkinter") as mock_tk_module:
                # Must provide real TclError for exception handling
                mock_tk_module.TclError = real_tkinter.TclError
                mock_tk_module.Tk.side_effect = RuntimeError("Test error")
                result = tkinter_utils.get_tk_root()

            assert result is None
            assert not tkinter_utils.is_tkinter_available()

    def test_lazy_initialization_caches_result(self):
        """Should only initialize once and cache the result."""
        mock_root = MagicMock()

        with patch.dict(os.environ, {"SDL_VIDEODRIVER": ""}, clear=False):
            with patch.object(tkinter_utils, "tkinter") as mock_tk_module:
                mock_tk_module.Tk.return_value = mock_root
                # First call - should initialize
                result1 = tkinter_utils.get_tk_root()
                # Second call - should return cached
                result2 = tkinter_utils.get_tk_root()

            assert result1 is mock_root
            assert result2 is mock_root
            assert mock_tk_module.Tk.call_count == 1  # Only called once


class TestIsTkinterAvailable:
    """Tests for is_tkinter_available function."""

    def test_returns_true_when_initialized(self):
        """Should return True when Tk root initializes successfully."""
        mock_root = MagicMock()

        with patch.dict(os.environ, {"SDL_VIDEODRIVER": ""}, clear=False):
            with patch.object(tkinter_utils, "tkinter") as mock_tk_module:
                mock_tk_module.Tk.return_value = mock_root
                result = tkinter_utils.is_tkinter_available()

        assert result is True

    def test_returns_false_when_init_fails(self):
        """Should return False when Tk init fails."""
        import tkinter as real_tkinter

        with patch.dict(os.environ, {"SDL_VIDEODRIVER": ""}, clear=False):
            # Must reset AFTER patching env to clear SDL dummy detection
            tkinter_utils.reset_tk_root()
            with patch.object(tkinter_utils, "tkinter") as mock_tk_module:
                # Must provide real TclError for exception handling
                mock_tk_module.TclError = real_tkinter.TclError
                mock_tk_module.Tk.side_effect = RuntimeError("No display")
                result = tkinter_utils.is_tkinter_available()

            assert result is False

    def test_returns_false_for_sdl_dummy(self):
        """Should return False when SDL_VIDEODRIVER=dummy (headless test mode)."""
        # This is the actual test environment
        assert not tkinter_utils.is_tkinter_available()


class TestResetTkRoot:
    """Tests for reset_tk_root function."""

    def test_resets_state_for_reinitialize(self):
        """Should reset state allowing reinitialization."""
        with patch.dict(os.environ, {"SDL_VIDEODRIVER": ""}, clear=False):
            # First init
            mock_root1 = MagicMock()
            with patch.object(tkinter_utils, "tkinter") as mock_tk_module:
                mock_tk_module.Tk.return_value = mock_root1
                result1 = tkinter_utils.get_tk_root()

            assert result1 is mock_root1

            # Reset
            tkinter_utils.reset_tk_root()

            # Second init - should create new
            mock_root2 = MagicMock()
            with patch.object(tkinter_utils, "tkinter") as mock_tk_module:
                mock_tk_module.Tk.return_value = mock_root2
                result2 = tkinter_utils.get_tk_root()

            assert result2 is mock_root2
            assert result2 is not result1


class TestOpenSaveDialog:
    """Tests for open_save_dialog function."""

    def test_returns_none_when_tk_unavailable(self):
        """Should return None when Tkinter unavailable (SDL dummy mode)."""
        # In test environment with SDL_VIDEODRIVER=dummy
        result = tkinter_utils.open_save_dialog("/tmp")
        assert result is None

    def test_calls_filedialog_with_params(self):
        """Should call filedialog with provided parameters."""
        mock_root = MagicMock()

        with patch.dict(os.environ, {"SDL_VIDEODRIVER": ""}, clear=False):
            with patch.object(tkinter_utils, "tkinter") as mock_tk_module:
                mock_tk_module.Tk.return_value = mock_root
                with patch.object(tkinter_utils, "filedialog") as mock_dialog:
                    mock_dialog.asksaveasfilename.return_value = "/path/to/file.json"
                    result = tkinter_utils.open_save_dialog(
                        initialdir="/test",
                        initialfile="test.json",
                        title="Save Test"
                    )

        assert result == "/path/to/file.json"
        mock_dialog.asksaveasfilename.assert_called_once()


class TestOpenLoadDialog:
    """Tests for open_load_dialog function."""

    def test_returns_none_when_tk_unavailable(self):
        """Should return None when Tkinter unavailable."""
        # In test environment with SDL_VIDEODRIVER=dummy
        result = tkinter_utils.open_load_dialog("/tmp")
        assert result is None


class TestPromptString:
    """Tests for prompt_string function."""

    def test_returns_initialvalue_when_tk_unavailable(self):
        """Should return initialvalue as fallback when Tkinter unavailable."""
        # In test environment with SDL_VIDEODRIVER=dummy
        result = tkinter_utils.prompt_string("Title", "Prompt", "Default")
        assert result == "Default"


class TestCopyToClipboard:
    """Tests for copy_to_clipboard function."""

    def test_returns_false_when_tk_unavailable(self):
        """Should return False when Tkinter unavailable."""
        # In test environment with SDL_VIDEODRIVER=dummy
        result = tkinter_utils.copy_to_clipboard("test")
        assert result is False

    def test_copies_text_to_clipboard(self):
        """Should copy text to clipboard when Tkinter available."""
        mock_root = MagicMock()

        with patch.dict(os.environ, {"SDL_VIDEODRIVER": ""}, clear=False):
            with patch.object(tkinter_utils, "tkinter") as mock_tk_module:
                mock_tk_module.Tk.return_value = mock_root
                result = tkinter_utils.copy_to_clipboard("test text")

        assert result is True
        mock_root.clipboard_clear.assert_called_once()
        mock_root.clipboard_append.assert_called_once_with("test text")
        mock_root.update.assert_called_once()
