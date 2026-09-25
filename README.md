# Olympic Football Scraper

> A Python scraper that retrieves official Paris 2024 Olympic football data and
> generates FootyScores-compatible match JSON files.

## What this project does

The application:

1. Fetches the official Olympic football schedule and match data.
2. Filters the schedule to football matches only.
3. Removes duplicate match identifiers.
4. Retrieves scores, half-time scores, scorers, lineups, formations, coaches,
   venues, and competition rounds.
5. Normalizes the data into the structure defined by [`example.json`](../example.json).
6. Writes deterministic JSON files to `output/`.
7. Prints every generated match filename and the total number of files.

It also supports listing available match identifiers without saving files and
retrieving one match by identifier.

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

## Run the scraper

Run from the `task-code` directory:

```powershell
python main.py --output-dir output
```

### Command-line options

The scraper accepts these parameters:

| Option | Default | Description |
| --- | --- | --- |
| `--output-dir PATH` | `output` | Directory for generated JSON files |
| `--timeout SECONDS` | `30` | Maximum time allowed for each HTTP request |
| `--workers COUNT` | `8` | Maximum number of detail requests downloaded concurrently |
| `--list-matches` | disabled | Print each match identifier and its teams without saving files |
| `--match-id ID` | disabled | Retrieve and save only the selected match |

The default mode generates all match files, `matches.json`, and
`generation.json`. The two special modes are mutually exclusive:

```powershell
# Print identifiers and participants only; no files are written
python main.py --list-matches

# Retrieve the single JSON file for an identifier printed above
python main.py --match-id FBLMTEAM11------------GPA-000100--
```

Single-match retrieval saves the result as
`<output-dir>\<match-id>.json`. If the identifier does not exist in the
official football schedule, the command exits with an error.

Example with custom settings:

```powershell
python main.py `
  --output-dir olympic-data `
  --timeout 60 `
  --workers 4
```

Use fewer workers when you want to reduce concurrent traffic. Use a higher
timeout when the network connection is slow. Both `--timeout` and `--workers`
must be greater than zero.

### Run unit tests

The test suite uses Python's standard-library `unittest` module and does not
make network requests:

```powershell
python -m unittest discover -s tests -v
```

To see the built-in command help:

```powershell
python main.py --help
```

The scraper prints output similar to:

```text
FBLMTEAM11------------GPA-000100--.json
FBLMTEAM11------------GPA-000200--.json
...
Total JSON match files: 58
```

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
├── retrieve_data/
│   ├── constants.py           # URLs, headers, and endpoint templates
│   ├── details.py             # Scores, scorers, lineups, and positions
│   ├── endpoint.py            # FootyScores endpoint transformation
│   ├── olympics_fetcher.py    # Data-generation orchestration and CLI
│   ├── parse_utils.py         # Safe JSON value conversion helpers
│   ├── rounds.py              # Round and summary parsing
│   ├── schedule.py            # Schedule parsing and football filtering
│   └── source.py              # HTTP retrieval and concurrent requests
├── main.py                    # Scraper entry point
├── requirements.txt           # Python dependencies
└── output/                    # Generated JSON files
```

## Technologies used

- **Python** - application language and CLI implementation
- **Requests** - HTTP communication with the official Olympics endpoints
- **ThreadPoolExecutor** - concurrent retrieval of match detail endpoints
- **JSON** - generated machine-readable output format
