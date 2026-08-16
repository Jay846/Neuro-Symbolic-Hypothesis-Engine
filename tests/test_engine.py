import unittest
import numpy as np
import sympy as sp
import os
import sys

# Ensure project root is in path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.executor import validate_and_simplify
from engine.optimizer import fit_parameters
from engine.tree import parse_string_to_tree, mutate_tree

class TestEngineComponents(unittest.TestCase):

    def test_ast_safety_guardrails(self):
        """Verify that AST sandbox allows valid math but blocks malicious code."""
        # 1. Safe math expressions must pass
        safe_exprs = [
            "a * x + b",
            "a * sin(b * x) + c",
            "a * exp(-x / b) + c"
        ]
        for expr in safe_exprs:
            res = validate_and_simplify(expr, ["a", "b", "c"])
            self.assertTrue(res["success"], f"Safe expression failed validation: {expr}")
            self.assertIsNotNone(res["expr"])

        # 2. Malicious or unsafe expressions must be blocked
        unsafe_exprs = [
            "__import__('os').system('echo hack')",
            "eval('1+1')",
            "exec('pass')",
            "a * x + open('secret.txt').read()",
            "compile('1+1', '', 'eval')"
        ]
        for expr in unsafe_exprs:
            res = validate_and_simplify(expr, ["a", "b"])
            self.assertFalse(res["success"], f"Unsafe expression bypassed validation: {expr}")
            self.assertIn("AST verification failed", res["error"])

    def test_parameter_optimizer(self):
        """Verify that SciPy optimizer accurately fits coefficients on synthetic data."""
        # Generate linear data: y = 2.5 * x + 1.8 + noise
        np.random.seed(42)
        x_data = np.linspace(0, 10, 50)
        y_data = 2.5 * x_data + 1.8 + np.random.normal(0, 0.05, len(x_data))

        # Define model equation
        eq_str = "a * x + b"
        val_res = validate_and_simplify(eq_str, ["a", "b"])
        self.assertTrue(val_res["success"])

        # Run parameter fit
        fit_res = fit_parameters(val_res["expr"], ["a", "b"], x_data, y_data)
        self.assertTrue(fit_res["success"])
        self.assertGreater(fit_res["r2"], 0.99)
        
        # Check coefficients are close to target
        self.assertAlmostEqual(fit_res["parameters"]["a"], 2.5, places=1)
        self.assertAlmostEqual(fit_res["parameters"]["b"], 1.8, places=1)

    def test_tree_parsing_and_mutation(self):
        """Verify expression tree parsing, string conversion, and mutations."""
        eq_str = "a * x + b"
        tree_root = parse_string_to_tree(eq_str)
        self.assertIsNotNone(tree_root)
        
        # Verify reconstruction
        reconstructed = tree_root.to_string()
        self.assertIn("a", reconstructed)
        self.assertIn("x", reconstructed)
        self.assertIn("b", reconstructed)

        # Run mutation
        parameters = ["a", "b"]
        mutated_tree = mutate_tree(tree_root, parameters)
        self.assertIsNotNone(mutated_tree)
        
        mutated_str = mutated_tree.to_string()
        # Verify it still compiles to a valid SymPy expression
        val_res = validate_and_simplify(mutated_str, parameters)
        self.assertTrue(val_res["success"], f"Mutated expression was invalid: {mutated_str}")

if __name__ == "__main__":
    unittest.main()
