# Loader Class Analyst Report (Module Specialist)

## Summary
- Total loader/parser classes found: 12
- Using json_utils: 9 (75%)
- Using direct json: 1 (WorkshopDataLoader)
- Delegating to other loaders: 1 (RegistryLoader)
- Not JSON (image loading): 1 (RaceAssetLoader — out of scope)
- Approximate duplicate code: 200-300 lines

## Findings

### MAJOR: Path Resolution Duplication
**ID:** LDR-001
**Location:** Multiple loaders across `game/strategy/generation/loaders/`, `game/simulation/services/`
**Issue:** 3+ loaders implement their own path resolution logic (relative vs absolute, existence checking, fallback paths).
**Impact:** Inconsistent path handling, duplicated code.
**Recommendation:** Add `resolve_path()` utility to json_utils or create shared helper.
**Effort:** Medium

### MAJOR: File Discovery Pattern Duplication
**ID:** LDR-002
**Location:** `game/ui/screens/workshop_data_loader.py`, `game/simulation/services/registry_loader.py`, `game/simulation/systems/tech_preset_loader.py`
**Issue:** 3 loaders implement `test_` prefix fallback file discovery independently (~30 lines each, ~90 total).
**Impact:** Duplicated logic, risk of inconsistent behavior.
**Recommendation:** Extract shared `find_file_with_test_prefix()` utility.
**Effort:** Medium

### MINOR: Schema Validation Duplication
**ID:** LDR-003
**Location:** `game/strategy/generation/loaders/astrophysics_loader.py`, `game/strategy/generation/loaders/system_blueprints_loader.py`, `game/simulation/entities/ship_loader.py`
**Issue:** 5+ loaders implement required-key/required-section validation independently.
**Impact:** Duplicated validation logic.
**Recommendation:** Extract `validate_required_keys()` utility.
**Effort:** Simple

### MINOR: WorkshopDataLoader Bypasses json_utils
**ID:** LDR-004
**Location:** `game/ui/screens/workshop_data_loader.py`
**Issue:** Complex orchestration loader uses direct json import and custom file discovery instead of json_utils.
**Impact:** Inconsistent with rest of codebase.
**Recommendation:** Migrate file I/O to json_utils while keeping orchestration logic.
**Effort:** Medium

### INFO: Inconsistent Return Types Across Loaders
**ID:** LDR-005
**Location:** All loader classes
**Issue:** Return types vary: `Dict[str, Any]`, `Tuple[Optional[Ship], str]`, `LoadResult` dataclass, exceptions raised.
**Impact:** No unified loader contract. Each consumer must know specific loader's return convention.
**Recommendation:** Document (not necessarily unify — different return types may be appropriate for different contexts).
**Effort:** Simple

## Loader Inventory

### 1. AstrophysicsLoader
- **File:** `game/strategy/generation/loaders/astrophysics_loader.py`
- **Loads:** Physics parameters for planet classification
- **Uses json_utils:** Yes (`load_json_required`)
- **Validation:** Comprehensive schema validation
- **Code size:** ~150 lines

### 2. GalaxyLayoutsLoader
- **File:** `game/strategy/generation/loaders/galaxy_layouts_loader.py`
- **Loads:** Galaxy layout configurations
- **Uses json_utils:** Yes (`load_json_required`)
- **Validation:** Required key check
- **Code size:** ~174 lines
- **Special:** Static methods, includes scaling logic

### 3. SystemBlueprintsLoader
- **File:** `game/strategy/generation/loaders/system_blueprints_loader.py`
- **Loads:** Star system blueprint templates
- **Uses json_utils:** Yes (`load_json_required`)
- **Validation:** Comprehensive blueprint validation
- **Code size:** ~175 lines

### 4. WorkshopDataLoader
- **File:** `game/ui/screens/workshop_data_loader.py`
- **Loads:** Components, modifiers, strategies, vehicle classes
- **Uses json_utils:** NO — uses direct `json` import
- **Validation:** File existence checking with priority fallback
- **Code size:** ~218 lines
- **Special:** Complex orchestration, priority-based file discovery

