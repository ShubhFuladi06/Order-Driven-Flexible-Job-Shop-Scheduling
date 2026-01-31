import os
import json


def load_all_orders(base_path):
    data = []

    if not os.path.exists(base_path):
        return data

    for filename in os.listdir(base_path):
        if filename.endswith(".json"):
            file_path = os.path.join(base_path, filename)
            with open(file_path, 'r') as f:
                try:
                    orders = json.load(f)
                    data.append({
                        "user": filename.split("_")[0],
                        "filename": filename,
                        "orders": orders
                    })
                except Exception as e:
                    print(f"Failed to parse {filename}: {e}")
    
    return data


def analyze_orders(all_data):
    product_summary = {}
    for entry in all_data:
        for order in entry["orders"]:
            product = order.get("product", "Unknown").lower()
            qty = int(order.get("quantity", 0))
            product_summary[product] = product_summary.get(product, 0) + qty

    print("Parsed product summary:", product_summary)

    return {
        "product_summary": product_summary
    }

# scheduler.py

def flatten_all_orders(all_data):
    """
    Flattens all orders into a single list for table rendering.
    Each item will include product, quantity, user, and source file info.
    """
    flat_orders = []

    for entry in all_data:
        username = entry["user"]
        filename = entry["filename"]
        for order in entry["orders"]:
            flat_orders.append({
                "user": username,
                "filename": filename,
                "product": order.get("product", "Unknown"),
                "quantity": order.get("quantity", 0)
            })

    return flat_orders
