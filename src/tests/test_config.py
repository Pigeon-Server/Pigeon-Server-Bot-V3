from unittest import TestCase

from src.base.config import ConfigSet


class TestConfig(TestCase):

    def test_load_config(self):
        config = ConfigSet()
        self.assertIsNotNone(config)
