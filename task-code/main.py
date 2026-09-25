"""Fetch Olympic data, generate JSON, and start the match REST API."""

import argparse
import json
from pathlib import Path
from typing import Any

import uvicorn

from api.app import create_app
from retrieve_data.olympics_fetcher import generate


def load_generated_matches(output_dir: Path) -> list[dict[str, Any]]:
    generation_file = output_dir / "generation.json"
    if not generation_file.is_file():
        raise FileNotFoundError(
            f"Generated data was not found at {generation_file}. "
            "Run without --server-only first."
        )

    payload = json.loads(generation_file.read_text(encoding="utf-8"))
    records = payload.get("matches")
    if not isinstance(records, list):
        raise ValueError(f"Invalid generated data in {generation_file}: 'matches' must be a list")

    return [
        {
            "matchId": item["matchCode"],
            "endpoint": item["endpoint"],
        }
        for item in records
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument(
        "--server-only",
        action="store_true",
        help="Start the API from existing output/generation.json without fetching data",
    )
    args = parser.parse_args()

    if args.server_only:
        matches = load_generated_matches(args.output_dir)
        startup_message = f"Loaded {len(matches)} matches from {args.output_dir}"
    else:
        result = generate(args.output_dir)
        matches = [
            {
                "matchId": item["matchCode"],
                "endpoint": item["endpoint"],
            }
            for item in result["matches"]
        ]
        startup_message = f"Generated {len(matches)} matches"

    for match in matches:
        print(f"http://{args.host}:{args.port}/matches/{match['matchId']}")
    app = create_app(matches)
    print(f"{startup_message}. API listening on http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="critical")


if __name__ == "__main__":
    main()
