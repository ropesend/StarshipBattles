# Planetary Complex System - Manual Testing Guide

This guide walks through manual testing of the complete planetary complex building system.

## Prerequisites

- StarshipBattles project is set up and running
- Workshop mode is accessible
- Strategy mode with at least one owned colony is accessible

## Test Suite

### 1. Workshop Integration Tests

#### 1.1 Verify Planetary Complex Vehicle Classes
**Steps:**
1. Launch the game in workshop mode
2. Open the vehicle class dropdown (top-left corner)
3. Scroll through the list

**Expected Result:**
- Should see 11 "Planetary Complex (Tier X)" options (Tier 1 through Tier 11)
- Each should be selectable

**Status:** ⬜ Pass / ⬜ Fail

---

#### 1.2 Verify Harvester Components Appear
**Steps:**
1. Select "Planetary Complex (Tier 1)" from vehicle class dropdown
2. Open the component palette (right panel)
3. Scroll through available components

**Expected Result:**
- Should see these 5 harvester components:
  - Metal Harvester
  - Organic Harvester
  - Vapor Harvester
  - Radioactive Harvester
  - Exotic Harvester
- Each should display proper icon and stats

**Status:** ⬜ Pass / ⬜ Fail

---

#### 1.3 Verify Space Shipyard Component
**Steps:**
1. With "Planetary Complex (Tier 1)" selected
2. Look for "Space Shipyard" in component palette

**Expected Result:**
- Space Shipyard component should be visible
- Should show higher mass/cost than harvesters
- Should display proper icon

**Status:** ⬜ Pass / ⬜ Fail

---

#### 1.4 Design a Mining Complex
**Steps:**
1. Select "Planetary Complex (Tier 1)"
2. Place 3 Metal Harvester components on the design grid
3. Set design name to "Mining Complex Mk1"
4. Click "Save Design"

**Expected Result:**
- Design saves successfully
- Message confirms save
- Design appears in designs list (if accessible in workshop)

**Status:** ⬜ Pass / ⬜ Fail

---

#### 1.5 Design a Shipyard Complex
**Steps:**
1. Start new design or clear existing
2. Select "Planetary Complex (Tier 1)"
3. Place 1 Space Shipyard component
4. Set design name to "Space Shipyard Mk1"
5. Click "Save Design"

**Expected Result:**
- Design saves successfully
- Message confirms save

**Status:** ⬜ Pass / ⬜ Fail

---

### 2. Build Queue UI Tests

#### 2.1 Open Build Queue Screen
**Steps:**
1. Launch strategy mode
2. Start or load a game with at least one owned colony
3. Click on an owned planet
4. Verify planet detail panel shows "Build Yard" button
5. Click "Build Yard" button

**Expected Result:**
- Full-screen Build Queue UI opens
- Shows 4 panels:
  - Top: Planet report (name, type, resources, facilities)
  - Left: Available designs list
  - Center: Build queue (currently empty)
  - Right: Category filters and action buttons
- Bottom bar shows "Close" button and current turn number

**Status:** ⬜ Pass / ⬜ Fail

---

#### 2.2 Category Filtering - Complexes
**Steps:**
1. In Build Queue screen
2. Click "Complexes" category button (should be selected by default)
3. Observe designs list on left

**Expected Result:**
- Should see "Mining Complex Mk1" and "Space Shipyard Mk1" (if designs exist)
- Should NOT see any ships, satellites, or fighters

**Status:** ⬜ Pass / ⬜ Fail

---

#### 2.3 Category Filtering - Ships
**Steps:**
1. Click "Ships" category button
2. Observe designs list updates

**Expected Result:**
- Should see only ship designs
- Should NOT see complexes, satellites, or fighters

**Status:** ⬜ Pass / ⬜ Fail

---

#### 2.4 Category Filtering - Satellites & Fighters
**Steps:**
1. Click "Satellites" button - observe list
2. Click "Fighters" button - observe list

