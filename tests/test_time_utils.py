import unittest
from datetime import datetime

from backend.utils.time import utc_now_iso_z, parse_api_datetime


class TimeUtilsTests(unittest.TestCase):
    def test_utc_now_iso_z_has_timezone(self):
        value = utc_now_iso_z()
        self.assertTrue(value.endswith('Z'))
        parsed = parse_api_datetime(value)
        self.assertIsNotNone(parsed.tzinfo)

    def test_parse_naive_datetime_as_utc_for_legacy_data(self):
        parsed = parse_api_datetime('2026-05-03T01:58:03')
        self.assertEqual(parsed.utcoffset().total_seconds(), 0)
        self.assertEqual(parsed.hour, 1)


if __name__ == '__main__':
    unittest.main()
