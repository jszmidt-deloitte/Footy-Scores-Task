import unittest

from retrieve_data.schedule import parse_schedule, unique_football_seeds


MATCH_ID = "FBLMTEAM11------------GPA-000100--"


class ScheduleTests(unittest.TestCase):
    def test_parse_schedule_orders_teams_and_extracts_metadata(self):
        payload = {
            "schedules": [{
                "code": MATCH_ID,
                "startDate": "2024-07-24T15:00:00Z",
                "status": {"code": "FINISHED"},
                "venue": {"description": "Stadium"},
                "location": {"description": "Stadium, Paris"},
                "start": [
                    {"startOrder": "2", "teamCode": "USA", "participant": {"name": "USA"}},
                    {"startOrder": "1", "teamCode": "FRA", "participant": {"name": "France"}},
                ],
            }],
        }
        seed = parse_schedule(payload)[0]
        self.assertEqual(seed["home"], "France")
        self.assertEqual(seed["away"], "USA")
        self.assertEqual(seed["status"], "FT")
        self.assertEqual(seed["city"], "Paris")

    def test_unique_football_seeds_filters_and_deduplicates(self):
        football = {"matchCode": MATCH_ID, "eventCode": MATCH_ID[:22]}
        non_football = {"matchCode": "SWM123", "eventCode": "SWM123"}
        self.assertEqual(unique_football_seeds([football, football, non_football]), [football])