**Expected Result:**
- Each category shows only designs matching that vehicle type
- Lists update immediately when switching categories

**Status:** ⬜ Pass / ⬜ Fail

---

#### 2.5 Add Complex to Queue
**Steps:**
1. Switch to "Complexes" category
2. Click on "Mining Complex Mk1" in designs list
3. Click "Add to Queue" button

**Expected Result:**
- Mining Complex appears in center build queue panel
- Shows design name and "5 turns remaining" (or configured value)
- Shows "Type: complex"

**Status:** ⬜ Pass / ⬜ Fail

---

#### 2.6 Add Multiple Items to Queue
**Steps:**
1. Add "Mining Complex Mk1" (if not already added)
2. Switch to "Ships" category
3. Click a ship design
4. Click "Add to Queue"
5. Switch back to "Complexes"
6. Click "Space Shipyard Mk1"
7. Click "Add to Queue"

**Expected Result:**
- All 3 items appear in queue in order added
- Each shows correct name, turns remaining, and type
- Queue is scrollable if items exceed visible area

**Status:** ⬜ Pass / ⬜ Fail

---

#### 2.7 Close Build Queue
**Steps:**
1. Click "Close" button at bottom

**Expected Result:**
- Build Queue screen closes
- Returns to strategy view
- Planet detail panel refreshes
- Build queue persists (will verify in next turn)

**Status:** ⬜ Pass / ⬜ Fail

---

### 3. Turn Processing Tests

#### 3.1 Process One Turn - Decrement Counter
**Steps:**
1. With items in build queue, note first item's "turns remaining"
2. Click "Next Turn" button in strategy view
3. Reopen Build Queue for the same planet

**Expected Result:**
- First item's "turns remaining" decremented by 1
- Item still in queue (not completed yet)
- Other items unchanged

**Status:** ⬜ Pass / ⬜ Fail

---

#### 3.2 Complete Complex Construction
**Steps:**
1. Continue advancing turns until first complex reaches 0 turns
2. After completion turn, reopen Build Queue

**Expected Result:**
- Completed complex removed from queue
- Next item (if any) now at top of queue
- Planet facilities list in top panel shows new facility
- Facility shows with checkmark (✓) indicating operational

**Status:** ⬜ Pass / ⬜ Fail

---

#### 3.3 Verify Facility Appears in Planet Details
**Steps:**
1. Close Build Queue
2. View planet detail panel in strategy screen

**Expected Result:**
- Planet details show "Facilities:" section
- Lists "✓ Mining Complex Mk1" (or design name)

**Status:** ⬜ Pass / ⬜ Fail

---

#### 3.4 Build Multiple Complexes on Same Planet
**Steps:**
1. Reopen Build Queue
2. Add 2 more Mining Complex designs to queue
3. Advance turns until both complete
4. Check planet facilities

**Expected Result:**
- Planet now has 3 facilities total
- Each has unique instance ID (internal)
- All show as operational in facilities list

**Status:** ⬜ Pass / ⬜ Fail

---

### 4. Shipyard Integration Tests

#### 4.1 Try Building Ship Without Shipyard
**Steps:**
1. Select a planet that does NOT have a Space Shipyard facility
2. Open Build Queue
3. Switch to "Ships" category
4. Add a ship design to queue
5. Try to advance turn or close queue

**Expected Result:**
- Ship should remain in queue
- When turn processes, validation may occur
- (Note: Current implementation allows queuing but may need validation at command level)

**Status:** ⬜ Pass / ⬜ Fail / ⬜ N/A (validation deferred)

---

#### 4.2 Build Space Shipyard Complex
**Steps:**
1. On planet without shipyard:
2. Open Build Queue
3. Add "Space Shipyard Mk1" to queue
4. Advance turns until shipyard completes
5. Check planet facilities

