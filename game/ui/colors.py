"""UI Colors and Style Constants.

PROJ-113: Moved basic colors (WHITE, BLACK, etc.) from core to UI layer.
PROJ-196: Removed FONT_MAIN - use game.ui.fonts.FONT_MAIN instead.
"""

# Basic colors for UI rendering
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)

# StarshipBattles UI Style Guide Colors
COLORS = {
    # Backgrounds
    'bg_deep': (18, 21, 26),
    'bg_dark': (20, 24, 31),
    'bg_base': (26, 30, 38),
    'bg_elevated': (30, 37, 48),
    'bg_hover': (40, 48, 64),
    'bg_selected': (42, 56, 85),
    
    # Borders
    'border_subtle': (42, 48, 64),
    'border_normal': (42, 53, 69),
    'border_active': (58, 72, 96),
    'border_hover': (85, 170, 238),  # Cyan glow
    'border_selected': (68, 153, 221),
    
    # Text
    'text_disabled': (85, 96, 112),
    'text_muted': (102, 119, 153),
    'text_subtle': (136, 153, 187),
    'text_normal': (154, 171, 204),
    'text_bright': (170, 187, 221),
    'text_highlight': (170, 204, 255),
    'text_hover': (200, 218, 255),
    'text_selected': (255, 255, 255),
    'text_error': (255, 100, 100),
    
    # Accents
    'accent_primary': (68, 136, 221),
    'accent_glow': (85, 170, 238),
    'accent_bright': (102, 187, 255),
}

# === Ship Layer Rendering ===
LAYER_ARMOR = (100, 100, 100)     # Gray
LAYER_OUTER = (200, 50, 50)       # Red
LAYER_INNER = (50, 50, 200)       # Blue
LAYER_CORE = (220, 220, 220)      # Light gray

# === Projectile Colors ===
PROJECTILE_STANDARD = (255, 200, 50)   # Golden yellow
PROJECTILE_MISSILE = (255, 50, 50)     # Red
PROJECTILE_BEAM = (100, 200, 255)      # Light blue

# === HP/Health Status ===
HP_HEALTHY = (0, 255, 0)         # Bright green (>50%)
HP_DAMAGED = (255, 200, 0)       # Yellow (20-50%)
HP_CRITICAL = (255, 50, 50)      # Red (<20%)
HP_DESTROYED = (100, 100, 100)   # Gray (0%)

# === Resource Display ===
RESOURCE_FUEL = (255, 165, 0)    # Orange
RESOURCE_ENERGY = (100, 200, 255)  # Light blue
RESOURCE_AMMO = (200, 200, 100)  # Yellowish
RESOURCE_SHIELD = (0, 200, 255)  # Cyan

# === Research Tree Nodes ===
RESEARCH_LOCKED = (80, 80, 90)       # Gray
RESEARCH_AVAILABLE = (50, 100, 180)  # Blue
RESEARCH_COMPLETED = (50, 140, 60)   # Green
RESEARCH_SELECTED = (200, 180, 50)   # Gold
RESEARCH_LINE_UNMET = (60, 65, 75)   # Dark gray
RESEARCH_LINE_MET = (80, 120, 80)    # Muted green
RESEARCH_LINE_NEGATED = (180, 80, 80)    # Red
RESEARCH_LINE_NEGATED_MET = (100, 60, 60)  # Dark red
RESEARCH_TEXT = (220, 220, 230)      # Off-white
RESEARCH_CHANCE = (255, 220, 100)    # Gold/yellow
RESEARCH_ALLOCATION = (255, 255, 0)  # Bright yellow

# === Test Lab ===
TEST_PASS = (80, 255, 120)      # Bright green
TEST_FAIL = (255, 80, 80)       # Bright red

# === Scene Backgrounds ===
BG_BATTLE = (10, 10, 20)        # Nearly black (battle + app)
BG_GALAXY = (15, 20, 30)        # Deep dark blue
BG_MENU = (20, 20, 30)          # Dark blue-gray

# === Common UI Colors ===
TEXT_LIGHT = (220, 220, 220)    # Primary text
TEXT_MUTED = (150, 150, 150)    # Muted/hint text
TEXT_DIM = (100, 100, 100)      # Dim/disabled text
PANEL_BG = (30, 30, 35)         # Popup/dialog background
BORDER_LIGHT = (100, 100, 120)  # Active borders
BORDER_DARK = (80, 80, 90)      # Standard borders

# === Ship Class Colors (Design Reports) ===
SHIP_CLASS_FIGHTER = (255, 150, 50)   # Orange
SHIP_CLASS_CORVETTE = (100, 200, 100)  # Green
SHIP_CLASS_ESCORT = (100, 150, 255)   # Light blue
SHIP_CLASS_DESTROYER = (255, 100, 100)  # Red
SHIP_CLASS_CRUISER = (200, 100, 255)  # Purple
SHIP_CLASS_BATTLESHIP = (255, 200, 50)  # Yellow
SHIP_CLASS_CARRIER = (150, 255, 200)  # Cyan-green
SHIP_CLASS_DEFAULT = (150, 150, 150)  # Gray

# === Builder Detail Panel (hex for HTML rendering) ===
DETAIL_COMPONENT_NAME = '#FFFF64'   # Yellow-green
DETAIL_COMPONENT_INFO = '#C8C8C8'   # Light gray
DETAIL_TEXT = '#E0E0E0'             # Very light gray

# === Design Stats Panel (hex for HTML rendering) ===
DESIGN_MISSING_REQ = '#ffaa55'     # Orange
DESIGN_REQS_MET = '#88ff88'        # Light green
DESIGN_WARNING = '#ffff88'         # Light yellow
DESIGN_NO_RECS = '#888888'         # Gray

# === Builder Panel Layout ===
BUILDER_ITEM_BG = '#14181f'     # Deep dark
BUILDER_GROUP_BG = '#1a1e26'    # Dark base
BUILDER_TREE_LINE = '#2a3545'   # Dark blue-gray
