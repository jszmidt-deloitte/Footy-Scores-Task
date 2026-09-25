import unittest

from retrieve_data.rounds import derive_round


class RoundTests(unittest.TestCase):
    def test_derive_round_from_match_identifier(self):
        self.assertEqual(derive_round("FBLMTEAM11------------GPA-000100--"), "Group A")
        self.assertEqual(derive_round("FBLMTEAM11------------QFNL000100--"), "Quarter-finals")
        self.assertEqual(derive_round("unknown"), "Unknown")
