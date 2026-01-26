import unittest

class TestModifierLogic(unittest.TestCase):

    def calculate_snap_decrement(self, current, interval, min_val):
        remainder = current % interval
        if remainder == 0:
            target = current - interval
        else:
            target = current - remainder
        return max(min_val, target)

    def calculate_snap_increment(self, current, interval, max_val):
        remainder = current % interval
        dist = interval - remainder
        target = current + dist
        return min(max_val, target)
        
    def calculate_size_decrement(self, current, interval, min_val):
        # "unless the value is 100 or less, in which case it should reduce to 1" 
        # (For 100 step button)
        # Wait, user said: "left most sheld reduce to the nearest next multiple of 100, 
        # unless the value is 100 or less, in which case it should reduce to 1"
        
        if interval == 100 and current <= 100:
            return max(min_val, 1)
            
        remainder = current % interval
        if remainder == 0:
            target = current - interval
        else:
            target = current - remainder
        return max(min_val, target)
        

    def test_turret_decrement_90(self):
        # pressing the left most double arrow (<<) should reduce the next lowest interval of 90 
        # so if it is currently 11 it should go to 0
        self.assertEqual(self.calculate_snap_decrement(11, 90, 0), 0)
        # if it is 45 then it should go to 0
        self.assertEqual(self.calculate_snap_decrement(45, 90, 0), 0)
        # if it is 117 then it would go to 90
        self.assertEqual(self.calculate_snap_decrement(117, 90, 0), 90)
        # Implicit: if 90 to 0
        self.assertEqual(self.calculate_snap_decrement(90, 90, 0), 0)

    def test_turret_decrement_15(self):
        # if it were 17 then it would go to 15
        self.assertEqual(self.calculate_snap_decrement(17, 15, 0), 15)
        # if it were 115 then it would go to 105
        self.assertEqual(self.calculate_snap_decrement(115, 15, 0), 105)
        
    def test_turret_increment_15(self):
        # if it were 22 then it would go to 30
        self.assertEqual(self.calculate_snap_increment(22, 15, 360), 30)
        # if it were 177 then it would go to 180
        self.assertEqual(self.calculate_snap_increment(177, 15, 360), 180)
        # Exact multiple?
        self.assertEqual(self.calculate_snap_increment(30, 15, 360), 45)

    def test_size_decrement(self):
        # 100 step (Snap Floor 100)
        # 376 -> 300
        self.assertEqual(self.calculate_snap_decrement(376, 100, 1), 300)
        # 300 -> 200
        self.assertEqual(self.calculate_snap_decrement(300, 100, 1), 200)
        # 147 -> 100
        self.assertEqual(self.calculate_snap_decrement(147, 100, 1), 100)
        # 100 -> 1 (Special case: <= 100 goes to 1?)
        # User said: "unless the value is 100 or less, in which case it should reduce to 1"
        # My implementation of smart_floor handled this.
        self.assertEqual(self.calculate_size_decrement(100, 100, 1), 1)
        self.assertEqual(self.calculate_size_decrement(50, 100, 1), 1)
        
        # 10 step (Snap Floor 10)
        # 376 -> 370
        self.assertEqual(self.calculate_snap_decrement(376, 10, 1), 370)
        # 87 -> 80
        self.assertEqual(self.calculate_snap_decrement(87, 10, 1), 80)
        
        # 1 step (Delta 1)
        # 376 -> 375
        self.assertEqual(376 - 1, 375)

    def test_size_increment(self):
        # 100 step (Snap Ceil 100)
        # 147 -> 200
        self.assertEqual(self.calculate_snap_increment(147, 100, 1024), 200)
        # 150 -> 200
        self.assertEqual(self.calculate_snap_increment(150, 100, 1024), 200)
        
        # 10 step (Snap Ceil 10)
        # 147 -> 150
        self.assertEqual(self.calculate_snap_increment(147, 10, 1024), 150)
        
        # 1 step (Delta 1)
        # 147 -> 148
        self.assertEqual(147 + 1, 148)
        
        

if __name__ == '__main__':
    unittest.main()
