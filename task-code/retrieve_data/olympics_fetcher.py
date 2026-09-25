import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import requests

from .details import parse_detail
from .endpoint import to_endpoint
from .rounds import build_rounds, build_summaries, derive_round
from .schedule import parse_schedule, unique_football_seeds
from .source import retrieve_details, retrieve_start_list


def write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def retrieve_records(
    session: requests.Session,
    seeds: list[dict[str, Any]],
    timeout: float,
    max_workers: int,
) -> tuple[list[tuple[dict[str, Any], dict[str, Any]]], list[str]]:
    event_units, games, phases, results, failed = retrieve_details(
        session,
        seeds,
        timeout,
        max_workers,
    )

    rounds = build_rounds(phases, event_units)
    summaries = build_summaries(games)
    records = []
    for seed in seeds:
        detail = parse_detail(results.get(seed["matchCode"]))
        summary = summaries.get(seed["matchCode"])
        if detail["status"] == "NS" and summary:
            detail.update({
                "status": summary["status"],
                "homeScore": summary["homeScore"],
                "awayScore": summary["awayScore"],
            })
        round_name = rounds.get(seed["matchCode"]) or (summary or {}).get("round") or derive_round(seed["matchCode"])
        records.append((seed, to_endpoint(seed, detail, round_name)))

    records.sort(key=lambda record: (
        record[1]["kickoff"],
        record[1]["teams"]["home"],
        record[1]["teams"]["away"],
    ))
    return records, failed


def generate(output_dir: Path, timeout: float = 30.0, max_workers: int = 8) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    seeds = unique_football_seeds(parse_schedule(retrieve_start_list(session, timeout)))
    records, failed = retrieve_records(session, seeds, timeout, max_workers)
    endpoints = [endpoint for _, endpoint in records]
    for seed, endpoint in records:
        write_json(output_dir / f"{seed['matchCode']}.json", endpoint)
    write_json(output_dir / "matches.json", endpoints)

    result = {
        "diagnostics": {
            "sourceMode": "official",
            "generatedAt": datetime.now().astimezone().isoformat(),
            "totalMatches": len(endpoints),
            "failedEndpoints": sorted(failed),
        },
        "matches": [
            {"matchCode": seed["matchCode"], "endpoint": endpoint}
            for seed, endpoint in records
        ],
    }
    write_json(output_dir / "generation.json", result)
    return result


def list_matches(timeout: float = 30.0) -> list[dict[str, Any]]:
    with requests.Session() as session:
        return unique_football_seeds(parse_schedule(retrieve_start_list(session, timeout)))


def generate_single(
    output_dir: Path,
    match_id: str,
    timeout: float = 30.0,
    max_workers: int = 8,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    with requests.Session() as session:
        seeds = unique_football_seeds(parse_schedule(retrieve_start_list(session, timeout)))
        seed = next((item for item in seeds if item["matchCode"] == match_id), None)
        if seed is None:
            raise ValueError(f"Match identifier not found: {match_id}")
        records, failed = retrieve_records(session, [seed], timeout, max_workers)

    endpoint = records[0][1]
    write_json(output_dir / f"{match_id}.json", endpoint)
    return {"match": endpoint, "failedEndpoints": failed}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument(
        "--list-matches",
        action="store_true",
        help="List match identifiers and teams without saving files",
    )
    mode.add_argument(
        "--match-id",
        metavar="ID",
        help="Retrieve and save one match by its identifier",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("output"),
        help="Directory where generated JSON files are saved (default: output)",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        metavar="SECONDS",
        help="HTTP timeout for each request (default: 30)",
    )
    parser.add_argument(
        "--workers",
        type=int,
        default=8,
        metavar="COUNT",
        help="Maximum number of detail requests made concurrently (default: 8)",
    )
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be greater than 0")
    if args.workers <= 0:
        parser.error("--workers must be greater than 0")

    if args.list_matches:
        matches = list_matches(args.timeout)
        for match in matches:
            print(f"{match['matchCode']}: {match['home']} vs {match['away']}")
        print(f"Total matches: {len(matches)}")
        return

    if args.match_id:
        try:
            result = generate_single(args.output_dir, args.match_id, args.timeout, args.workers)
        except ValueError as error:
            parser.error(str(error))
        print(f"{args.match_id}.json")
        if result["failedEndpoints"]:
            print(f"Warning: {len(result['failedEndpoints'])} secondary endpoints failed")
        return

    result = generate(args.output_dir, args.timeout, args.workers)
    for match in result["matches"]:
        print(f"{match['matchCode']}.json")
    print(f"Total JSON match files: {result['diagnostics']['totalMatches']}")
    if result["diagnostics"]["failedEndpoints"]:
        print(f"Warning: {len(result['diagnostics']['failedEndpoints'])} secondary endpoints failed")


if __name__ == "__main__":
    main()
