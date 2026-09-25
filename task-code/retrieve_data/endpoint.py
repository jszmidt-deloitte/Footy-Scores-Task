from typing import Any

def to_endpoint(seed: dict[str, Any], detail: dict[str, Any], round_name: str) -> dict[str, Any]:
    def lineup(team_code: str, team_name: str) -> dict[str, Any]:
        source = next((item for item in detail["lineups"] if item["teamCode"] == team_code), None)
        if not source:
            return {"team": team_name or "Unknown", "formation": "Unknown", "coach": "Unknown", "startingXI": [], "bench": []}

        players = sorted(source["players"], key=lambda item: item["sortOrder"])
        mapped = [{"name": item["name"], "number": item["number"], "position": item["position"]} for item in players]
        return {
            "team": source["team"] or team_name or "Unknown",
            "formation": source["formation"] or "Unknown",
            "coach": source["coach"] or "Unknown",
            "startingXI": [player for player, item in zip(mapped, players) if item["starter"]],
            "bench": [player for player, item in zip(mapped, players) if not item["starter"]],
        }

    scorers = []
    for scorer in detail["scorers"]:
        team = (
            seed["home"] if scorer["teamCode"] == seed["homeCode"]
            else seed["away"] if scorer["teamCode"] == seed["awayCode"]
            else "Unknown"
        )
        mapped = {
            "team": team or "Unknown",
            "player": scorer["player"] or "Unknown",
            "minute": scorer["minute"],
            "type": scorer["type"] or "open_play",
        }
        if scorer.get("assist"):
            mapped["assist"] = scorer["assist"]
        scorers.append(mapped)

    return {
        "competition": {
            "name": "Olympic Football Tournament",
            "season": "2024",
            "round": round_name or "Unknown",
        },
        "venue": {"name": seed["venue"] or "Unknown", "city": seed["city"] or "Unknown"},
        "kickoff": seed["kickoff"],
        "status": detail["status"] or seed["status"],
        "teams": {"home": seed["home"] or "Unknown", "away": seed["away"] or "Unknown"},
        "score": {
            "home": detail["homeScore"],
            "away": detail["awayScore"],
            "halfTime": {"home": detail["homeHalf"], "away": detail["awayHalf"]},
        },
        "scorers": scorers,
        "lineups": {
            "home": lineup(seed["homeCode"], seed["home"]),
            "away": lineup(seed["awayCode"], seed["away"]),
        },
    }
