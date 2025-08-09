import os
import json
import requests
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# --------------------------
# Load secrets from env
# --------------------------
SHOP1_DOMAIN = os.getenv("SHOP1_DOMAIN")
SHOP1_TOKEN = os.getenv("SHOP1_TOKEN")
SHOP2_DOMAIN = os.getenv("SHOP2_DOMAIN")
SHOP2_TOKEN = os.getenv("SHOP2_TOKEN")
GOOGLE_SHEET_ID = os.getenv("GOOGLE_SHEET_ID")
GOOGLE_SERVICE_ACCOUNT_JSON = os.getenv("GOOGLE_SERVICE_ACCOUNT")

if not all([SHOP1_DOMAIN, SHOP1_TOKEN, SHOP2_DOMAIN, SHOP2_TOKEN, GOOGLE_SHEET_ID, GOOGLE_SERVICE_ACCOUNT_JSON]):
    raise ValueError("One or more environment variables are missing!")

# --------------------------
# Google Sheets setup
# --------------------------
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

service_account_info = json.loads(GOOGLE_SERVICE_ACCOUNT_JSON)
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)

sheet = client.open_by_key(GOOGLE_SHEET_ID).sheet1

# --------------------------
# Function to fetch orders from Shopify
# --------------------------
def get_orders(shop_domain, token):
    url = f"https://{shop_domain}/admin/api/2025-01/orders.json"
    headers = {"X-Shopify-Access-Token": token}
    params = {"status": "any", "limit": 5, "order": "created_at desc"}  # Limit to last 5 orders for demo
    response = requests.get(url, headers=headers, params=params)

    if response.status_code != 200:
        raise Exception(f"Error fetching orders from {shop_domain}: {response.text}")

    return response.json().get("orders", [])

# --------------------------
# Fetch and write to sheet
# --------------------------
orders_shop1 = get_orders(SHOP1_DOMAIN, SHOP1_TOKEN)
orders_shop2 = get_orders(SHOP2_DOMAIN, SHOP2_TOKEN)

all_orders = []

for shop_name, orders in [("Shop 1", orders_shop1), ("Shop 2", orders_shop2)]:
    for order in orders:
        all_orders.append([
            shop_name,
            order.get("id"),
            order.get("created_at"),
            order.get("total_price"),
            order.get("currency"),
            order.get("financial_status"),
            order.get("fulfillment_status")
        ])

# Write header + data
sheet.clear()
sheet.append_row(["Shop Name", "Order ID", "Created At", "Total Price", "Currency", "Financial Status", "Fulfillment Status"])
sheet.append_rows(all_orders)

print(f"✅ Synced {len(all_orders)} orders to Google Sheet")
