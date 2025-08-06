import requests
from datetime import datetime, timedelta
import os
from sheet import log_cancellations

def get_old_unfulfilled_orders(shop, token):
    url = f"https://{shop}/admin/api/2023-07/orders.json"
    five_days_ago = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%dT%H:%M:%S')
    params = {
        "status": "open",
        "fulfillment_status": "unfulfilled",
        "created_at_max": five_days_ago,
        "limit": 250
    }
    headers = {
        "X-Shopify-Access-Token": token
    }
    r = requests.get(url, headers=headers, params=params)
    return r.json().get('orders', [])

def cancel_order(shop, token, order_id):
    url = f"https://{shop}/admin/api/2023-07/orders/{order_id}/cancel.json"
    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }
    r = requests.post(url, headers=headers)
    return r.status_code == 200

def process_store(store_name, shop, token):
    orders = get_old_unfulfilled_orders(shop, token)
    cancelled = []
    for order in orders:
        success = cancel_order(shop, token, order['id'])
        if success:
            cancelled.append({
                'id': order['id'],
                'name': order['customer']['first_name'] + ' ' + order['customer'].get('last_name', ''),
                'phone': order['customer'].get('phone', ''),
                'order_date': order['created_at'][:10]
            })
    if cancelled:
        log_cancellations(store_name, cancelled)

if __name__ == "__main__":
    process_store("Store 1", os.environ['SHOP1_DOMAIN'], os.environ['SHOP1_TOKEN'])
    process_store("Store 2", os.environ['SHOP2_DOMAIN'], os.environ['SHOP2_TOKEN'])

