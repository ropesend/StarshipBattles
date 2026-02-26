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
RESOURCE_BIOMASS = (100, 255, 100)  # Green (domain-specific)

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

# === Common UI Constants ===
TEXT_SECONDARY = (180, 180, 180)    # Label/stat text
TEXT_ITEM = (200, 200, 200)         # List item text, neutral content
BAR_BG = (40, 40, 40)               # Progress bar / banner dark fill
BAR_BORDER = (80, 80, 80)           # Progress bar outline
BG_PANEL_DARK = (20, 25, 35)        # Dark panel backgrounds
BG_ROW_ALT = (35, 35, 45)           # Alternating row background
BG_ITEM = (40, 40, 50)              # List item / tag background
BORDER_PANEL = (60, 60, 80)         # Panel divider lines
GRID_LINE = (45, 45, 55)            # Grid/separator lines
GRID_BG = (30, 30, 40)              # Grid/card backgrounds

# === Team Colors (Battle/Setup) ===
TEAM_1_TEXT = (100, 200, 255)       # Team 1 titles, accents
TEAM_1_BG = (30, 50, 70)            # Team 1 item backgrounds
TEAM_1_BANNER_BG = (40, 60, 80)     # Team 1 banner/header background
TEAM_1_BORDER = (100, 150, 200)     # Team 1 borders
TEAM_2_TEXT = (255, 100, 100)       # Team 2 titles, accents
TEAM_2_BG = (70, 30, 30)            # Team 2 item backgrounds
TEAM_2_BANNER_BG = (80, 40, 40)     # Team 2 banner/header background
TEAM_2_BORDER = (200, 100, 100)     # Team 2 borders

# === Battle Status ===
STATUS_ACTIVE_TEXT = (255, 255, 100)    # Active entity text
STATUS_ACTIVE_BG = (50, 50, 60)         # Active entity background
STATUS_HIT_TEXT = (50, 255, 50)         # Hit confirmed text
STATUS_DESTROYED_TEXT = (255, 50, 50)   # Destroyed text (same as HP_CRITICAL)
STATUS_DERELICT = (255, 165, 0)         # Derelict/orange alert
SEEKER_TITLE = (255, 200, 100)          # Seeker monitor title
DAMAGE_TEXT = (255, 150, 150)           # Damage amount text
TARGET_TEXT = (150, 200, 150)           # Target info text

# === Button Colors ===
BTN_NEUTRAL_BG = (60, 60, 80)
BTN_NEUTRAL_BORDER = (100, 100, 150)
BTN_NEUTRAL_TEXT = (200, 200, 255)
BTN_DANGER_BG = (50, 30, 30)
BTN_DANGER_HOVER = (60, 40, 40)
BTN_DANGER_BORDER = (100, 60, 60)
BTN_DANGER_TEXT = (255, 150, 150)
BTN_PRIMARY_BG = (50, 150, 50)
BTN_PRIMARY_BORDER = (100, 200, 100)
BTN_DISABLED_BG = (50, 50, 50)
BTN_RETURN_BG = (0, 100, 150)
BTN_RETURN_HOVER = (0, 150, 200)
BTN_END_BG = (80, 40, 40)
BTN_END_BORDER = (150, 80, 80)
BTN_END_TEXT = (255, 200, 200)
BTN_VICTORY_BG = (50, 80, 120)
BTN_VICTORY_BORDER = (100, 150, 200)

# === Component Status ===
COMPONENT_NO_POWER = (255, 255, 0)      # No power status yellow
COMPONENT_NO_FUEL = (255, 100, 0)       # No fuel status orange
COMPONENT_INACTIVE_BG = (100, 50, 50)   # Inactive component dark red bg
WEAPON_STATS_TEXT = (150, 150, 255)     # Weapon S:H stats
SECTION_HEADER_WEAPONS = (200, 200, 150)    # Weapons section header
SECTION_HEADER_COMPONENTS = (200, 200, 100) # Components section header
AI_STRATEGY_TEXT = (150, 200, 150)      # AI strategy name
METADATA_FILE_TEXT = (150, 150, 200)    # Source file path text

