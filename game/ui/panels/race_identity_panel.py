"""
Race Identity Panel - Identity configuration for races.

PROJ-66 Phase 3: Panel for configuring race identity fields including
race name, government type, faction name, and other identity attributes.

Provides UI controls for:
- Race name and plural form
- Physical type selection
- Government type and organization
- Leader title selection
- Society type selection
- Faction name (auto-generated or custom)
"""
import pygame
import pygame_gui
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from game.strategy.data.race_config import RaceConfig

from game.strategy.data.race_config import (
    GOVERNMENT_TYPES,
    GOVERNMENT_ORGANIZATIONS,
    LEADER_TITLES,
    PHYSICAL_TYPES,
    SOCIETY_TYPES,
)


class RaceIdentityPanel:
    """
    Panel for configuring race identity attributes.

    Creates and manages text inputs and dropdowns for race name,
    government, physical type, and faction identity.
    """

    # Empty option for dropdowns
    EMPTY_OPTION = "-- Select --"

    def __init__(
        self,
        panel: pygame_gui.elements.UIPanel,
        manager: pygame_gui.UIManager,
        race_config: 'RaceConfig'
    ):
        """
        Create identity configuration panel content.

        Args:
            panel: Parent UIPanel to add controls to
            manager: pygame_gui UIManager
            race_config: RaceConfig to read/write values from/to
        """
        self.panel = panel
        self.ui_manager = manager
        self.race_config = race_config

        # Track if faction name was manually overridden
        self._faction_name_overridden = False

        # Initialize UI element references
        self._init_empty_refs()

        self._create_content()

    def _init_empty_refs(self):
        """Initialize all UI references to None."""
        # Text inputs
        self.race_name_input: Optional[pygame_gui.elements.UITextEntryLine] = None
        self.race_name_plural_input: Optional[pygame_gui.elements.UITextEntryLine] = None
        self.faction_name_input: Optional[pygame_gui.elements.UITextEntryLine] = None

        # Dropdowns
        self.physical_type_dropdown: Optional[pygame_gui.elements.UIDropDownMenu] = None
        self.government_type_dropdown: Optional[pygame_gui.elements.UIDropDownMenu] = None
        self.government_org_dropdown: Optional[pygame_gui.elements.UIDropDownMenu] = None
        self.leader_title_dropdown: Optional[pygame_gui.elements.UIDropDownMenu] = None
        self.society_type_dropdown: Optional[pygame_gui.elements.UIDropDownMenu] = None

    def _create_content(self):
        """Create all panel content."""
        panel_width = self.panel.get_relative_rect().width - 20
        y = 5

        # Section 1: Race Identity
        y = self._create_race_section(y, panel_width)
        y += 15

        # Section 2: Government
        y = self._create_government_section(y, panel_width)
        y += 15

        # Section 3: Faction
        y = self._create_faction_section(y, panel_width)

    def _create_race_section(self, y: int, width: int) -> int:
        """Create race identity controls."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 200, 25),
            text="Species Identity:",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#section_header"
        )
        y += 28

        # Race Name
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 120, 22),
            text="Species Name:",
            manager=self.ui_manager,
            container=self.panel
        )
        self.race_name_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(140, y, width - 160, 28),
            manager=self.ui_manager,
            container=self.panel,
            placeholder_text="Species name (e.g., Rossarian)"
        )
        if self.race_config.race_name:
            self.race_name_input.set_text(self.race_config.race_name)
        y += 32

        # Race Name Plural
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 120, 22),
            text="Plural Form:",
            manager=self.ui_manager,
            container=self.panel
        )
        self.race_name_plural_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(140, y, width - 160, 28),
            manager=self.ui_manager,
            container=self.panel,
            placeholder_text="Plural (e.g., Rossarians)"
        )
        if self.race_config.race_name_plural:
            self.race_name_plural_input.set_text(self.race_config.race_name_plural)
        y += 32

        # Physical Type dropdown
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 120, 22),
            text="Physical Type:",
            manager=self.ui_manager,
            container=self.panel
        )
        physical_options = [self.EMPTY_OPTION] + list(PHYSICAL_TYPES)
        starting_option = self.race_config.physical_type if self.race_config.physical_type else self.EMPTY_OPTION
        self.physical_type_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=physical_options,
            starting_option=starting_option,
            relative_rect=pygame.Rect(140, y, width - 160, 28),
            manager=self.ui_manager,
            container=self.panel
        )
        y += 32

        return y

    def _create_government_section(self, y: int, width: int) -> int:
        """Create government controls."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 200, 25),
            text="Government:",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#section_header"
        )
        y += 28

        # Government Type
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 120, 22),
            text="Type:",
            manager=self.ui_manager,
            container=self.panel
        )
        gov_options = [self.EMPTY_OPTION] + list(GOVERNMENT_TYPES)
        starting_gov = self.race_config.government_type if self.race_config.government_type else self.EMPTY_OPTION
        self.government_type_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=gov_options,
            starting_option=starting_gov,
            relative_rect=pygame.Rect(140, y, width - 160, 28),
            manager=self.ui_manager,
            container=self.panel
        )
        y += 32

        # Government Organization
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 120, 22),
            text="Organization:",
            manager=self.ui_manager,
            container=self.panel
        )
        org_options = [self.EMPTY_OPTION] + list(GOVERNMENT_ORGANIZATIONS)
        starting_org = self.race_config.government_organization if self.race_config.government_organization else self.EMPTY_OPTION
        self.government_org_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=org_options,
            starting_option=starting_org,
            relative_rect=pygame.Rect(140, y, width - 160, 28),
            manager=self.ui_manager,
            container=self.panel
        )
        y += 32

        # Leader Title
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 120, 22),
            text="Leader Title:",
            manager=self.ui_manager,
            container=self.panel
        )
        title_options = [self.EMPTY_OPTION] + list(LEADER_TITLES)
        starting_title = self.race_config.leader_title if self.race_config.leader_title else self.EMPTY_OPTION
        self.leader_title_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=title_options,
            starting_option=starting_title,
            relative_rect=pygame.Rect(140, y, width - 160, 28),
            manager=self.ui_manager,
            container=self.panel
        )
        y += 32

        # Society Type
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 120, 22),
            text="Society Type:",
            manager=self.ui_manager,
            container=self.panel
        )
        society_options = [self.EMPTY_OPTION] + list(SOCIETY_TYPES)
        starting_society = self.race_config.society_type if self.race_config.society_type else self.EMPTY_OPTION
        self.society_type_dropdown = pygame_gui.elements.UIDropDownMenu(
            options_list=society_options,
            starting_option=starting_society,
            relative_rect=pygame.Rect(140, y, width - 160, 28),
            manager=self.ui_manager,
            container=self.panel
        )
        y += 32

        return y

    def _create_faction_section(self, y: int, width: int) -> int:
        """Create faction name controls."""
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(10, y, 200, 25),
            text="Faction:",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#section_header"
        )
        y += 28

        # Faction Name
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, 120, 22),
            text="Faction Name:",
            manager=self.ui_manager,
            container=self.panel
        )
        self.faction_name_input = pygame_gui.elements.UITextEntryLine(
            relative_rect=pygame.Rect(140, y, width - 160, 28),
            manager=self.ui_manager,
            container=self.panel,
            placeholder_text="e.g., Rossarian Empire"
        )
        if self.race_config.faction_name:
            self.faction_name_input.set_text(self.race_config.faction_name)
            # Check if faction matches auto-generated
            auto = self._auto_generate_faction_name(
                self.race_config.race_name,
                self.race_config.government_type
            )
            self._faction_name_overridden = (self.race_config.faction_name != auto)
        y += 32

        # Help text
        pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, y, width - 40, 20),
            text="Auto-generated from Species Name + Government Type. Edit to override.",
            manager=self.ui_manager,
            container=self.panel,
            object_id="#help_text"
        )
        y += 24

        return y

    def _auto_generate_faction_name(self, race_name: str, government_type: str) -> str:
        """
        Auto-generate faction name from race name and government type.

        Args:
            race_name: Species name
            government_type: Government type (e.g., "Empire")

        Returns:
            Combined faction name or components if only one set
        """
        race_name = race_name.strip() if race_name else ""
        government_type = government_type.strip() if government_type else ""

        if race_name and government_type:
            return f"{race_name} {government_type}"
        elif race_name:
            return race_name
        elif government_type:
            return government_type
        else:
            return ""

    def _update_faction_if_not_overridden(self, race_name: str, government_type: str):
        """
        Update faction name if not manually overridden.

        Args:
            race_name: Current race name
            government_type: Current government type
        """
        if not self._faction_name_overridden and self.faction_name_input:
            auto_name = self._auto_generate_faction_name(race_name, government_type)
            self.faction_name_input.set_text(auto_name)

    def _get_dropdown_value(self, dropdown) -> str:
        """
        Get value from dropdown, handling empty selection.

        Args:
            dropdown: UIDropDownMenu instance

        Returns:
            Selected value or empty string if empty option selected
        """
        if dropdown is None:
            return ""
        selected = dropdown.selected_option
        # pygame_gui returns tuple (display_text, value) or just string
        if isinstance(selected, tuple):
            value = selected[1] if len(selected) > 1 else selected[0]
        else:
            value = selected

        if value == self.EMPTY_OPTION or value == "":
            return ""
        return value

    def update_config(self):
        """Update race_config from UI element values."""
        if self.race_name_input:
            self.race_config.race_name = self.race_name_input.get_text()

        if self.race_name_plural_input:
            self.race_config.race_name_plural = self.race_name_plural_input.get_text()

        if self.faction_name_input:
            self.race_config.faction_name = self.faction_name_input.get_text()

        if self.physical_type_dropdown:
            self.race_config.physical_type = self._get_dropdown_value(self.physical_type_dropdown)

        if self.government_type_dropdown:
            self.race_config.government_type = self._get_dropdown_value(self.government_type_dropdown)

        if self.government_org_dropdown:
            self.race_config.government_organization = self._get_dropdown_value(self.government_org_dropdown)

        if self.leader_title_dropdown:
            self.race_config.leader_title = self._get_dropdown_value(self.leader_title_dropdown)

        if self.society_type_dropdown:
            self.race_config.society_type = self._get_dropdown_value(self.society_type_dropdown)

    def set_from_config(self):
        """Set UI element values from race_config (for loading saved races)."""
        if self.race_name_input:
            self.race_name_input.set_text(self.race_config.race_name or "")

        if self.race_name_plural_input:
            self.race_name_plural_input.set_text(self.race_config.race_name_plural or "")

        if self.faction_name_input:
            self.faction_name_input.set_text(self.race_config.faction_name or "")
            # Check override status
            auto = self._auto_generate_faction_name(
                self.race_config.race_name,
                self.race_config.government_type
            )
            self._faction_name_overridden = (self.race_config.faction_name != auto and self.race_config.faction_name != "")

        # Set dropdowns - need to handle empty values
        self._set_dropdown_value(self.physical_type_dropdown, self.race_config.physical_type)
        self._set_dropdown_value(self.government_type_dropdown, self.race_config.government_type)
        self._set_dropdown_value(self.government_org_dropdown, self.race_config.government_organization)
        self._set_dropdown_value(self.leader_title_dropdown, self.race_config.leader_title)
        self._set_dropdown_value(self.society_type_dropdown, self.race_config.society_type)

    def _set_dropdown_value(self, dropdown, value: str):
        """
        Set dropdown to specific value or empty option.

        Args:
            dropdown: UIDropDownMenu instance
            value: Value to select, or empty string for empty option
        """
        if dropdown is None:
            return

        if not value:
            # Select empty option
            # pygame_gui's UIDropDownMenu needs the option to exist in the list
            dropdown.selected_option = (self.EMPTY_OPTION, self.EMPTY_OPTION)
        else:
            dropdown.selected_option = (value, value)

    def update_labels(self):
        """Update display labels. No-op for this panel (labels are static)."""
        pass

    def handle_event(self, event) -> bool:
        """
        Handle UI events for auto-generation logic.

        Args:
            event: pygame event

        Returns:
            True if event was handled
        """
        # Check for text changes in faction name to detect override
        if event.type == pygame_gui.UI_TEXT_ENTRY_CHANGED:
            if hasattr(event, 'ui_element') and event.ui_element == self.faction_name_input:
                # User manually edited faction name
                self._faction_name_overridden = True
                return True
            elif hasattr(event, 'ui_element') and event.ui_element == self.race_name_input:
                # Race name changed - update faction if not overridden
                if not self._faction_name_overridden:
                    race_name = self.race_name_input.get_text() if self.race_name_input else ""
                    gov_type = self._get_dropdown_value(self.government_type_dropdown)
                    self._update_faction_if_not_overridden(race_name, gov_type)
                return True

        # Check for dropdown changes
        if event.type == pygame_gui.UI_DROP_DOWN_MENU_CHANGED:
            if hasattr(event, 'ui_element') and event.ui_element == self.government_type_dropdown:
                # Government type changed - update faction if not overridden
                if not self._faction_name_overridden:
                    race_name = self.race_name_input.get_text() if self.race_name_input else ""
                    gov_type = self._get_dropdown_value(self.government_type_dropdown)
                    self._update_faction_if_not_overridden(race_name, gov_type)
                return True

        return False
