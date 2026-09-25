BASE_URL = "https://stacy.olympics.com/OG2024"
DATA_URL = f"{BASE_URL}/data"
LABELS_URL = f"{BASE_URL}/locales/eng/labels.json"

EVENT_CODE_LENGTH = 22
START_LIST_FILE = "SCH_StartList~comp=OG2024~disc=FBL~lang=ENG.json"
EVENT_UNITS_FILE = "GLO_EventUnits~comp=OG2024~disc=FBL~lang=ENG.json"
EVENT_GAMES_TEMPLATE = "GLO_EventGames~comp=OG2024~event={event_code}~lang=ENG.json"
PHASES_TEMPLATE = "SEL_Phases~comp=OG2024~lang=ENG~event={event_code}.json"
RESULT_TEMPLATE = (
    "RES_ByRSC_H2H~comp=OG2024~disc=FBL"
    "~rscResult={match_code}~lang=ENG.json"
)

KNOWN_POSITIONS = {
    "GK", "RB", "LB", "CB", "RWB", "LWB", "DM", "CM", "AM",
    "RW", "LW", "ST", "FW", "DF", "MF",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept": "application/json,text/plain,*/*",
    "Referer": "https://www.olympics.com/",
    "Origin": "https://www.olympics.com",
}
