# shopify_api.py
import requests
import pandas as pd

def get_shopify_orders(shop_url, access_token):
    headers = {
        "X-Shopify-Access-Token": access_token,
        "Content-Type": "application/json"
    }
    url = f"https://{shop_url}/admin/api/2023-01/orders.json?status=any&limit=50"

    response = requests.get(url, headers=headers)
    if response.status_code != 200:
        return pd.DataFrame()

    orders = response.json().get("orders", [])
    all_data = []
    for order in orders:
        for item in order.get("line_items", []):
            all_data.append({
                "order_id": order.get("id"),
                "created_at": order.get("created_at"),
                "sku": item.get("sku"),
                "product_id": item.get("product_id"),
                "quantity": item.get("quantity"),
                "price": item.get("price")
            })

    return pd.DataFrame(all_data)
