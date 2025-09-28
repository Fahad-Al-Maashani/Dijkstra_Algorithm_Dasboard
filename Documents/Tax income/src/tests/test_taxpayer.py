import unittest
from src.models.taxpayer import Taxpayer

class TestTaxpayer(unittest.TestCase):
    def test_taxpayer_creation(self):
        taxpayer = Taxpayer()
        self.assertIsNotNone(taxpayer)

