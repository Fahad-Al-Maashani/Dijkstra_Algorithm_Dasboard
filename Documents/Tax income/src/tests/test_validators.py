"""
Unit tests for input validators
"""

import unittest
from src.utils.validators import InputValidator


class TestInputValidator(unittest.TestCase):
    """Test cases for InputValidator class"""

    def test_validate_currency_valid_input(self):
        """Test valid currency input"""
        is_valid, value = InputValidator.validate_currency("1000.50")
        self.assertTrue(is_valid)
        self.assertEqual(value, 1000.50)

    def test_validate_currency_with_omr_symbol(self):
        """Test currency input with OMR symbol"""
        is_valid, value = InputValidator.validate_currency("OMR 2500.75")
        self.assertTrue(is_valid)
        self.assertEqual(value, 2500.75)

    def test_validate_currency_with_commas(self):
        """Test currency input with commas"""
        is_valid, value = InputValidator.validate_currency("50,000.00")
        self.assertTrue(is_valid)
        self.assertEqual(value, 50000.00)

    def test_validate_currency_empty_input(self):
        """Test empty currency input"""
        is_valid, value = InputValidator.validate_currency("")
        self.assertTrue(is_valid)
        self.assertEqual(value, 0.0)

    def test_validate_currency_invalid_input(self):
        """Test invalid currency input"""
        is_valid, value = InputValidator.validate_currency("abc")
        self.assertFalse(is_valid)
        self.assertEqual(value, 0.0)

    def test_validate_currency_negative_input(self):
        """Test negative currency input"""
        is_valid, value = InputValidator.validate_currency("-500")
        self.assertFalse(is_valid)
        self.assertEqual(value, 0.0)

    def test_validate_positive_number_valid(self):
        """Test valid positive number"""
        is_valid, value = InputValidator.validate_positive_number("123.45")
        self.assertTrue(is_valid)
        self.assertEqual(value, 123.45)

    def test_validate_positive_number_zero(self):
        """Test zero as positive number"""
        is_valid, value = InputValidator.validate_positive_number("0")
        self.assertTrue(is_valid)
        self.assertEqual(value, 0.0)

    def test_validate_positive_number_negative(self):
        """Test negative number"""
        is_valid, value = InputValidator.validate_positive_number("-10")
        self.assertFalse(is_valid)
        self.assertEqual(value, 0.0)

    def test_format_currency(self):
        """Test currency formatting"""
        formatted = InputValidator.format_currency(12345.67)
        self.assertEqual(formatted, "OMR 12,345.67")

    def test_format_percentage(self):
        """Test percentage formatting"""
        formatted = InputValidator.format_percentage(0.05)
        self.assertEqual(formatted, "5.0%")


if __name__ == '__main__':
    unittest.main()