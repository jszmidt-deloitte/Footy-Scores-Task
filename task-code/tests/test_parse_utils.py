import unittest

from retrieve_data.parse_utils import (
    as_array,
    as_number,
    as_record,
    as_string,
    normalize_status,
    venue_city,
)


class ParseUtilsTests(unittest.TestCase):
    def test_safe_conversions_use_fallbacks_for_wrong_types(self):
        self.assertEqual(as_record("not a record"), {})
        self.assertEqual(as_array("not an array"), [])
        self.assertEqual(as_string(12, "Unknown"), "Unknown")
        self.assertEqual(as_number("45' +2"), 45)
        self.assertEqual(as_number(True, 7), 7)

    def test_status_and_city_normalization(self):
        self.assertEqual(normalize_status("FINISHED"), "FT")
        self.assertEqual(normalize_status("scheduled"), "NS")
        self.assertEqual(normalize_status(""), "NS")
        self.assertEqual(venue_city("Parc des Princes, Paris"), "Paris")
        self.assertEqual(venue_city("Unknown"), "Unknown")
