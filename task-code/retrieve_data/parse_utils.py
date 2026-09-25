import re
from typing import Any


def as_record(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def as_array(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def as_string(value: Any, fallback: str = "") -> str:
    return value if isinstance(value, str) else fallback


def as_number(value: Any, fallback: int = 0) -> int:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return int(value)
    if isinstance(value, str):
        match = re.match(r"^-?\d+", value.strip())
        if match:
            return int(match.group())
    return fallback


def normalize_status(status: str) -> str:
    return {
        "FINISHED": "FT",
        "OFFICIAL": "FT",
        "SCHEDULED": "NS",
        "HALF_TIME": "HT",
    }.get(status.upper(), status or "NS")


def venue_city(description: str) -> str:
    parts = [part.strip() for part in description.split(",") if part.strip()]
    return parts[-1] if len(parts) >= 2 else "Unknown"

