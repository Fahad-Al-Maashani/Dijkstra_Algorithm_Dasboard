import unittest
from src.utils.config import AppConfig

class TestAppConfig(unittest.TestCase):
    def test_default_config(self):
        config = AppConfig()
        self.assertIsNotNone(config.get('app.name'))
