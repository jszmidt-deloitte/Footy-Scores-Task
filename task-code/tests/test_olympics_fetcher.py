import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from retrieve_data.olympics_fetcher import generate_single, list_matches


MATCH_ID = "FBLMTEAM11------------GPA-000100--"


class FetcherModeTests(unittest.TestCase):
    def test_list_matches_only_fetches_schedule(self):
        seeds = [{"matchCode": MATCH_ID, "home": "France", "away": "USA", "eventCode": MATCH_ID[:22]}]
        with patch("retrieve_data.olympics_fetcher.retrieve_start_list", return_value={}), \
             patch("retrieve_data.olympics_fetcher.parse_schedule", return_value=seeds), \
             patch("retrieve_data.olympics_fetcher.retrieve_details") as retrieve_details:
            self.assertEqual(list_matches(), seeds)
            retrieve_details.assert_not_called()

    def test_generate_single_writes_only_selected_match(self):
        seed = {
            "matchCode": MATCH_ID,
            "eventCode": MATCH_ID[:22],
            "home": "France",
            "away": "USA",
        }
        endpoint = {"teams": {"home": "France", "away": "USA"}}
        with tempfile.TemporaryDirectory() as directory, \
             patch("retrieve_data.olympics_fetcher.retrieve_start_list", return_value={}), \
             patch("retrieve_data.olympics_fetcher.parse_schedule", return_value=[seed]), \
             patch("retrieve_data.olympics_fetcher.retrieve_records", return_value=([(seed, endpoint)], [])):
            result = generate_single(Path(directory), MATCH_ID)
            output = Path(directory) / f"{MATCH_ID}.json"
            self.assertTrue(output.exists())
            self.assertEqual(json.loads(output.read_text()), endpoint)
            self.assertEqual(result["match"], endpoint)

    def test_generate_single_rejects_unknown_match(self):
        with patch("retrieve_data.olympics_fetcher.retrieve_start_list", return_value={}), \
             patch("retrieve_data.olympics_fetcher.parse_schedule", return_value=[]):
            with self.assertRaisesRegex(ValueError, "Match identifier not found"):
                generate_single(Path(tempfile.gettempdir()), MATCH_ID)
