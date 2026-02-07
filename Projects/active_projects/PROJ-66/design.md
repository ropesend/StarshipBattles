# PROJ-66: Design Document

> **THIS IS A REFERENCE DOCUMENT**
> Do not modify during implementation. Refer to this for architecture decisions.
> If you discover something that contradicts this document, add a note to decisions.md.

## Initial Analysis

### Current Race Setup Architecture
The Race Setup system follows a clean extracted-panel architecture (from PROJ-12):
- `RaceSetupScreen` (UIWindow) orchestrates 5 tab panels
- Each panel is an extracted class in `game/ui/panels/race_*.py`
- Panels share a `race_config: RaceConfig` reference for direct read/write
- Three-method contract: `update_config()`, `update_labels()`, `set_from_config()`
- Validation delegated to `RaceValidator`
- Persistence delegated to `RaceLibrary`

### Current RaceConfig Fields
- Identity: `race_id`, `name`
- Visual: `flag_id`, `portrait_id`, `theme_id`
- Environmental: `gravity_ideal/tolerance`, `temperature_ideal/tolerance`, `atmosphere_preferences`, `radiation_tolerance`
- Descriptive: `bio_description`, `socio_description`
- Timestamps: `created_date`, `modified_date`

### Data Flow
RaceConfig → RaceLibrary (JSON) → NewGameSetupScreen → PlayerConfig → GameSession → Empire
Only visual fields (`flag_id`, `portrait_id`, `theme_id`) propagate to Empire. Environmental data stays in race JSON files.

## Swarm Findings Summary

### Architecture
- Window size is 1800x1200 — 7 tabs yields ~252px per tab (comfortable)
- Tab width is dynamically calculated: `(content_width - 10) // num_tabs`
- Scrolling container pattern already proven in Ships tab
- UIDropDownMenu is available in pygame_gui but not yet used in race screens
- Panel height is `content_height - 130` (room for tabs + bottom buttons)

### Key Patterns to Reuse
- **Extracted Panel**: `game/ui/panels/race_environment_panel.py` — constructor(panel, manager, race_config) + 3 methods
- **Slider + Label**: `race_environment_panel.py:95-152` — slider with value display label and formatting
- **Gallery Button Grid**: `race_flag_gallery.py` — scrollable grid of selectable buttons
- **Tab Navigation**: `race_setup_screen.py:154-170` — dynamic tab buttons with index storage
- **Dropdown Selection**: `new_game_setup_screen.py:105-111` — UIDropDownMenu with event handling
- **Event Routing**: `race_setup_screen.py:780-835` — cascading event type checks with delegation

### Dependencies & Risks
1. **RaceConfig serialization** — All new fields must be in `to_dict()`/`from_dict()` with sensible defaults for backward compatibility
2. **Test fixture updates** — `test_emp1.json` and `test_emp2.json` need new fields added
3. **Validation complexity** — New required vs optional fields need clear definition
4. **Point-buy system is novel** — No existing budget allocation UI pattern; must design from scratch
5. **Homeworld presets** — Need data file mapping PlanetType → default environment values

### Opportunities Discovered
- Environmental preferences currently unused in gameplay — this project lays groundwork for colonization mechanics
- Point-buy system creates natural race balancing mechanism
- Government/Society types create framework for future gameplay modifiers

## Design Decisions

### New RaceConfig Fields

#### Identity Fields (stored, UI-only for now)
| Field | Type | Default | Validation |
|-------|------|---------|------------|
| `faction_name` | str | "" | Auto-generated from race_name + government_type, or manual override |
| `race_name` | str | "" | Required, 1-50 chars (replaces current `name` field semantics) |
| `race_name_plural` | str | "" | Optional, 1-50 chars |
| `government_type` | str | "" | Must be from GOVERNMENT_TYPES list |
| `government_organization` | str | "" | Must be from GOVERNMENT_ORGANIZATIONS list |
| `leader_title` | str | "" | Must be from LEADER_TITLES list |
| `physical_type` | str | "" | Must be from PHYSICAL_TYPES list |
| `society_type` | str | "" | Must be from SOCIETY_TYPES list |

#### Homeworld & Environment Fields
| Field | Type | Default | Validation |
|-------|------|---------|------------|
| `homeworld_type` | str | "" | Must be valid PlanetType name |
| `water_ideal` | float | 0.5 | 0.0-1.0 (fraction of surface) |
| `water_tolerance` | float | 0.2 | 0.0-1.0 |

#### Aptitude Fields (point-buy)
| Field | Type | Default | Range |
|-------|------|---------|-------|
| `aptitude_strength` | int | 5 | 1-10 |
| `aptitude_intelligence` | int | 5 | 1-10 |
| `aptitude_constitution` | int | 5 | 1-10 |
| `aptitude_dexterity` | int | 5 | 1-10 |
| `aptitude_tolerance_other_species` | int | 5 | 1-10 |
| `aptitude_cooperation` | int | 5 | 1-10 |
| `aptitude_happiness` | int | 5 | 1-10 |
| `aptitude_population_growth` | int | 5 | 1-10 |
| `aptitude_conflict_tolerance` | int | 5 | 1-10 |

