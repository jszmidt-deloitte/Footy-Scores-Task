from typing import Any

from .constants import EVENT_CODE_LENGTH
from .parse_utils import as_array, as_number, as_record, as_string, normalize_status


def derive_round(match_code: str) -> str:
    token = match_code[EVENT_CODE_LENGTH : EVENT_CODE_LENGTH + 4]
    if token.startswith("GP"):
        return f"Group {token[2]}"
    if token == "QFNL":
        return "Quarter-finals"
    if token == "SFNL":
        return "Semi-finals"
    if token == "FNL-":
        return "Gold Medal Match" if "000100" in match_code else "Bronze Medal Match" if "000200" in match_code else "Finals"
    return "Unknown"


def build_rounds(phase_payloads: list[Any], event_units: Any) -> dict[str, str]:
    rounds: dict[str, str] = {}
    for payload in phase_payloads:
        event = as_record(as_record(payload).get("event"))
        for phase in as_array(event.get("phases")):
            phase_item = as_record(phase)
            phase_round = as_string(phase_item.get("shortDescription"), as_string(phase_item.get("description"), "Unknown"))
            for unit in as_array(phase_item.get("units")):
                unit_item = as_record(unit)
                if code := as_string(unit_item.get("code")):
                    rounds[code] = as_string(unit_item.get("shortDescription"), as_string(unit_item.get("description"), phase_round))
    for unit in as_array(as_record(event_units).get("eventUnits")):
        unit_item = as_record(unit)
        code = as_string(unit_item.get("code"))
        if as_string(unit_item.get("type")) == "HTEAM" and code not in rounds:
            rounds[code] = as_string(unit_item.get("shortDescription"), as_string(unit_item.get("description"), "Unknown"))
    return rounds


def build_summaries(payloads: list[Any]) -> dict[str, dict[str, Any]]:
    summaries: dict[str, dict[str, Any]] = {}
    for payload in payloads:
        event = as_record(as_record(payload).get("event"))
        for phase in as_array(event.get("phases")):
            phase_item = as_record(phase)
            phase_round = as_string(phase_item.get("shortDescription"), as_string(phase_item.get("description"), "Unknown"))
            for unit in as_array(phase_item.get("units")):
                unit_item = as_record(unit)
                code = as_string(unit_item.get("code"))
                result = as_record(as_record(as_record(unit_item.get("schedule")).get("result")))
                items = [as_record(item) for item in as_array(result.get("items"))]
                home = next((item for item in items if as_string(item.get("startOrder")) == "1"), {})
                away = next((item for item in items if as_string(item.get("startOrder")) == "2"), {})
                if code:
                    summaries[code] = {
                        "homeScore": as_number(home.get("resultData")),
                        "awayScore": as_number(away.get("resultData")),
                        "status": normalize_status(as_string(as_record(result.get("status")).get("code"))),
                        "round": as_string(unit_item.get("shortDescription"), as_string(unit_item.get("description"), phase_round)),
                    }
    return summaries
