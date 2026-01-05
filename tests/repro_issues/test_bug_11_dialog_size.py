import pytest
import pygame
import pygame_gui
from pygame_gui.windows import UIConfirmationDialog

import os
os.environ["SDL_VIDEODRIVER"] = "dummy"

class TestBug11DialogSize:
    @pytest.fixture(autouse=True)
    def setup_pygame(self):
        pygame.init()
        self.window_size = (1600, 900)
        pygame.display.set_mode(self.window_size)
        # Load theme
        theme_path = "builder_theme.json"
        self.ui_manager = pygame_gui.UIManager(self.window_size, theme_path if os.path.exists(theme_path) else None)
        yield
        # pygame.quit() removed for xdist session isolation

    def test_confirmation_dialog_scrolling(self):
        """
        Verify that the 'Confirm Refit' dialog requires scrolling with 400x200 size.
        """
        new_class = "Cruiser"
        # Original message
        msg = f"Change class to {new_class}?<br><br>Warning: This will attempt to refit existing components.<br>Some items may be resized or lost if they don't fit."
        # Make it even longer to ensure it scrolls if font is small
        msg += "<br><br>" + "Long message line. " * 20
        
        # Fixed dimensions from builder_screen.py
        dialog_rect = pygame.Rect((1600-600)//2, (900-400)//2, 600, 400)
        
        dialog = UIConfirmationDialog(
            rect=dialog_rect,
            manager=self.ui_manager,
            action_long_desc=msg,
            window_title="Confirm Refit"
        )
        
        # Force layout update
        self.ui_manager.update(0.1)
        
        text_box = None
        for element in dialog.get_container().elements:
            if isinstance(element, pygame_gui.elements.UITextBox):
                text_box = element
                break
        
        assert text_box is not None, "Could not find UITextBox in UIConfirmationDialog"
        
        # Check if text is truncated or scrollbar is visible
        has_scroll = False
        if hasattr(text_box, 'scroll_bar') and text_box.scroll_bar is not None:
             if text_box.scroll_bar.visible:
                 has_scroll = True
        elif hasattr(text_box, 'vertical_scroll_bar') and text_box.vertical_scroll_bar is not None:
             if text_box.vertical_scroll_bar.visible:
                 has_scroll = True
        
        # Verification: After the fix, we expect NO scroll bar
        print(f"\nDialog Size: {dialog_rect.size}")
        if not has_scroll:
            print("VERIFIED: Dialog does NOT have a scroll bar with the new size.")
        else:
            print("FAILURE: Scroll bar still visible despite larger size.")
            
        assert not has_scroll, "Fix verification failed: Scroll bar still detected in 600x400 dialog."
