"""
Unit tests for TaxCalculator
"""

import unittest
from src.models.tax_calculator import TaxCalculator


class TestTaxCalculator(unittest.TestCase):
    """Test cases for TaxCalculator class"""

    def setUp(self):
        """Set up test fixtures"""
        self.calculator = TaxCalculator()

    def test_initial_state(self):
        """Test calculator initial state"""
        self.assertEqual(self.calculator.annual_income, 0.0)
        self.assertEqual(self.calculator.calculate_tax_owed(), 0.0)

    def test_income_below_threshold(self):
        """Test income below tax threshold"""
        self.calculator.set_annual_income(30000)
        self.assertEqual(self.calculator.calculate_tax_owed(), 0.0)

    def test_income_at_threshold(self):
        """Test income exactly at tax threshold"""
        self.calculator.set_annual_income(42000)
        self.assertEqual(self.calculator.calculate_tax_owed(), 0.0)

    def test_income_above_threshold(self):
        """Test income above tax threshold"""
        self.calculator.set_annual_income(50000)
        expected_tax = (50000 - 42000) * 0.05
        self.assertEqual(self.calculator.calculate_tax_owed(), expected_tax)

    def test_deductions_reduce_taxable_income(self):
        """Test that deductions reduce taxable income"""
        self.calculator.set_annual_income(50000)
        self.calculator.set_deduction('education', 3000)

        taxable_income = self.calculator.calculate_taxable_income()
        self.assertEqual(taxable_income, 47000)

    def test_multiple_deductions(self):
        """Test multiple deduction categories"""
        self.calculator.set_annual_income(60000)
        self.calculator.set_deduction('education', 2000)
        self.calculator.set_deduction('medical', 1500)
        self.calculator.set_deduction('zakat', 1000)
        self.calculator.set_deduction('housing', 2500)

        total_deductions = self.calculator.calculate_total_deductions()
        self.assertEqual(total_deductions, 7000)

    def test_negative_values_handled(self):
        """Test that negative values are handled correctly"""
        self.calculator.set_annual_income(-1000)
        self.assertEqual(self.calculator.annual_income, 0.0)

        self.calculator.set_deduction('education', -500)
        self.assertEqual(self.calculator.deductions['education'], 0.0)


if __name__ == '__main__':
    unittest.main()