"""Tests for UI widget classes."""
import unittest
import pygame

from ui import Button, Label, Slider


class TestButton(unittest.TestCase):
    """Test Button widget."""
    
    def setUp(self):
        import os
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        pygame.font.init()

    def tearDown(self):
        pygame.quit()
    
    
    def test_button_initialization(self):
        """Button should initialize with correct rect."""
        btn = Button(10, 20, 100, 50, "Test", None)
        
        self.assertEqual(btn.rect.x, 10)
        self.assertEqual(btn.rect.y, 20)
        self.assertEqual(btn.rect.w, 100)
        self.assertEqual(btn.rect.h, 50)
    
    def test_button_stores_callback(self):
        """Button should store its callback."""
        cb_called = [False]
        def callback():
            cb_called[0] = True
        
        btn = Button(0, 0, 100, 50, "Test", callback)
        
        self.assertEqual(btn.callback, callback)
    
    def test_button_hover_detection(self):
        """Hover state should change on mouse motion."""
        btn = Button(0, 0, 100, 50, "Test", None)
        
        # Motion inside
        event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': (50, 25)})
        btn.handle_event(event)
        
        self.assertTrue(btn.is_hovered)
        
        # Motion outside
        event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': (200, 200)})
        btn.handle_event(event)
        
        self.assertFalse(btn.is_hovered)
    
    def test_button_click_fires_callback(self):
        """Click on hovered button should fire callback."""
        cb_called = [False]
        def callback():
            cb_called[0] = True
        
        btn = Button(0, 0, 100, 50, "Test", callback)
        
        # First hover over button
        motion_event = pygame.event.Event(pygame.MOUSEMOTION, {'pos': (50, 25)})
        btn.handle_event(motion_event)
        
        # Then click
        click_event = pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1, 'pos': (50, 25)})
        btn.handle_event(click_event)
        
        self.assertTrue(cb_called[0])


class TestLabel(unittest.TestCase):
    """Test Label widget."""
    
    def setUp(self):
        import os
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        pygame.font.init()

    def tearDown(self):
        pygame.quit()
    
    
    def test_label_initialization(self):
        """Label should initialize with correct position and text."""
        lbl = Label(10, 20, "Hello World")
        
        self.assertEqual(lbl.pos, (10, 20))
        self.assertEqual(lbl.text, "Hello World")
    
    def test_label_update_text(self):
        """update_text should change label text."""
        lbl = Label(0, 0, "Original")
        
        lbl.update_text("New Text")
        
        self.assertEqual(lbl.text, "New Text")
    
    def test_label_custom_color(self):
        """Label should accept custom color."""
        lbl = Label(0, 0, "Test", color=(255, 0, 0))
        
        self.assertEqual(lbl.color, (255, 0, 0))


class TestSlider(unittest.TestCase):
    """Test Slider widget."""
    
    def setUp(self):
        import os
        os.environ["SDL_VIDEODRIVER"] = "dummy"
        pygame.init()
        pygame.font.init()
    
    
    def test_slider_initialization(self):
        """Slider should initialize with correct values."""
        slider = Slider(0, 0, 100, 20, 0, 100, 50, None)
        
        self.assertEqual(slider.min_val, 0)
        self.assertEqual(slider.max_val, 100)
        self.assertEqual(slider.val, 50)
    
    def test_slider_value_update(self):
        """update_val should change slider value."""
        slider = Slider(0, 0, 100, 20, 0, 100, 50, None)
        
        # Drag to middle of slider
        slider.update_val(50)
        
        # Value should have updated
        self.assertIsNotNone(slider.val)
    
    def test_slider_callback_fires(self):
        """Slider should fire callback on value change."""
        cb_called = [False]
        def callback(val):
            cb_called[0] = True
        
        slider = Slider(0, 0, 100, 20, 0, 100, 50, callback)
        
        # Update value (simulate drag)
        slider.update_val(75)
        
        self.assertTrue(cb_called[0])
    
    def test_slider_clamps_value(self):
        """Slider should clamp value within bounds."""
        slider = Slider(0, 0, 100, 20, 0, 100, 50, None)
        
        # Value should stay within min/max
        self.assertGreaterEqual(slider.val, slider.min_val)
        self.assertLessEqual(slider.val, slider.max_val)


if __name__ == '__main__':
    unittest.main()
