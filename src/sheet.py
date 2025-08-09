import gspread
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime

# Google Sheets setup
SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
CREDS = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", SCOPE)
CLIENT = gspread.authorize(CREDS)

# Replace with your actual sheet name
SHEET_NAME = "Shopify Order Cancellations"
SHEET = CLIENT.open(SHEET_NAME).sheet1


def log_cancellations(cancellations):
    """
    Logs canceled orders to Google Sheets.

    Args:
        cancellations (list of dict): Each dict should have
            'order_id', 'customer_name', 'reason', and optionally 'cancelled_at'.
    """
    if not cancellations:
        print("No cancellations to log.")
        return

    rows = []
    for c in cancellations:
        rows.append([
            c.get("order_id", ""),
            c.get("customer_name", ""),
            c.get("reason", ""),
            c.get("cancelled_at", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S"))
        ])

    # Append in one batch for efficiency
    SHEET.append_rows(rows, value_input_option="USER_ENTERED")
    print(f"✅ Synced {len(rows)} cancellations to Google Sheet")