**Expected Result:**
- Shipyard appears in facilities list
- Planet detail shows "✓ Space Shipyard Mk1"
- Planet now has_space_shipyard property = True (internal)

**Status:** ⬜ Pass / ⬜ Fail

---

#### 4.3 Build Ship After Shipyard Complete
**Steps:**
1. On planet WITH shipyard facility:
2. Open Build Queue
3. Switch to "Ships" category
4. Add a ship design to queue
5. Advance turns until ship completes

**Expected Result:**
- Ship builds successfully
- Ship spawns as fleet at planet's location
- Fleet appears on strategy map
- Fleet contains ship with design_id matching queued design

**Status:** ⬜ Pass / ⬜ Fail

---

#### 4.4 Verify Multiple Ships Can Build
**Steps:**
1. With shipyard present
2. Add 3 ship designs to queue
3. Advance turns until all complete

**Expected Result:**
- Each ship spawns as separate fleet
- 3 new fleets appear at planet location
- All fleets belong to player empire

**Status:** ⬜ Pass / ⬜ Fail

---

### 5. Backwards Compatibility Tests

#### 5.1 Load Old Savegame
**Steps:**
1. If available, load a savegame from BEFORE this feature was added
2. Select a planet with existing production queue in old format
3. Observe planet details

**Expected Result:**
- Game loads without crashing
- Old queue items (if any) still present
- Old format ["Ship Name", turns] migrates correctly
- Can add new items in new format

**Status:** ⬜ Pass / ⬜ Fail / ⬜ N/A (no old save)

---

#### 5.2 Mixed Queue Format Processing
**Steps:**
1. Manually edit a savegame to have mixed queue:
   ```json
   "construction_queue": [
       ["Colony Ship", 3],
       {"design_id": "mining_complex_mk1", "type": "complex", "turns_remaining": 2}
   ]
   ```
2. Load game and advance turns

**Expected Result:**
- Both items process correctly
- Old format decrements and spawns ship
- New format decrements and spawns complex
- No crashes or errors

**Status:** ⬜ Pass / ⬜ Fail / ⬜ N/A (manual edit)

---

### 6. Edge Case Tests

#### 6.1 Empty Designs Folder
**Steps:**
1. Open Build Queue on a planet
2. If no designs exist in savegame, observe

**Expected Result:**
- Categories still work
- Designs list shows "No designs available"
- Can still switch categories
- "Add to Queue" button does nothing when no design selected

**Status:** ⬜ Pass / ⬜ Fail

---

#### 6.2 Queue with Many Items
**Steps:**
1. Add 10+ items to build queue
2. Observe UI

**Expected Result:**
- Queue panel is scrollable
- All items visible via scrolling
- Performance remains smooth

**Status:** ⬜ Pass / ⬜ Fail

---

#### 6.3 Unowned Planet
**Steps:**
1. Click on an unowned (neutral or enemy) planet
2. Observe detail panel

**Expected Result:**
- "Build Yard" button is hidden (not visible)
- Cannot access build queue for unowned planets

**Status:** ⬜ Pass / ⬜ Fail

---

#### 6.4 Non-Operational Shipyard
**Steps:**
1. Planet with operational shipyard
2. Manually damage facility (set is_operational = False via savegame edit)
3. Reload game
4. Check if ships can still be built

**Expected Result:**
- has_space_shipyard should return False
- Ship building should fail validation (if implemented)
- Facility shows with ✗ instead of ✓

**Status:** ⬜ Pass / ⬜ Fail / ⬜ N/A (manual edit)

---

## Test Summary

**Total Tests:** 27
**Passed:** ___
**Failed:** ___
**N/A:** ___

**Overall Status:** ⬜ All Pass / ⬜ Some Failures

---

## Known Issues

(Document any issues discovered during testing)

---

## Notes

- All automated tests (38 tests) are passing
- Integration tests verify design loading, queue processing, and shipyard detection
- Manual tests verify UI/UX and end-to-end workflow
