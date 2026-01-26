import pytest
import os
import pygame
import pygame_gui
from unittest.mock import MagicMock, patch

from game.ui.panels.builder_widgets import ModifierEditorPanel
from game.core.registry import RegistryManager
from game.simulation.components.component import Modifier


@pytest.fixture
def pygame_env():
    """Set up pygame environment for testing."""
    os.environ['SDL_VIDEODRIVER'] = 'dummy'
    pygame.init()
    window = pygame.display.set_mode((800, 600), flags=pygame.HIDDEN)
    manager = pygame_gui.UIManager((800, 600))
    container = pygame_gui.elements.UIPanel(pygame.Rect(0, 0, 100, 100), manager=manager)

    # Ensure registry has our mods
    mods = RegistryManager.instance().modifiers
    if 'simple_size' not in mods:
        mods['simple_size'] = Modifier({'id': 'simple_size', 'name': 'Size', 'type': 'linear', 'min_val': 1, 'max_val': 100})
    if 'range_mount' not in mods:
        mods['range_mount'] = Modifier({'id': 'range_mount', 'name': 'Range', 'type': 'linear', 'min_val': 0, 'max_val': 10})
    if 'facing' not in mods:
        mods['facing'] = Modifier({'id': 'facing', 'name': 'Facing', 'type': 'linear', 'min_val': 0, 'max_val': 360})

    yield {'manager': manager, 'container': container}

    # Cleanup
    patch.stopall()
    pygame.quit()


def _setup_mock_comp(type_str):
    """Set up a mock component with the given type."""
    mock_comp = MagicMock()
    mock_comp.name = f"Test{type_str}"
    mock_comp.type_str = type_str

    mods = {}
    def get_mod(mid): return mods.get(mid)
    def add_mod(mid):
        m = MagicMock()
        m.value = 1.0  # Default
        mods[mid] = m
        return True

    # ModifierLogic now reads from comp.data for base stats
    mock_comp.data = {}
    def remove_mod(mid):
        if mid in mods: del mods[mid]

    mock_comp.get_modifier.side_effect = get_mod
    mock_comp.add_modifier.side_effect = add_mod
    mock_comp.remove_modifier.side_effect = remove_mod
    return mock_comp, mods


