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
    return client.open_by_key(os.environ['GOOGLE_SHEET_ID']).sheet1

def log_cancellations(store_name, cancelled_orders):
    sheet = get_sheet()
    rows = []
    for order in cancelled_orders:
        rows.append([
            store_name,
            order['order_number'],   # Shopify order name (e.g. #1001)
            order['name'],
            order['phone'],
            order['address'],
            order['products'],
            order['order_date'],
            datetime.now().strftime('%Y-%m-%d')  # logged_at timestamp
        ])
    if rows:
        sheet.append_rows(rows, value_input_option="USER_ENTERED")
        print(f"✅ Appended {len(rows)} cancellations for {store_name}")
