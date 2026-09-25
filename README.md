# Footy Scores

> A small Python service that retrieves official Paris 2024 Olympic football
> data and exposes FootyScores-compatible match JSON through a REST API.

## What this project does

The application:

1. Fetches the official Olympic football schedule and match data.
2. Filters the schedule to football matches only.
3. Removes duplicate match identifiers.
4. Retrieves scores, half-time scores, scorers, lineups, formations, coaches,
   venues, and competition rounds.
5. Normalizes the data into the structure defined by [`example.json`](../example.json).
6. Writes deterministic JSON files to `output/`.
7. Starts a REST API for retrieving all matches or one match by identifier.

## Requirements

- Python 3.10 or newer
- Internet access to the official Olympics data endpoints

## Installation

Open PowerShell in this directory:

```powershell
cd "task-code"
```

Create a virtual environment if needed:

```powershell
py -m venv .venv
```

Activate it:

```powershell
.\.venv\Scripts\Activate.ps1
```

Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

## Run the data generator only

You can run only the data fetcher without starting
the web server using this command:

```powershell
python -m retrieve_data.olympics_fetcher --output-dir output
```

Expected output:

```text
Generated ... football match endpoints in output
```

## Run the hosted REST server

The recommended command is:

```powershell
python main.py --host 127.0.0.1 --port 8000
```

The startup sequence is:

```text
Fetch Olympic data
    ↓
Generate and save JSON files
    ↓
Create the FastAPI application
    ↓
Start the Uvicorn web server
```

By default, `main.py` always refreshes the Olympic data before starting the
server.

### Start the server from existing output

To start the API without making any Olympic requests, use:

```powershell
python main.py --server-only --output-dir output --host 127.0.0.1 --port 8000
```

This mode loads `output/generation.json` and serves the matches already
generated there. Run the normal command at least once first:

```powershell
python main.py
```

If the requested output directory does not contain `generation.json`, server
startup stops with an instruction to run the normal fetch-and-serve command.

Once started, the server is available at:

```text
http://127.0.0.1:8000
```

The exat endpoints are described in the section below

The server must remain running while you send requests. Stop it with
`Ctrl+C`.

### Host and port options

Use a different host or port when required:

```powershell
python main.py --host 0.0.0.0 --port 8080
```

`0.0.0.0` makes the server listen on all network interfaces. Use it only when
the service needs to be accessed from another machine or container.

## REST API

### Get all matches

```http
GET /matches
```

PowerShell example:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/matches
```

The response is a JSON array containing one FootyScores endpoint object per
football match.

### Get one match

```http
GET /matches/{match_id}
```

The identifier is the same value used in the generated filename.

Example:

```http
GET /matches/FBLMTEAM11------------GPA-000100--
```

The `.json` suffix is also accepted:

```http
GET /matches/FBLMTEAM11------------GPA-000100--.json
```

PowerShell example:

```powershell
Invoke-RestMethod `
  "http://127.0.0.1:8000/matches/FBLMTEAM11------------GPA-000100--"
```

If the identifier does not exist, the API returns:

```json
{
  "detail": "Match 'UNKNOWN' was not found"
}
```

with HTTP status `404`.

### Interactive API documentation

FastAPI automatically provides:

- Swagger UI: <http://127.0.0.1:8000/docs>
- ReDoc: <http://127.0.0.1:8000/redoc>

## Generated files

The generator creates the following files in `output/`:

| File | Description |
| --- | --- |
| `<match-code>.json` | One endpoint object for a single match |
| `matches.json` | All endpoint objects in deterministic order |
| `generation.json` | Diagnostics, failed secondary requests, and generated records |

Example match filename:

```text
FBLMTEAM11------------GPA-000100--.json
```

Generated matches are ordered by:

1. Kickoff timestamp
2. Home team name
3. Away team name

## Data source and fallback behavior

The source is the official Olympics `stacy.olympics.com` data service. The
retrieval layer uses:

- `SCH_StartList` for the schedule and teams
- `GLO_EventUnits` for competition-unit fallback data
- `GLO_EventGames` for summary scores and rounds
- `SEL_Phases` for tournament-round information
- `RES_ByRSC_H2H` for detailed match results
- `labels.json` for source availability validation

Browser-like request headers are included because the source may reject plain
HTTP clients with a `403` response.

If a secondary endpoint fails, generation continues. Failed requests are
listed in `generation.json`, and missing details use safe defaults such as
`Unknown`, `0`, `NS`, empty scorer lists, or empty lineups.

## Project structure

```text
task-code/
├── api/
│   └── app.py                 # FastAPI routes
├── retrieve_data/
│   ├── constants.py           # URLs, headers, and endpoint templates
│   ├── details.py             # Scores, scorers, lineups, and positions
│   ├── endpoint.py            # FootyScores endpoint transformation
│   ├── olympics_fetcher.py    # Data-generation orchestration and CLI
│   ├── parse_utils.py         # Safe JSON value conversion helpers
│   ├── rounds.py              # Round and summary parsing
│   ├── schedule.py            # Schedule parsing and football filtering
│   └── source.py              # HTTP retrieval and concurrent requests
├── main.py                    # Fetches data and starts the server
├── requirements.txt           # Python dependencies
└── output/                    # Generated JSON files
```

## Technologies used

- **Python** - application language and CLI implementation
- **Requests** - HTTP communication with the official Olympics endpoints
- **FastAPI** - REST API framework and automatic API documentation
- **Uvicorn** - ASGI server hosting the FastAPI application
- **ThreadPoolExecutor** - concurrent retrieval of match detail endpoints
- **JSON** - generated machine-readable output format
