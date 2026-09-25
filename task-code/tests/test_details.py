import unittest

from retrieve_data.details import extract_minute, extract_position, parse_detail


class DetailsTests(unittest.TestCase):
    def test_invalid_positions_are_unknown(self):
        self.assertEqual(extract_position([{"eue_code": "POSITION", "eue_value": "M23"}]), "Unknown")
        self.assertEqual(extract_position([{"eue_code": "POSITION", "eue_value": "FW"}]), "FW")

    def test_extract_minute_handles_stoppage_time(self):
        self.assertEqual(extract_minute("45' + 2"), 47)
        self.assertEqual(extract_minute("12'"), 12)
        self.assertEqual(extract_minute("unknown"), 0)

    def test_parse_detail_reads_scores_and_goal_information(self):
        payload = {
            "results": {
                "periods": [
                    {"p_code": "TOT", "home": {"score": "2"}, "away": {"score": 1}},
                    {"p_code": "H1", "home": {"score": 1}, "away": {"score": 0}},
                ],
                "status": {"code": "FINISHED"},
                "items": [{
                    "teamCode": "FRA",
                    "participant": {"name": "France"},
                    "teamAthletes": [{
                        "participantCode": "P1",
                        "athlete": {"name": "Player One"},
                    }],
                }],
                "playByPlay": [{
                    "actions": [{
                        "pbpa_Result": "GOAL",
                        "pbpa_When": "45' + 2",
                        "pbpa_Action": "HEADER",
                        "competitors": [{
                            "pbpc_code": "FRA",
                            "athletes": [{"pbpat_code": "P1", "pbpat_role": "SCR"}],
                        }],
                    }],
                }],
            },
        }
        detail = parse_detail(payload)
        self.assertEqual(detail["homeScore"], 2)
        self.assertEqual(detail["awayHalf"], 0)
        self.assertEqual(detail["scorers"][0]["minute"], 47)
        self.assertEqual(detail["scorers"][0]["type"], "header")
