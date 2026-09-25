import unittest

from retrieve_data.endpoint import to_endpoint


class EndpointTests(unittest.TestCase):
    def test_endpoint_contains_expected_match_shape(self):
        seed = {
            "home": "France",
            "away": "USA",
            "homeCode": "FRA",
            "awayCode": "USA",
            "kickoff": "2024-07-24T15:00:00Z",
            "status": "FT",
            "venue": "Stadium",
            "city": "Paris",
        }
        detail = {
            "status": "FT",
            "homeScore": 2,
            "awayScore": 1,
            "homeHalf": 1,
            "awayHalf": 0,
            "scorers": [],
            "lineups": [],
        }
        endpoint = to_endpoint(seed, detail, "Group A")
        self.assertEqual(endpoint["teams"], {"home": "France", "away": "USA"})
        self.assertEqual(endpoint["competition"]["round"], "Group A")
        self.assertEqual(endpoint["score"]["halfTime"]["home"], 1)
