import math

def check_arc(ship_angle, facing_angle, arc, ship_pos, target_pos):
    print(f"--- Test Case ---")
    print(f"Ship Angle: {ship_angle} (0=Right, 90=Down)")
    print(f"Weapon Facing: {facing_angle} (Relative)")
    print(f"Arc: {arc}")
    print(f"Ship Pos: {ship_pos}")
    print(f"Target Pos: {target_pos}")

    # 1. Global Component Facing
    comp_facing = (ship_angle + facing_angle) % 360
    print(f"Global Comp Facing: {comp_facing}")
    
    # 2. Aim Vector
    aim_vec = (target_pos[0] - ship_pos[0], target_pos[1] - ship_pos[1])
    print(f"Aim Vec: {aim_vec}")
    
    # 3. Aim Angle
    # math.atan2(y, x)
    # In Y-Down: (0, -1) -> -90 = 270.
    aim_angle = math.degrees(math.atan2(aim_vec[1], aim_vec[0])) % 360
    print(f"Aim Angle: {aim_angle}")
    
    # 4. Diff
    diff = (aim_angle - comp_facing + 180) % 360 - 180
    print(f"Diff: {diff:.2f}")
    
    # 5. Check
    pass_check = abs(diff) <= arc
    print(f"Result: {'PASS' if pass_check else 'FAIL'}")
    return pass_check

# Scenario 1: Forward Fire (Working)
# Ship Right(0), Target Right, Weapon Forward(0)
check_arc(0, 0, 45, (0,0), (100, 0))

# Scenario 2: Broadside
# Ship Left (180). Weapon Starboard (90). Total Up (270). Target Up.
check_arc(180, 90, 45, (0,0), (0, -100))

# Scenario 3: Broadside Miss
# Ship Left (180). Weapon Starboard (90). Total Up (270). Target Down.
check_arc(180, 90, 45, (0,0), (0, 100))

# Scenario 4: User Report (90/270)
# Ship Right (0). Weapon 90. Target in Front (Right).
# This SHOULD Fail.
check_arc(0, 90, 45, (0,0), (100, 0))
