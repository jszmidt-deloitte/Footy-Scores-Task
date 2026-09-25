import re
from typing import Any

from .constants import KNOWN_POSITIONS
from .parse_utils import as_array, as_number, as_record, as_string, normalize_status


def find_entry(entries: list[Any], code: str) -> str:
    for entry in entries:
        item = as_record(entry)
        if as_string(item.get("eue_code")) == code:
            return as_string(item.get("eue_value"))
    return ""


def extract_position(entries: list[Any]) -> str:
    positions = [
        as_string(as_record(entry).get("eue_value"))
        for entry in entries
        if as_string(as_record(entry).get("eue_code")) == "POSITION"
    ]
    return next((position for position in positions if position in KNOWN_POSITIONS), "Unknown")


def parse_lineup(item: Any) -> dict[str, Any]:
    record = as_record(item)
    players = []
    for entry in as_array(record.get("teamAthletes")):
        athlete_entry = as_record(entry)
        entries = as_array(athlete_entry.get("eventUnitEntries"))
        players.append({
            "name": as_string(as_record(athlete_entry.get("athlete")).get("name"), "Unknown"),
            "number": as_number(athlete_entry.get("bib")),
            "position": extract_position(entries),
            "starter": find_entry(entries, "STARTER") == "Y",
            "sortOrder": as_number(athlete_entry.get("startSortOrder"), as_number(athlete_entry.get("order"), 999)),
        })

    coach = "Unknown"
    for entry in as_array(record.get("teamCoaches")):
        coach_entry = as_record(entry)
        if as_string(as_record(coach_entry.get("function")).get("functionCode")) == "COACH":
            coach = as_string(as_record(coach_entry.get("coach")).get("name"), "Unknown")
            break

    return {
        "teamCode": as_string(record.get("teamCode")),
        "team": as_string(as_record(record.get("participant")).get("name"), "Unknown"),
        "formation": find_entry(as_array(record.get("eventUnitEntries")), "FORMATION") or "Unknown",
        "coach": coach,
        "players": sorted(players, key=lambda player: player["sortOrder"]),
    }


def extract_minute(value: str) -> int:
    match = re.search(r"(\d+)'\+(\d+)", value.replace(" ", "")) or re.search(r"(\d+)'", value)
    return int(match.group(1)) + (int(match.group(2)) if match.lastindex == 2 else 0) if match else 0


def empty_detail() -> dict[str, Any]:
    return {
        "status": "NS",
        "homeScore": 0,
        "awayScore": 0,
        "homeHalf": 0,
        "awayHalf": 0,
        "scorers": [],
        "lineups": [],
    }


def parse_detail(payload: Any) -> dict[str, Any]:
    results = as_record(as_record(payload).get("results"))
    if not results:
        return empty_detail()

    periods = [as_record(period) for period in as_array(results.get("periods"))]
    total = next((period for period in periods if as_string(period.get("p_code")) == "TOT"), {})
    first_half = next((period for period in periods if as_string(period.get("p_code")) == "H1"), {})
    score = lambda period, side: as_number(as_record(period.get(side)).get("score"))
    items = as_array(results.get("items"))
    lineups = [parse_lineup(item) for item in items if as_record(item).get("teamAthletes") is not None]
    names = {
        as_string(as_record(athlete).get("participantCode")):
        as_string(as_record(as_record(athlete).get("athlete")).get("name"), "Unknown")
        for item in items
        for athlete in as_array(as_record(item).get("teamAthletes"))
    }

    scorers = []
    for period in as_array(results.get("playByPlay")):
        for action in as_array(as_record(period).get("actions")):
            action_item = as_record(action)
            if as_string(action_item.get("pbpa_Result")) != "GOAL":
                continue
            team = next((as_record(value) for value in as_array(action_item.get("competitors")) if isinstance(value, dict)), {})
            athletes = [as_record(value) for value in as_array(team.get("athletes"))]
            scorer = next((value for value in athletes if as_string(value.get("pbpat_role")) == "SCR"), {})
            assist = next((value for value in athletes if as_string(value.get("pbpat_role")) == "ASSIST"), {})
            action_name = as_string(action_item.get("pbpa_Action")).upper()
            comment = as_string(action_item.get("pbpa_Comment")).upper()
            goal_type = "penalty" if "PEN" in action_name else "header" if "HEAD" in action_name or "HEADER" in comment else "open_play"
            scorer_record = {
                "teamCode": as_string(team.get("pbpc_code")),
                "player": names.get(as_string(scorer.get("pbpat_code")), "Unknown"),
                "minute": extract_minute(as_string(action_item.get("pbpa_When"))),
                "type": goal_type,
            }
            if assist_name := names.get(as_string(assist.get("pbpat_code"))):
                scorer_record["assist"] = assist_name
            scorers.append(scorer_record)

    unique_scorers = {(item["teamCode"], item["player"], item["minute"]): item for item in scorers}
    extended_status = next(
        (as_string(as_record(value).get("ei_value"))
         for value in as_array(results.get("extendedInfos"))
         if as_string(as_record(value).get("ei_code")) == "PERIOD"),
        "",
    )
    return {
        "status": normalize_status(extended_status or as_string(as_record(results.get("status")).get("code"))),
        "homeScore": score(total, "home"),
        "awayScore": score(total, "away"),
        "homeHalf": score(first_half, "home"),
        "awayHalf": score(first_half, "away"),
        "scorers": sorted(unique_scorers.values(), key=lambda item: item["minute"]),
        "lineups": lineups,
    }
