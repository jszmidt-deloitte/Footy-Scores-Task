from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

import requests

from .constants import (
    DATA_URL,
    EVENT_GAMES_TEMPLATE,
    EVENT_UNITS_FILE,
    HEADERS,
    LABELS_URL,
    PHASES_TEMPLATE,
    RESULT_TEMPLATE,
    START_LIST_FILE,
)


def fetch_json(session: requests.Session, url: str) -> Any:
    response = session.get(url, headers=HEADERS, timeout=30)
    response.raise_for_status()
    return response.json()


def data_url(filename: str) -> str:
    return f"{DATA_URL}/{filename}"


def retrieve_start_list(session: requests.Session) -> Any:
    return fetch_json(session, data_url(START_LIST_FILE))


def retrieve_details(
    session: requests.Session,
    seeds: list[dict[str, Any]],
) -> tuple[Any, list[Any], list[Any], dict[str, Any], list[str]]:
    failed: list[str] = []
    try:
        event_units = fetch_json(session, data_url(EVENT_UNITS_FILE))
    except requests.RequestException as error:
        event_units = {}
        failed.append(f"{EVENT_UNITS_FILE}: {error}")

    try:
        fetch_json(session, LABELS_URL)
    except requests.RequestException as error:
        failed.append(f"labels.json: {error}")

    event_codes = sorted({seed["eventCode"] for seed in seeds})
    requests_to_make = [
        (EVENT_GAMES_TEMPLATE.format(event_code=code), "games", code)
        for code in event_codes
    ]
    requests_to_make += [
        (PHASES_TEMPLATE.format(event_code=code), "phases", code)
        for code in event_codes
    ]
    requests_to_make += [
        (RESULT_TEMPLATE.format(match_code=seed["matchCode"]), "result", seed["matchCode"])
        for seed in seeds
    ]

    games: list[Any] = []
    phases: list[Any] = []
    results: dict[str, Any] = {}
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {
            executor.submit(fetch_json, session, data_url(filename)): (filename, kind, key)
            for filename, kind, key in requests_to_make
        }
        for future in as_completed(futures):
            filename, kind, key = futures[future]
            try:
                payload = future.result()
            except requests.RequestException as error:
                failed.append(f"{filename}: {error}")
                continue
            if kind == "games":
                games.append(payload)
            elif kind == "phases":
                phases.append(payload)
            else:
                results[key] = payload
    return event_units, games, phases, results, failed
