"""Test Lab UI Theme Colors.

PROJ-196: Consolidated ~80 inline color tuples from Test Lab files
into a centralized theme module. All Test Lab screens should import
colors from here rather than defining inline tuples.
"""

from game.ui.colors import TEST_PASS, TEST_FAIL


# === Backgrounds ===
BG_PRIMARY = (20, 20, 25)       # Main screen background
BG_PANEL = (25, 25, 30)         # Panel backgrounds
BG_CONTENT = (30, 30, 35)       # Content area / dialog backgrounds
BG_CATEGORY = (35, 35, 40)      # Category buttons / card backgrounds
BG_ITEM_HOVER = (40, 40, 50)    # Hovered item backgrounds
BG_OVERLAY = (40, 40, 45)       # Progress overlay background


# === Borders ===
BORDER = (80, 80, 90)           # Standard borders
BORDER_ACTIVE = (100, 100, 120) # Active/popup borders, scrollbar thumbs


# === Text ===
TEXT = (220, 220, 220)          # Primary text
TEXT_HEADER = (150, 200, 255)   # Header/accent light blue
TEXT_SECONDARY = (140, 140, 160)  # Labels, secondary info
TEXT_EXPECTED = (180, 200, 255)   # Expected values display
TEXT_WHITE = (255, 255, 255)    # Emphasis / button text
TEXT_MUTED = (180, 180, 180)    # Muted info text
TEXT_DIM = (150, 150, 150)      # Dim / hint text
TEXT_LABEL = (140, 140, 160)    # Same as secondary (alias)


# === Status ===
STATUS_PASS = TEST_PASS
STATUS_FAIL = TEST_FAIL
STATUS_WARNING = (255, 200, 80)     # Orange/gold warnings
STATUS_INFO = (120, 120, 200)       # Blue-gray info
STATUS_HIGHLIGHT = (255, 220, 100)  # Gold highlight


# === Tags/Filters ===
TAG_ACTIVE_BG = (40, 80, 40)        # Green active tag background
TAG_ACTIVE_BORDER = (80, 150, 80)   # Green active tag border
TAG_ACTIVE_TEXT = (150, 255, 150)   # Green active tag text
TAG_EXCLUDED_BG = (100, 40, 40)     # Red excluded tag background
TAG_EXCLUDED_BORDER = (180, 80, 80) # Red excluded tag border
TAG_EXCLUDED_TEXT = (255, 150, 150) # Red excluded tag text
TAG_NORMAL_BG = (50, 50, 60)        # Neutral tag background
TAG_NORMAL_BORDER = (100, 100, 110) # Neutral tag border
TAG_NORMAL_TEXT = (180, 180, 180)   # Neutral tag text


# === Tabs ===
TAB_NORMAL = (40, 40, 50)       # Inactive tab
TAB_SELECTED = (60, 80, 120)    # Active tab
TAB_HOVER = (50, 50, 60)        # Hovered tab


# === Selection ===
SELECTED_BG = (0, 100, 200)         # Selected item highlight
SELECTED_CARD_BG = (55, 100, 150)   # Selected card blue tint
SELECTED_BORDER = (100, 150, 255)   # Selected item border


# === Buttons ===
BUTTON_BLUE = (60, 120, 200)        # Standard blue button
BUTTON_BLUE_HOVER = (80, 140, 220)  # Blue button hover
BUTTON_BLUE_BORDER = (100, 140, 200)  # Blue button border
BUTTON_GREEN = (40, 60, 40)         # Green action button
BUTTON_GREEN_HOVER = (60, 80, 60)   # Green button hover
BUTTON_GREEN_BORDER = (80, 120, 80) # Green button border
BUTTON_GREEN_TEXT = (150, 200, 150) # Green button text


# === Scrollbar ===
SCROLLBAR_TRACK = (40, 40, 50)      # Track background
SCROLLBAR_THUMB = (100, 100, 120)   # Thumb color


# === Seed Controls ===
SEED_RANDOM = (100, 100, 100)       # Random seed indicator
SEED_FIXED = (100, 140, 100)        # Fixed seed indicator (green-tinted)
SEED_CUSTOM = (100, 180, 255)       # Custom seed indicator (blue)
SEED_CUSTOM_PENDING = (180, 140, 100)  # Custom seed pending (orange)


# === Section Headers (test info panel) ===
SECTION_CATEGORY = (200, 150, 100)  # Category section (orange)
SECTION_SUMMARY = (100, 200, 150)   # Summary section (green)
SECTION_CONDITIONS = (150, 200, 255)  # Conditions section (blue)
SECTION_EDGE_CASES = (255, 200, 100)  # Edge cases section (orange)
SECTION_OUTCOME = (100, 255, 150)   # Expected outcome (bright green)
SECTION_CRITERIA = (255, 150, 150)  # Pass criteria (pink)
