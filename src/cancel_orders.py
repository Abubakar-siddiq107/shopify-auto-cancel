import requests
from datetime import datetime, timedelta
import os
from sheet import log_cancellations

def get_old_unfulfilled_orders(shop, token):
    url = f"https://{shop}/admin/api/2023-07/orders.json"
    five_days_ago = (datetime.utcnow() - timedelta(days=5)).strftime('%Y-%m-%dT%H:%M:%S')
    params = {
        "status": "open",
        "fulfillment_status": "unfulfilled",
        "created_at_max": five_days_ago,
        "limit": 250
    }
    headers = {"X-Shopify-Access-Token": token}
    r = requests.get(url, headers=headers, params=params)
    r.raise_for_status()
    return r.json().get('orders', [])

def cancel_order(shop, token, order_id):
    url = f"https://{shop}/admin/api/2023-07/orders/{order_id}/cancel.json"
    headers = {
        "X-Shopify-Access-Token": token,
        "Content-Type": "application/json"
    }
    r = requests.post(url, headers=headers)
    return r.status_code == 200

def extract_customer_info(order):
    customer_name = "Unknown"
    phone = "Unknown"

    cust = order.get('customer') or {}
    if cust:
        first = cust.get('first_name', '')
        last = cust.get('last_name', '')
        customer_name = (first + ' ' + last).strip() or customer_name
        phone = cust.get('phone') or phone

    # fallback to shipping or billing address
    if (customer_name == "Unknown" or phone == "Unknown"):
        ship = order.get('shipping_address') or {}
        bill = order.get('billing_address') or {}
        if ship:
            name = " ".join(filter(None, [ship.get('first_name', ''), ship.get('last_name', '')])).strip()
            customer_name = name or customer_name
            phone = ship.get('phone') or phone
        if (customer_name == "Unknown" or phone == "Unknown") and bill:
            name = " ".join(filter(None, [bill.get('first_name', ''), bill.get('last_name', '')])).strip()
            customer_name = name or customer_name
            phone = bill.get('phone') or phone

    # final fallback to order-level phone field
    phone = phone or order.get('phone') or "Unknown"
    return customer_name, phone

def process_store(domain_env_key, token_env_key, name_env_key):
    shop = os.environ.get(domain_env_key)
    token = os.environ.get(token_env_key)
    display_name = os.environ.get(name_env_key) or shop  # use friendly name if set, otherwise domain

    if not shop or not token:
        print(f"Missing env for {domain_env_key} or {token_env_key}. Skipping.")
        return

    print(f"Processing store: {display_name} ({shop})")
    orders = get_old_unfulfilled_orders(shop, token)
    cancelled = []

    for order in orders:
        order_id = order.get('id')
        if not order_id:
            continue
        success = cancel_order(shop, token, order_id)
        if success:
            customer_name, phone = extract_customer_info(order)
            cancelled.append({
                'order_number': order.get('name', str(order_id)),  # human-facing order number like #1001
                'name': customer_name,
                'phone': phone,
                'order_date': order.get('created_at', '')[:10]
            })
            print(f"Cancelled {order.get('name','(no-name)')} for {display_name}")

    if cancelled:
        log_cancellations(display_name, cancelled)
    else:
        print(f"No orders cancelled for {display_name}")

if __name__ == "__main__":
    # Pass the ENV NAMES (not literal values). If SHOP1_NAME/SHOP2_NAME are not set, domain will be used.
    process_store('SHOP1_DOMAIN', 'SHOP1_TOKEN', 'SHOP1_NAME')
    process_store('SHOP2_DOMAIN', 'SHOP2_TOKEN', 'SHOP2_NAME')
