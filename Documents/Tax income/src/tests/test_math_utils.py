"""Tests for math utilities"""
import unittest
from src.utils.math_utils import round_currency, calculate_percentage

class TestMathUtils(unittest.TestCase):
    def test_round_currency(self):
        self.assertEqual(round_currency(10.555), 10.56)

    def test_calculate_percentage(self):
        self.assertEqual(calculate_percentage(1000, 0.05), 50.0)
