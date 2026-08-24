"""Mock supply chain tools."""

from datetime import datetime, timezone
from uuid import uuid4

from app.data.mock_data import INVENTORY, PRODUCT_CATALOG


def check_inventory(sku: str) -> dict:
    product = PRODUCT_CATALOG.get(sku, {"name": "Unknown", "unit": "each"})
    stock = INVENTORY.get(sku, 0)
    return {
        "sku": sku,
        "product_name": product["name"],
        "available_quantity": stock,
        "unit": product["unit"],
        "in_stock": stock > 0,
        "checked_at": datetime.now(timezone.utc).isoformat(),
    }


def create_supply_order(
    customer_name: str,
    items: list[dict],
    delivery_date: str,
    notes: str = "",
) -> dict:
    order_items = []
    total = 0.0
    for item in items:
        sku = item.get("sku", "")
        qty = item.get("quantity", 0)
        catalog = PRODUCT_CATALOG.get(sku, {})
        price = catalog.get("price", 0) * qty
        total += price
        order_items.append({
            "sku": sku,
            "name": catalog.get("name", item.get("name", "Unknown")),
            "quantity": qty,
            "unit": item.get("unit", catalog.get("unit", "each")),
            "line_total": round(price, 2),
        })

    return {
        "order_id": f"SC-{uuid4().hex[:8].upper()}",
        "customer_name": customer_name,
        "items": order_items,
        "delivery_date": delivery_date,
        "total_amount": round(total, 2),
        "status": "confirmed",
        "notes": notes,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
