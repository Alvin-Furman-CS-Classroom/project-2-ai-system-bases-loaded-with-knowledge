"""
Unit tests for src/module3/csp_solver.py (Person A generic CSP engine).
"""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from module3.csp_solver import solve_max_csp


class TestToyCSPFeasibility(unittest.TestCase):
    def test_two_variables_two_values(self):
        variables = ["X", "Y"]
        domains = {"X": ["a", "b"], "Y": ["a", "b"]}
        result = solve_max_csp(variables, domains, lambda v, val: 1.0, all_different=True)
        self.assertIsNotNone(result)
        self.assertEqual(set(result.keys()), {"X", "Y"})
        self.assertNotEqual(result["X"], result["Y"])

    def test_chain_domains(self):
        variables = ["A", "B", "C"]
        domains = {"A": [1, 2], "B": [2, 3], "C": [3, 4]}

        def contrib(v, val):
            return float(val)

        result = solve_max_csp(variables, domains, contrib, all_different=True)
        self.assertIsNotNone(result)
        self.assertEqual(len(set(result.values())), 3)


class TestAllDifferent(unittest.TestCase):
    def test_enforces_unique_values(self):
        variables = ["p1", "p2", "p3"]
        domains = {
            "p1": ["Alice", "Bob", "Carol"],
            "p2": ["Alice", "Bob", "Carol"],
            "p3": ["Alice", "Bob", "Carol"],
        }
        result = solve_max_csp(
            variables,
            domains,
            lambda v, p: 1.0,
            all_different=True,
        )
        self.assertIsNotNone(result)
        self.assertEqual(len(result), 3)
        self.assertEqual(len(set(result.values())), 3)

    def test_impossible_three_players_one_value(self):
        variables = ["a", "b", "c"]
        domains = {"a": [1], "b": [1], "c": [1]}
        result = solve_max_csp(variables, domains, lambda v, x: 1.0, all_different=True)
        self.assertIsNone(result)


class TestOptimization(unittest.TestCase):
    def test_picks_higher_sum(self):
        variables = ["X", "Y"]
        domains = {"X": ["p1", "p2"], "Y": ["p1", "p2"]}

        def contrib(v, val):
            if (v, val) == ("X", "p2"):
                return 10.0
            if (v, val) == ("X", "p1"):
                return 1.0
            if (v, val) == ("Y", "p1"):
                return 10.0
            if (v, val) == ("Y", "p2"):
                return 1.0
            return 0.0

        result = solve_max_csp(variables, domains, contrib, all_different=True)
        self.assertIsNotNone(result)
        total = sum(contrib(v, result[v]) for v in variables)
        self.assertEqual(total, 20.0)
        self.assertEqual(result["X"], "p2")
        self.assertEqual(result["Y"], "p1")

    def test_branch_bound_matches_exhaustive(self):
        variables = ["A", "B", "C"]
        domains = {
            "A": ["x", "p1", "p2"],
            "B": ["x", "p1", "p3"],
            "C": ["x", "p2", "p3"],
        }

        def contrib(v, val):
            if val in ("p1", "p2", "p3"):
                return 5.0
            return 1.0

        with_bb = solve_max_csp(
            variables, domains, contrib, all_different=True, use_branch_bound=True
        )
        without_bb = solve_max_csp(
            variables, domains, contrib, all_different=True, use_branch_bound=False
        )
        self.assertIsNotNone(with_bb)
        self.assertIsNotNone(without_bb)
        s_bb = sum(contrib(v, with_bb[v]) for v in variables)
        s_no = sum(contrib(v, without_bb[v]) for v in variables)
        self.assertEqual(s_bb, s_no)
        self.assertEqual(s_bb, 15.0)


class TestUnsatisfiable(unittest.TestCase):
    def test_two_vars_one_value_all_different(self):
        result = solve_max_csp(
            ["a", "b"], {"a": [1], "b": [1]}, lambda v, x: 1.0, all_different=True
        )
        self.assertIsNone(result)

    def test_locked_conflicts(self):
        result = solve_max_csp(
            ["X", "Y"],
            {"X": ["a"], "Y": ["a"]},
            lambda v, x: 1.0,
            all_different=True,
            locked={"X": "a"},
        )
        self.assertIsNone(result)


class TestLocked(unittest.TestCase):
    def test_lock_forces_value(self):
        variables = ["A", "B", "C"]
        domains = {"A": [1, 2, 3], "B": [1, 2, 3], "C": [1, 2, 3]}
        result = solve_max_csp(
            variables,
            domains,
            lambda v, x: float(x),
            all_different=True,
            locked={"B": 2},
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["B"], 2)
        self.assertEqual(len(set(result.values())), 3)


class TestPartialConstraint(unittest.TestCase):
    def test_rejects_both_twos(self):
        variables = ["X", "Y"]
        domains = {"X": [1, 2], "Y": [1, 2]}

        def contrib(v, val):
            return float(val)

        def no_both_twos(assign):
            if assign.get("X") == 2 and assign.get("Y") == 2:
                return False
            return True

        result = solve_max_csp(
            variables,
            domains,
            contrib,
            all_different=False,
            partial_constraint=no_both_twos,
        )
        self.assertIsNotNone(result)
        self.assertFalse(result.get("X") == 2 and result.get("Y") == 2)


class TestAPI(unittest.TestCase):
    def test_duplicate_variables_raises(self):
        with self.assertRaises(ValueError):
            solve_max_csp(["X", "X"], {"X": [1]}, lambda v, x: 1.0)

    def test_missing_domain_raises(self):
        with self.assertRaises(KeyError):
            solve_max_csp(["X", "Y"], {"X": [1]}, lambda v, x: 1.0)

    def test_all_different_false_allows_duplicate_value(self):
        result = solve_max_csp(
            ["A", "B"], {"A": [1], "B": [1]}, lambda v, x: 1.0, all_different=False
        )
        self.assertIsNotNone(result)
        self.assertEqual(result["A"], 1)
        self.assertEqual(result["B"], 1)


if __name__ == "__main__":
    unittest.main()
