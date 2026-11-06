"""Check the installed solar policy without a live controller."""

import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location(
    "tb40_solar",
    Path(__file__).resolve().parents[1] / "custom_components/novastar_tb40/solar.py",
)
solar = importlib.util.module_from_spec(spec)
spec.loader.exec_module(solar)


class TestSolar(unittest.TestCase):
    def test_startup_at_day_night_and_midpoint(self):
        for elevation, expected in [(10, 100), (-10, 8), (1, 54)]:
            with self.subTest(elevation=elevation):
                self.assertEqual(solar.solar_target(elevation), expected)

    def test_gradual_dimming(self):
        self.assertEqual(solar.solar_step(1, 100), 98.5)
        self.assertEqual(solar.solar_step(-4, 17), 16.6)
        self.assertEqual(solar.solar_step(-4, 9), 8.6)

    def test_small_change_and_lower_manual_target_are_preserved(self):
        self.assertIsNone(solar.solar_step(-4, 8.2))
        self.assertIsNone(solar.solar_step(-4, 7))
        self.assertIsNone(solar.solar_step(10, 8))

    def test_startup_retry_times(self):
        self.assertEqual(solar.RETRY_TIMES, (5, 10, 20, 30))
