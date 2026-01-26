import unittest
import math
from formula_system import evaluate_math_formula

class TestFormulaSystem(unittest.TestCase):
    
    def test_basic_math(self):
        context = {}
        self.assertEqual(evaluate_math_formula("1 + 1", context), 2)
        self.assertEqual(evaluate_math_formula("2 * 5", context), 10)
        self.assertEqual(evaluate_math_formula("10 / 2", context), 5.0)

    def test_math_functions(self):
        context = {}
        self.assertEqual(evaluate_math_formula("sqrt(16)", context), 4.0)
        self.assertEqual(evaluate_math_formula("pow(2, 3)", context), 8.0)
        self.assertLess(abs(evaluate_math_formula("sin(0)", context) - 0.0), 0.001)
        self.assertLess(abs(evaluate_math_formula("cos(0)", context) - 1.0), 0.001)

    def test_context_variables(self):
        context = {'x': 10, 'y': 20}
        self.assertEqual(evaluate_math_formula("x + y", context), 30)
        self.assertEqual(evaluate_math_formula("x * 2", context), 20)

    def test_error_handling(self):
        context = {}
        # Should return 0 on error
        self.assertEqual(evaluate_math_formula("undefined_var", context), 0)
        self.assertEqual(evaluate_math_formula("1 / 0", context), 0)
        self.assertEqual(evaluate_math_formula("invalid syntax ??", context), 0)

if __name__ == '__main__':
    unittest.main()
