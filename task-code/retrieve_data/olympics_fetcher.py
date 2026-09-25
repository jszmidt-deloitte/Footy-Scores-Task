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


def generate(output_dir: Path) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    session = requests.Session()
    seeds = unique_football_seeds(parse_schedule(retrieve_start_list(session)))
    event_units, games, phases, results, failed = retrieve_details(session, seeds)

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


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    args = parser.parse_args()
    result = generate(args.output_dir)
    print(f"Generated {result['diagnostics']['totalMatches']} football match endpoints in {args.output_dir}")
    if result["diagnostics"]["failedEndpoints"]:
        print(f"Warning: {len(result['diagnostics']['failedEndpoints'])} secondary endpoints failed")


if __name__ == "__main__":
    main()
