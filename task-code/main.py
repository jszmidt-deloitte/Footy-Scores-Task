"""Fetch Olympic data, generate JSON, and start the match REST API."""

import argparse
from pathlib import Path

import uvicorn

from api.app import create_app
from retrieve_data.olympics_fetcher import generate


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("output"))
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    result = generate(args.output_dir)
    matches = []
    for item in result["matches"]:
        print(f"http://{args.host}:{args.port}/matches/{item['matchCode']}")
        matches.append(
            {
                "matchId": item["matchCode"],
                "endpoint": item["endpoint"],
            }
        )
    app = create_app(matches)
    print(f"Generated {len(matches)} matches. API listening on http://{args.host}:{args.port}")
    uvicorn.run(app, host=args.host, port=args.port, log_level="critical")


if __name__ == "__main__":
    main()
