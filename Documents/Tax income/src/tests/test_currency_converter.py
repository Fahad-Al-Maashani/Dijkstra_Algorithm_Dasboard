import unittest
from src.utils.currency_converter import CurrencyConverter

class TestCurrencyConverter(unittest.TestCase):
    def test_convert_to_omr(self):
        result = CurrencyConverter.convert_to_omr(100, 'USD')
        self.assertGreater(result, 0)

