import os
import requests
import pandas as pd
from datetime import datetime, timedelta

def fetch_cancelled_orders(store_url, api_key, api_password, days=1):
    since = (datetime.utcnow() - timedelta(days=days)).isoformat() + "Z"
    url = f"https://{api_key}:{api_password}@{store_url}/admin/api/2023-10/orders.json"
    params = {
        "status": "cancelled",
        "created_at_min": since,
        "limit": 250
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        print(f"Failed to fetch data from {store_url}. Response: {response.text}")
        return pd.DataFrame()

    orders = response.json().get("orders", [])
    print(f"Fetched {len(orders)} cancelled orders from {store_url}.")
    if not orders:
        return pd.DataFrame()

    df = pd.DataFrame([{
        "Order ID": order["id"],
        "Name": order["name"],
        "Cancelled At": order["cancelled_at"],
        "Email": order["email"],
        "Total Price": order["total_price"],
        "Reason": order["cancel_reason"]
    } for order in orders])

    return df

def save_to_csv(df, filename):
    if df.empty:
        print(f"No data to save for {filename}.")
        return
    df.to_csv(filename, index=False)
    print(f"Saved to {filename}")

def main():
    # Store 1
    df1 = fetch_cancelled_orders(
        os.environ["STORE1_URL"],
        os.environ["STORE1_API_KEY"],
        os.environ["STORE1_API_PASSWORD"]
    )
    save_to_csv(df1, "cancelled_orders_store1.csv")

    # Store 2
    df2 = fetch_cancelled_orders(
        os.environ["STORE2_URL"],
        os.environ["STORE2_API_KEY"],
        os.environ["STORE2_API_PASSWORD"]
    )
    save_to_csv(df2, "cancelled_orders_store2.csv")

if __name__ == "__main__":
    main()
