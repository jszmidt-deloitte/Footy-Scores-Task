from typing import Any

from fastapi import FastAPI, HTTPException


def create_app(matches: list[dict[str, Any]]) -> FastAPI:
    app = FastAPI(title="Olympic Football Matches", version="1.0.0")
    matches_by_id = {
        match_id: match
        for match in matches
        if (match_id := match.get("matchId"))
    }

    @app.get("/matches")
    def get_matches() -> list[dict[str, Any]]:
        return [match["endpoint"] for match in matches]

    @app.get("/matches/{match_id}")
    def get_match(match_id: str) -> dict[str, Any]:
        normalized_id = match_id.removesuffix(".json")
        match = matches_by_id.get(normalized_id)
        if match is None:
            raise HTTPException(status_code=404, detail=f"Match '{match_id}' was not found")
        return match["endpoint"]

    return app
