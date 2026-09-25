from typing import Any

from .constants import EVENT_CODE_LENGTH
from .parse_utils import as_array, as_number, as_record, as_string, normalize_status, venue_city


def parse_schedule(payload: Any) -> list[dict[str, Any]]:
    schedules = as_record(payload).get("schedules")
    if not isinstance(schedules, list) or not schedules:
        raise ValueError("Official start-list payload has no schedules")

    seeds = []
    for schedule in schedules:
        item = as_record(schedule)
        match_code = as_string(item.get("code"))
        starts = sorted(
            as_array(item.get("start")),
            key=lambda value: as_number(as_record(value).get("startOrder"), 999),
        )
        if not match_code or len(starts) < 2:
            continue

        home = as_record(starts[0])
        away = as_record(starts[1])
        home_participant = as_record(home.get("participant"))
        away_participant = as_record(away.get("participant"))
        home_code = as_string(home.get("teamCode"), as_string(home_participant.get("code")))
        away_code = as_string(away.get("teamCode"), as_string(away_participant.get("code")))
        if not home_code or not away_code:
            continue

        seeds.append({
            "matchCode": match_code,
            "eventCode": match_code[:EVENT_CODE_LENGTH],
            "kickoff": as_string(item.get("startDate")),
            "status": normalize_status(as_string(as_record(item.get("status")).get("code"))),
            "homeCode": home_code,
            "home": as_string(home_participant.get("name"), "Unknown"),
            "awayCode": away_code,
            "away": as_string(away_participant.get("name"), "Unknown"),
            "venue": as_string(as_record(item.get("venue")).get("description"), "Unknown"),
            "city": venue_city(as_string(as_record(item.get("location")).get("description"))),
        })
    return seeds


def unique_football_seeds(seeds: list[dict[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result = []
    for seed in seeds:
        if seed["matchCode"].startswith("FBL") and seed["eventCode"].startswith("FBL"):
            if seed["matchCode"] not in seen:
                seen.add(seed["matchCode"])
                result.append(seed)
    return result