# === Setup Screen ===
SETUP_TITLE = (200, 200, 255)
SETUP_LABEL_SHIPS = (150, 150, 200)
SETUP_LABEL_FORMATIONS = (150, 200, 150)
FORMATION_TEXT = (200, 255, 200)
FORMATION_BG = (35, 50, 35)
FORMATION_BORDER = (80, 120, 80)
FORMATION_TEAM_BG = (30, 60, 50)
FORMATION_TEAM_BORDER = (100, 200, 150)
ITEM_BG = (40, 45, 55)
ITEM_BORDER = (80, 80, 100)
DROPDOWN_BG = (30, 30, 40)
DROPDOWN_BUTTON_BG = (40, 60, 90)
DROPDOWN_BUTTON_BORDER = (80, 120, 180)
DROPDOWN_BUTTON_TEXT = (150, 200, 255)
BTN_CLEAR_BG = (120, 50, 50)
BTN_CLEAR_BORDER = (200, 100, 100)
BTN_CLEAR_TEXT = (255, 200, 200)
BTN_QUICK_BG = (80, 50, 120)
BTN_QUICK_BORDER = (150, 100, 200)
BTN_QUICK_TEXT = (220, 200, 255)

# === Strategy Map ===
WARP_LANE = (50, 50, 100)
STAR_LABEL = (200, 200, 200)
FLEET_SELECTED = (255, 255, 0)
PATH_MOVE = (0, 255, 100)
PATH_WARP = (255, 50, 50)
PATH_LABEL = (200, 200, 255)
OVERLAY_PROCESSING = (255, 200, 0)
WARPPOINT_FALLBACK = (200, 0, 255)
DYSON_FALLBACK = (0, 200, 200)
PLANET_FALLBACK = (100, 100, 100)

# === Storm Effects ===
STORM_ION = (100, 150, 255)
STORM_PLASMA = (255, 100, 100)
STORM_GRAVITATIONAL = (180, 100, 255)
STORM_RADIATION = (255, 255, 100)
STORM_DARK_NEBULA = (150, 150, 150)

# === Star Spectrum ===
SPECTRUM_GAMMA = (200, 0, 255)
SPECTRUM_XRAY = (148, 0, 211)
SPECTRUM_UV = (75, 0, 130)
SPECTRUM_BLUE = (0, 0, 255)
SPECTRUM_GREEN = (0, 255, 0)
SPECTRUM_RED = (255, 0, 0)
SPECTRUM_INFRARED = (139, 0, 0)
SPECTRUM_MICROWAVE = (160, 82, 45)
SPECTRUM_RADIO = (128, 128, 128)

# === Atmospheric Gases ===
GAS_N2 = (173, 216, 230)
GAS_O2 = (0, 0, 255)
GAS_CO2 = (100, 100, 100)
GAS_H2O = (0, 0, 139)
GAS_CH4 = (255, 165, 0)
GAS_H2 = (255, 192, 203)
GAS_HE = (255, 255, 255)
GAS_AR = (128, 0, 128)
GAS_SO2 = (255, 255, 0)
GAS_UNKNOWN = (100, 150, 100)

# === Planet Types ===
PLANET_CONTINENTAL = (70, 130, 70)
PLANET_ARID = (180, 140, 80)
PLANET_PELAGIC = (50, 80, 180)
PLANET_MAGMA = (200, 50, 30)
PLANET_CRYO = (180, 200, 220)
PLANET_BARREN = (130, 130, 130)
PLANET_JOVIAN = (200, 160, 100)
PLANET_ICE_GIANT = (100, 150, 200)
PLANET_CHTHONIAN = (100, 80, 60)
PLANET_ICE_DWARF = (200, 210, 230)
PLANET_PLANETOID = (90, 90, 90)
PLANET_TERRESTRIAL = (100, 150, 200)
PLANET_GAS_GIANT = (200, 150, 100)
PLANET_ICE = (150, 200, 255)
PLANET_ROCKY = (150, 100, 80)
PLANET_OCEANIC = (50, 100, 200)

# === Vehicle Types ===
VEHICLE_SHIP = (80, 100, 180)
VEHICLE_FIGHTER = (180, 180, 80)
VEHICLE_STATION = (180, 100, 80)
VEHICLE_COMPLEX = (80, 180, 100)

# === Resource Placeholders ===
RESOURCE_METALS = (192, 192, 192)
RESOURCE_ORGANICS = (80, 180, 80)
RESOURCE_VAPORS = (100, 150, 220)
RESOURCE_RADIOACTIVES = (220, 180, 50)
RESOURCE_EXOTICS = (180, 80, 200)

# === Battle HUD ===
SPEED_PAUSED = (255, 100, 100)
SPEED_SLOWMO = (255, 200, 100)
SPEED_FAST = (100, 255, 100)
HUD_TEXT = (180, 180, 180)
HUD_ZOOM_TEXT = (150, 200, 255)

