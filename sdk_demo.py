"""
sdk_demo.py — Demonstrates using the generated Python SDK to interact with the
Inventory Management API. Run this AFTER:

  1. runapplication.bat (backend must be live at http://localhost:8000)
  2. generate_sdk.bat   (SDK must be generated in ./inventory_sdk/)
  3. cd inventory_sdk && pip install -e .

Usage:
    python sdk_demo.py
"""

import sys
import os

# Allow running from the project root even if SDK isn't installed as a package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "inventory_sdk"))

try:
    from inventory_sdk.api.items_api import ItemsApi
    from inventory_sdk.api_client import ApiClient
    from inventory_sdk.configuration import Configuration
    from inventory_sdk.models.item_create import ItemCreate
    from inventory_sdk.models.stock_update import StockUpdate
except ImportError:
    print(
        "\n[ERROR] SDK not found.\n"
        "  Run generate_sdk.bat first, then: cd inventory_sdk && pip install -e .\n"
    )
    sys.exit(1)


def main():
    print("\n" + "=" * 60)
    print("  Inventory Management Python SDK — Demo")
    print("=" * 60)

    # ── Configure SDK client ──────────────────────────────────
    config = Configuration(host="http://localhost:8000")
    client = ApiClient(configuration=config)
    api = ItemsApi(api_client=client)

    # ── 1. List all items ─────────────────────────────────────
    print("\n[1] Fetching all inventory items...")
    result = api.list_items_items_get()
    print(f"    Total items : {result.total}")
    print(f"    Low stock   : {result.low_stock_count}")
    for item in result.items[:5]:
        flag = "⚠ LOW" if item.low_stock else "✓ OK "
        print(f"    [{flag}] #{item.id:3d} {item.name:<30} qty={item.quantity}")

    # ── 2. Add a new item ─────────────────────────────────────
    print("\n[2] Adding a new item via SDK...")
    new_item = api.add_item_items_post(
        item_create=ItemCreate(name="SDK Demo Widget", quantity=42)
    )
    print(f"    Created: #{new_item.id} — {new_item.name} (qty={new_item.quantity})")

    # ── 3. Update stock (valid) ───────────────────────────────
    print(f"\n[3] Updating stock for item #{new_item.id} to 5 (triggers low-stock)...")
    updated = api.update_stock_items_item_id_stock_patch(
        item_id=new_item.id,
        stock_update=StockUpdate(quantity=5),
    )
    print(f"    Updated qty={updated.quantity}, low_stock={updated.low_stock}")

    # ── 4. Demonstrate trick logic: negative stock rejected ───
    print(f"\n[4] Attempting to set stock to -1 (should fail)...")
    try:
        api.update_stock_items_item_id_stock_patch(
            item_id=new_item.id,
            stock_update=StockUpdate(quantity=-1),
        )
        print("    [UNEXPECTED] Request succeeded — this should not happen!")
    except Exception as exc:
        print(f"    [EXPECTED] Rejected: {exc}")

    # ── 5. Get specific item ──────────────────────────────────
    print(f"\n[5] Fetching single item #{new_item.id}...")
    fetched = api.get_item_items_item_id_get(item_id=new_item.id)
    print(f"    {fetched.name} — qty={fetched.quantity}, low_stock={fetched.low_stock}")

    # ── 6. Delete the demo item ──────────────────────────────
    print(f"\n[6] Deleting demo item #{new_item.id}...")
    delete_resp = api.delete_item_items_item_id_delete(item_id=new_item.id)
    print(f"    {delete_resp.message}")

    print("\n" + "=" * 60)
    print("  SDK Demo completed successfully!")
    print("=" * 60 + "\n")


if __name__ == "__main__":
    main()
