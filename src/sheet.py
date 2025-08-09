import gspread
import json
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime
import os

def get_sheet():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_json = json.loads(os.environ['GOOGLE_SERVICE_ACCOUNT'])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_json, scope)
    client = gspread.authorize(creds)
    sheet = client.open_by_key(os.environ['GOOGLE_SHEET_ID']).sheet1
    return sheet

def log_cancellations(store_name, cancelled_orders):
    if not cancelled_orders:
        return

    sheet = get_sheet()

    # Prepare all rows in one list to avoid per-row quota issues
    rows = [
        [
            store_name,
            order['id'],
            order['name'],
            order['phone'],
            order['order_date'],
            datetime.now().strftime('%Y-%m-%d')
        ]
        for order in cancelled_orders
    ]

    # Append all at once (one API call)
    sheet.append_rows(rows)
