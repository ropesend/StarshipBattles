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
        # The arrows here should function similarly except with the rounding be to the nearest 10 or 100
        # unless the value is 100 or less, in which case it should reduce to 1
        
        # 100 step
        self.assertEqual(self.calculate_size_decrement(50, 100, 1), 1)
        self.assertEqual(self.calculate_size_decrement(100, 100, 1), 1)
        self.assertEqual(self.calculate_size_decrement(150, 100, 1), 100)
        self.assertEqual(self.calculate_size_decrement(200, 100, 1), 100)
        
        # 10 step
        # "so 87 becomees 80"
        self.assertEqual(self.calculate_size_decrement(87, 10, 1), 80)
        # what if 8? -> 0? min val is 1 (assumed for size)
        self.assertEqual(self.calculate_size_decrement(8, 10, 1), 1) # target 0, max(1, 0) -> 1
        
        

if __name__ == '__main__':
    unittest.main()
