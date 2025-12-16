
import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:5000/api"

def test_calendar_flow():
    print("--- Starting Calendar Flow Test ---")

    # 1. Create a Receipt
    # We'll use today's date so it shows up in the 'default' view (current month) presumably,
    # or a fixed date. Let's use a fixed date "2025-12-01" as per the user's mockup year.
    test_date = "2025-12-01"
    print(f"1. Creating Receipt for date: {test_date}...")
    
    payload = {
        "shop": "Test Shop Biedronka",
        "date": test_date,
        "items": [
            {
                "name": "Mleko Testowe",
                "category": "nabiał",
                "quantity": 2,
                "price": 3.50,
                "unit": "l",
                "expiry_date": "2025-12-10"
            },
            {
                "name": "Chleb Testowy",
                "category": "pieczywo",
                "quantity": 1,
                "price": 4.20,
                "unit": "szt",
                "expiry_date": "2025-12-03"
            }
        ]
    }
    
    try:
        res = requests.post(f"{BASE_URL}/receipts", json=payload)
        if res.status_code == 201:
            data = res.json()
            receipt_id = data['receipt']['id']
            print(f"   [SUCCESS] Receipt created. ID: {receipt_id}")
        else:
            print(f"   [FAIL] creating receipt: {res.text}")
            return
            
        # 2. Fetch Receipts (Calendar Data Source)
        print("2. Fetching all receipts (Simulating Calendar Load)...")
        res = requests.get(f"{BASE_URL}/receipts")
        if res.status_code == 200:
            receipts = res.json()
            # Find our receipt
            found = False
            for r in receipts:
                if r['id'] == receipt_id and r['data_zakupu'] == test_date:
                    found = True
                    print(f"   [SUCCESS] Found receipt {receipt_id} in list.")
                    break
            if not found:
                print(f"   [FAIL] Receipt {receipt_id} not found in list!")
        else:
             print(f"   [FAIL] fetching receipts: {res.text}")

        # 3. Fetch Receipt Details (Modal Data Source)
        print(f"3. Fetching details for Receipt {receipt_id}...")
        res = requests.get(f"{BASE_URL}/receipts/{receipt_id}")
        if res.status_code == 200:
            details = res.json()
            r_data = details['receipt']
            items = details['items']
            
            # Verify totals
            expected_total = 2 * 3.50 + 1 * 4.20 # 7.00 + 4.20 = 11.20
            if abs(float(r_data['suma_total']) - expected_total) < 0.01:
                 print(f"   [SUCCESS] Total sum correct: {r_data['suma_total']}")
            else:
                 print(f"   [FAIL] Total sum mismatch. Expected {expected_total}, got {r_data['suma_total']}")
                 
            # Verify items count
            if len(items) == 2:
                print(f"   [SUCCESS] Item count correct: {len(items)}")
            else:
                print(f"   [FAIL] Item count mismatch: {len(items)}")
                
            # Verify product name persistence (Migration v4 check)
            if items[0].get('product_name') == "Mleko Testowe":
                 print(f"   [SUCCESS] Product Name persisted correctly: {items[0]['product_name']}")
            else:
                 print(f"   [FAIL] Product Name missing or wrong: {items[0].get('product_name')}")

        else:
            print(f"   [FAIL] fetching details: {res.text}")

    except Exception as e:
        print(f"   [ERROR] Exception during test: {e}")

if __name__ == "__main__":
    test_calendar_flow()