### 5. RaceAssetLoader (OUT OF SCOPE)
- **File:** `game/ui/screens/race_asset_loader.py`
- **Loads:** Race visual assets (PNG/JPG) — NOT JSON
- **Uses json_utils:** N/A
- **Code size:** ~277 lines

### 6. SimulationDesignLoader
- **File:** `game/simulation/services/design_loader.py`
- **Loads:** Ship designs into Ship objects
- **Uses json_utils:** Yes (`load_json_required`)
- **Validation:** Delegated to Ship.from_dict()
- **Code size:** ~130 lines

### 7. TechPresetLoader
- **File:** `game/simulation/systems/tech_preset_loader.py`
- **Loads:** Technology presets
- **Uses json_utils:** Yes (`load_json_required`)
- **Validation:** Glob-based existence checking
- **Code size:** ~204 lines
- **Special:** All static methods

### 8. RegistryLoader
- **File:** `game/simulation/services/registry_loader.py`
- **Loads:** All registry data (orchestrator)
- **Uses json_utils:** Indirectly (delegates to other loaders)
- **Validation:** Directory existence checking
- **Code size:** ~123 lines

### 9-10. Component Loading Functions
- **File:** `game/simulation/components/component.py`
- **Loads:** Component definitions, modifier definitions
- **Uses json_utils:** Yes (`load_json_required`)
- **Validation:** Schema validation + instantiation
- **Code size:** ~191 lines combined

### 11. Ship/Vehicle Loading
- **File:** `game/simulation/entities/ship_loader.py`
- **Loads:** Vehicle class definitions
- **Uses json_utils:** Yes (`load_json`, `load_json_required`)
- **Validation:** Layer resolution, deep copying
- **Code size:** ~138 lines

### 12. Resource Loading
- **File:** `game/core/resources.py`
- **Loads:** Resource type definitions
- **Uses json_utils:** Yes (`load_json_required`)
- **Validation:** Schema validation (dict, id key)
- **Code size:** ~100 lines

## Comparison Matrix

| Loader | Uses json_utils | Error Handling | Validation | Lines | Migration Need |
|--------|-----------------|----------------|------------|-------|---------------|
| AstrophysicsLoader | Yes | Raises | Comprehensive | ~150 | None |
| GalaxyLayoutsLoader | Yes | Raises | Basic | ~174 | None |
| SystemBlueprintsLoader | Yes | Raises | Comprehensive | ~175 | None |
| WorkshopDataLoader | **No** | Returns result | File existence | ~218 | **Migrate to json_utils** |
| SimulationDesignLoader | Yes | Type-specific | Delegated | ~130 | None |
| TechPresetLoader | Yes | Raises | Glob-based | ~204 | None |
| RegistryLoader | Indirect | Per-loader | Dir check | ~123 | None |
| Component loading | Yes | Comprehensive | Schema + instantiation | ~191 | None |
| Ship/Vehicle loading | Yes | Raises | Layer resolution | ~138 | None |
| Resource loading | Yes | Comprehensive | Schema | ~100 | None |

## BaseJSONLoader Recommendation

### Assessment: **Option B — "Just use json_utils" is sufficient**

**Rationale:**
1. **9 of 11 JSON loaders already use json_utils** — the pattern is established
2. The loaders vary significantly in post-processing (scaling, instantiation, caching, orchestration)
3. A base class would need so many extension points that it adds complexity without reducing code
4. The shared patterns (path resolution, file discovery, schema validation) are better as **utility functions** than class inheritance

### Recommended Actions:
1. **Migrate WorkshopDataLoader** to use json_utils for actual file I/O
2. **Extract utility functions** (not a base class):
   - `find_file_with_test_prefix()` — shared by 3 loaders
   - `validate_required_keys()` — shared by 5+ loaders
3. **Do NOT create BaseJSONLoader** — the overhead isn't justified for loaders that are already well-standardized

### Expected Impact:
- Eliminate ~150 lines of duplicate code via shared utility functions
- Improve consistency without adding architectural complexity
- Keep json_utils as the canonical JSON file I/O layer
