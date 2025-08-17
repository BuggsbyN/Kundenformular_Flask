import os
import json
import gspread
from typing import Dict, List
from google.oauth2.service_account import Credentials
from config import HEADER  # -> Stelle sicher, dass config.py eine Konstante HEADER = [...] enthält

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
WORKSHEET_TITLE = "Kundendaten"  # Tab-Name im Spreadsheet


def get_client():
    raw_json = os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    if not raw_json:
        raise RuntimeError("GOOGLE_SERVICE_ACCOUNT_JSON fehlt in Environment Variables!")
    info = json.loads(raw_json)
    scopes = ["https://www.googleapis.com/auth/spreadsheets"]
    creds = Credentials.from_service_account_info(info, scopes=scopes)
    return gspread.authorize(creds)


def _open_sheet():

    spreadsheet_id = os.getenv("SPREADSHEET_ID")
    if not spreadsheet_id:
        raise RuntimeError("SPREADSHEET_ID fehlt in .env")

    client = get_client()
    ss = client.open_by_key(spreadsheet_id)

    try:
        ws = ss.worksheet(WORKSHEET_TITLE)
    except gspread.exceptions.WorksheetNotFound:
        # Neues Arbeitsblatt mit ausreichenden Spalten/Zeilen anlegen
        ws = ss.add_worksheet(
            title=WORKSHEET_TITLE,
            rows=2000,
            cols=max(26, len(HEADER))
        )
    return ws


def ensure_header() -> None:

    ws = _open_sheet()
    first = ws.row_values(1)
    if first != HEADER:
        # Neue Signatur von gspread: values zuerst, dann range_name (oder benannte Argumente)
        ws.update(values=[HEADER], range_name="A1")


def append_customer(data: Dict[str, str]) -> None:

    ws = _open_sheet()

    row: List[str] = []
    for col in HEADER:
        val = data.get(col, "")
        if isinstance(val, list):
            val = ", ".join(val)
        row.append("" if val is None else str(val))

    ws.append_row(row, value_input_option="RAW")


# --- Optional: kleine Helfer, falls du später lesen willst ---

def get_all_rows() -> List[List[str]]:

    ws = _open_sheet()
    return ws.get_all_values()


def health_check() -> str:

    ws = _open_sheet()
    ok_header = (ws.row_values(1) == HEADER)
    return f"Worksheet: {ws.title} | Header ok: {ok_header}"