### Point-Buy Budget System
- **Total budget**: Configurable (suggest 100 points to start)
- **Aptitude costs**: Each point in an aptitude costs 1 point (linear, simple)
- **Tolerance costs**: Each step of environmental tolerance width costs exponentially: `cost = 2^step` (doubling)
- **Setting ideal center**: Free (no cost to choose where you prefer)
- **Display**: Remaining points shown prominently at top of Aptitudes tab
- **Validation**: Cannot save if over budget; warn if significantly under budget

### Homeworld Presets (derived from planet generation data)
Each PlanetType maps to default environment slider values:

| PlanetType | Gravity (g) | Temp (K) | Water % | Radiation | Key Atmosphere |
|------------|-------------|----------|---------|-----------|----------------|
| CONTINENTAL | 1.0 | 293 | 0.60 | 0 | O2: +50, N2: +30 |
| ARID | 1.0 | 320 | 0.10 | +20 | CO2: +30, N2: +20 |
| PELAGIC | 0.9 | 290 | 0.95 | -10 | O2: +50, N2: +30, H2O vapor |
| MAGMA | 1.2 | 800 | 0.0 | +60 | SO2/CO2 dominant |
| CRYOPLANET | 0.8 | 200 | 0.30 (ice) | +10 | CO2/N2 thin |
| BARREN | 0.6 | 350 | 0.0 | +80 | None (vacuum) |
| JOVIAN | 2.5 | 200 | 0.0 | +40 | H2: +80, He: +60 |
| ICE_GIANT | 1.5 | 100 | 0.0 | +20 | H2: +50, He: +40, CH4: +30 |
| CHTHONIAN | 2.0 | 900 | 0.0 | +90 | Trace only |
| ICE_DWARF | 0.1 | 100 | 0.80 (ice) | +10 | None/Trace |
| PLANETOID | 0.05 | 250 | 0.0 | +50 | None |

### Tab Layout (7 tabs)
```
[Summary] [Identity] [Visuals] [Ships] [Environment] [Aptitudes] [Descriptions]
```

- **Summary**: Landing page showing all selections (read-only preview)
- **Identity**: Faction Name, Race Name, Race Name Plural, Government Type, Government Organization, Leader Title, Physical Type, Society Type — mostly dropdowns + text inputs
- **Visuals**: Flag + Portrait selection (unchanged)
- **Ships**: Ship theme selection (unchanged)
- **Environment**: Existing gravity/temp/radiation/atmosphere sliders + NEW water ideal/tolerance + homeworld type dropdown (sets initial values)
- **Aptitudes**: Point-buy stat sliders with remaining budget display + environmental tolerance budget
- **Descriptions**: Bio/Socio text areas (unchanged)

### Constant Lists (stored as module-level constants in race_config.py)

```python
GOVERNMENT_TYPES = [
    "Empire", "Hegemony", "Alliance", "Oligarchy", "Confederation",
    "Protectorate", "Consortium", "Federation", "Commonwealth",
    "Imperium", "Hive", "Clan", "Society", "Collective"
]

GOVERNMENT_ORGANIZATIONS = [
    "Anarchy", "Democracy", "Dictatorship", "Monarchy", "Theocracy",
    "Oligarchy", "Republic", "Feudalism", "Communism", "Totalitarianism",
    "Corporate", "Hive Mind", "Collective"
]

LEADER_TITLES = [
    "Central Speaker", "Chairman", "Chairwoman", "Chancellor", "Czar",
    "Director", "Duke", "Duchess", "Emperor", "Empress", "Grand Admiral",
    "Grand Lord", "High Priest", "High Priestess", "High Regent", "Kaiser",
    "King", "Omnicron", "Praetor", "Premier", "President", "Prime Minister",
    "Prince", "Princess", "Queen", "Triumvir", "Warlord"
]

PHYSICAL_TYPES = [
    "Felinoid", "Caninoid", "Serpentoid", "Ornithoid", "Insectoid",
    "Humanoid", "Reptilian", "Crystalline", "Energy Being", "Symbiotic",
    "Gaseous", "Aquatic", "Mechanoid", "Techno-Organic"
]

SOCIETY_TYPES = [
    "Artisans", "Berserkers", "Engineers", "Farmers", "Industrialists",
    "Mechanics", "Merchants", "Miners", "Neutral", "Politicians",
    "Refiners", "Schemers", "Scientists", "Suppliers", "Traders",
    "Warriors", "Xenophobes"
]
```

See [decisions.md](decisions.md) for the full log with rationale.