class TestMandatoryModifiers:
    def test_auto_apply_turret(self, pygame_env):
        panel = ModifierEditorPanel(pygame_env['manager'], pygame_env['container'], 400, MagicMock())
        mock_comp, mods = _setup_mock_comp('ProjectileWeapon')
        mock_comp.firing_arc = 45  # Base arc
        mock_comp.data['firing_arc'] = 45

        test_registry = {
            'turret_mount': Modifier({'id': 'turret_mount', 'name': 'Turret', 'type': 'linear', 'min_val': 0, 'max_val': 360, 'restrictions': {'allow_types': ['ProjectileWeapon']}})
        }

        with patch.dict(RegistryManager.instance().modifiers, test_registry, clear=True):
            panel.rebuild(mock_comp, {})
            panel.layout(10)

        assert 'turret_mount' in mods
        assert mods['turret_mount'].value == 45  # Should default to base

    def test_turret_min_constraint_updates(self, pygame_env):
        # Ensure buttons respect the base firing arc constraint
        panel = ModifierEditorPanel(pygame_env['manager'], pygame_env['container'], 400, MagicMock())
        mock_comp, mods = _setup_mock_comp('ProjectileWeapon')
        mock_comp.firing_arc = 45
        mock_comp.data['firing_arc'] = 45

        test_registry = {
            'turret_mount': Modifier({'id': 'turret_mount', 'name': 'Turret', 'type': 'linear', 'min_val': 0, 'max_val': 360, 'restrictions': {'allow_types': ['ProjectileWeapon']}})
        }

        with patch.dict(RegistryManager.instance().modifiers, test_registry, clear=True):
            panel.rebuild(mock_comp, {})
            panel.layout(10)

            # Locate row
            assert 'turret_mount' in panel.modifier_rows, "Row not found"
            row = panel.modifier_rows['turret_mount']

            # Locate a decrement button in the row
            # We need to find the button that does snap_floor 15.
            # Row stores buttons in self.buttons dict: element -> action
            target_btn = None
            for btn, action in row.buttons.items():
                if action['action'] == 'snap_floor' and action['value'] == 15:
                    target_btn = btn
                    break

            assert target_btn is not None, "Decrement button not found in row"

            # Mock the slider in the row to return current value
            row.slider = MagicMock()
            row.slider.get_current_value.return_value = 45.0

            # Trigger event
            event = MagicMock()
            event.type = pygame_gui.UI_BUTTON_PRESSED
            event.ui_element = target_btn

            # Handle event
            panel.handle_event(event)

            # Test explicit set attempt to violate constraint
            # Using 'set_value' mode button if we had one, or manual injection.
            # Let's inject a fake button into the row for testing 'set_value'
            mock_btn = MagicMock()
            row.buttons[mock_btn] = {'action': 'set_value', 'value': 40}

            event.ui_element = mock_btn
            panel.handle_event(event)

            # Should be clamped to 45.
            # 45 -> 45. No change.

            # Try setting current to 60, then decrement to 45 (allowed), then decrement to 30 (blocked)
            row.current_value = 60.0
            # Decrement 15 -> 45
            event.ui_element = target_btn

            # We need to mock the callback because Row calls it
            mock_cb = MagicMock()
            row.on_change_callback = mock_cb

            panel.handle_event(event)

            # Should have called callback with 45
            mock_cb.assert_called_with('value_change', 'turret_mount', 45.0)

    def test_range_limit_seeker(self, pygame_env):
        # Range should NOT apply to Seeker
        panel = ModifierEditorPanel(pygame_env['manager'], pygame_env['container'], 400, MagicMock())
        mock_comp, mods = _setup_mock_comp('SeekerWeapon')

        test_registry = {
            'range_mount': Modifier({'id': 'range_mount', 'name': 'Range', 'type': 'linear', 'min_val': 0, 'max_val': 10, 'restrictions': {'allow_types': ['ProjectileWeapon', 'BeamWeapon']}})
            # Note: Seeker NOT in allow_types (mimicking modifiers.json update)
        }

        with patch.dict(RegistryManager.instance().modifiers, test_registry, clear=True):
            panel.rebuild(mock_comp, {})
            panel.layout(10)

        assert 'range_mount' not in mods

    def test_auto_apply_size(self, pygame_env):
        panel = ModifierEditorPanel(pygame_env['manager'], pygame_env['container'], 400, MagicMock())
        mock_comp, mods = _setup_mock_comp('reactor')
        # Ensure registry has simple_size_mount
        with patch.dict(RegistryManager.instance().modifiers, {'simple_size_mount': Modifier({'id': 'simple_size_mount', 'name': 'Size', 'type': 'linear', 'min_val': 1, 'max_val': 100})}, clear=True):
            # Run layout
            panel.rebuild(mock_comp, {})
            panel.layout(10)

        assert 'simple_size_mount' in mods

    def test_auto_apply_range_weapon(self, pygame_env):
        panel = ModifierEditorPanel(pygame_env['manager'], pygame_env['container'], 400, MagicMock())
        # USE CORRECT TYPE STRING
        mock_comp, mods = _setup_mock_comp('ProjectileWeapon')

        # Setup registry with all needed mods and CORRECT RESTRICTIONS
        test_registry = {
            'simple_size_mount': Modifier({'id': 'simple_size_mount', 'name': 'Size', 'type': 'linear', 'min_val': 1, 'max_val': 100}),
            'range_mount': Modifier({
                'id': 'range_mount', 'name': 'Range', 'type': 'linear', 'min_val': 0, 'max_val': 10,
                'restrictions': {'allow_types': ['ProjectileWeapon', 'BeamWeapon', 'SeekerWeapon']}
            }),
            'facing': Modifier({
                'id': 'facing', 'name': 'Facing', 'type': 'linear', 'min_val': 0, 'max_val': 360,
                'restrictions': {'allow_types': ['ProjectileWeapon', 'BeamWeapon', 'SeekerWeapon']}
            })
        }

        with patch.dict(RegistryManager.instance().modifiers, test_registry, clear=True):
            # Run layout
            panel.rebuild(mock_comp, {})
            panel.layout(10)

        assert 'range_mount' in mods
        assert 'simple_size_mount' in mods
        assert 'facing' in mods

    def test_no_auto_apply_range_non_weapon(self, pygame_env):
        panel = ModifierEditorPanel(pygame_env['manager'], pygame_env['container'], 400, MagicMock())
        mock_comp, mods = _setup_mock_comp('Reactor')  # PascalCase for non-weapon too likely

        test_registry = {
            'simple_size_mount': Modifier({'id': 'simple_size_mount', 'name': 'Size', 'type': 'linear', 'min_val': 1, 'max_val': 100}),
            'range_mount': Modifier({
                'id': 'range_mount', 'name': 'Range', 'type': 'linear', 'min_val': 0, 'max_val': 10,
                'restrictions': {'allow_types': ['ProjectileWeapon', 'BeamWeapon', 'SeekerWeapon']}
            })
        }

        with patch.dict(RegistryManager.instance().modifiers, test_registry, clear=True):
            panel.rebuild(mock_comp, {})
            panel.layout(10)

        assert 'range_mount' not in mods
        assert 'simple_size_mount' in mods

    def test_prevent_removal(self, pygame_env):
        panel = ModifierEditorPanel(pygame_env['manager'], pygame_env['container'], 400, MagicMock())
        mock_comp, mods = _setup_mock_comp('Reactor')

        # Pre-add
        m = MagicMock()
        m.value = 1.0
        mods['simple_size_mount'] = m

        test_registry = {
            'simple_size_mount': Modifier({'id': 'simple_size_mount', 'name': 'Size', 'type': 'linear', 'min_val': 1, 'max_val': 100})
        }

        with patch.dict(RegistryManager.instance().modifiers, test_registry, clear=True):
            panel.rebuild(mock_comp, {})
            panel.layout(10)

            # Find button - New Structure uses modifier_rows
            assert 'simple_size_mount' in panel.modifier_rows, "simple_size_mount row not created"

            row = panel.modifier_rows['simple_size_mount']
            btn = row.name_label

            event = MagicMock()
            event.type = pygame_gui.UI_BUTTON_PRESSED
            event.ui_element = btn

            panel.handle_event(event)

        # Verify NOT removed
        assert 'simple_size_mount' in mods
        mock_comp.remove_modifier.assert_not_called()