# === Battle Grid/Overlay ===
GRID_BG_BATTLE = (30, 30, 50)           # Battle grid lines
DEBUG_TARGET_LINE = (0, 0, 255)         # Target indicator line (blue)
DEBUG_WEAPON_RANGE = (100, 100, 100)    # Weapon range circle
DEBUG_AIM_POINT = (0, 100, 255)         # Aim point indicator
DEBUG_FIRING_ARC = (255, 165, 0)        # Firing arc lines (orange)

# === Test Complete UI ===
TEST_COMPLETE_PASSED = (80, 255, 120)   # Green for passed
TEST_COMPLETE_FAILED = (255, 80, 80)    # Red for failed
TEST_COMPLETE_NEUTRAL = (255, 200, 100) # Yellow for neutral
RESULT_WIN = (0, 255, 0)                # Win result text
RESULT_DRAW = (255, 255, 0)             # Draw result text

# === Diff Viewer ===
DIFF_CHANGED_BG = (60, 50, 20)
DIFF_CHANGED_TEXT = (255, 220, 100)
DIFF_ADDED_BG = (20, 50, 30)
DIFF_ADDED_TEXT = (100, 255, 150)
DIFF_REMOVED_BG = (50, 20, 20)
DIFF_REMOVED_TEXT = (255, 120, 120)
VIEWER_BTN_BG = (80, 80, 100)
VIEWER_BTN_HOVER = (100, 100, 130)
VIEWER_BTN_BORDER = (120, 120, 140)

# === Formation Editor ===
FORMATION_GRID = (45, 45, 55)
FORMATION_AXIS = (60, 60, 70)
FORMATION_ARROW = (100, 200, 255)
FORMATION_ARROW_SELECTED = (255, 255, 100)
FORMATION_FIXED = (100, 255, 100)
FORMATION_FIXED_SELECTED = (200, 255, 200)

# === Weapon Renderer ===
WEAPON_BAR_BEAM = (40, 80, 40)
WEAPON_BAR_PROJECTILE = (80, 60, 40)
WEAPON_BAR_SEEKER = (80, 40, 80)
WEAPON_ACCURACY_HIGH = (0, 200, 0)
WEAPON_ACCURACY_MED = (200, 100, 0)
WEAPON_ACCURACY_LOW = (200, 50, 50)
WEAPON_LABEL = (200, 200, 100)
WEAPON_RANGE_LABEL = (150, 150, 200)
WEAPON_ARC = (200, 150, 50)

# === JSON Viewer / Scrollable Panel ===
JSON_BG = (25, 25, 30)                  # Panel background
JSON_BORDER = (80, 80, 100)             # Panel border
JSON_TITLE_BG = (40, 40, 50)            # Title bar background
JSON_TITLE_TEXT = (220, 220, 255)       # Title text
JSON_KEY = (156, 220, 254)              # Key names (light blue)
JSON_STRING = (206, 145, 120)           # String values (orange-brown)
JSON_NUMBER = (181, 206, 168)           # Number values (green)
JSON_BOOL = (86, 156, 214)              # Boolean values (blue)
JSON_NULL = (86, 156, 214)              # Null values (blue)
JSON_BRACKET = (180, 180, 180)          # Brackets/braces (gray)
SCROLLBAR_TRACK = (50, 50, 60)          # Scrollbar track
SCROLLBAR_THUMB = (100, 100, 120)       # Scrollbar thumb (same as BORDER_LIGHT)
SCROLLBAR_THUMB_ACTIVE = (120, 120, 140)  # Scrollbar thumb when dragging

# === Modifier Impact Grid ===
MODIFIER_HEADER_BG = (40, 40, 50)       # Column header background
MODIFIER_ROW_BG = (30, 30, 40)          # Row background
MODIFIER_ROW_ALT_BG = (35, 35, 45)      # Alternating row background
MODIFIER_FOOTER_BG = (50, 50, 60)       # Footer (net values) background
MODIFIER_BUFF = (100, 255, 100)         # Green for positive effects
MODIFIER_DEBUFF = (255, 100, 100)       # Red for negative effects
MODIFIER_NEUTRAL = (180, 180, 180)      # Gray for neutral

# === Ship Stats Renderer ===
WEAPON_INACTIVE = (150, 50, 50)         # Inactive weapon text
WEAPON_INACTIVE_STATUS = (255, 100, 100)  # Inactive weapon status
CREW_LOW = (255, 100, 100)              # Low crew warning
