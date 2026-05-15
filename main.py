import os
import time
import requests

# =========================
# DHAN CREDENTIALS
# =========================

CLIENT_ID = os.environ["DHAN_CLIENT_ID"]
ACCESS_TOKEN = os.environ["DHAN_ACCESS_TOKEN"]

# =========================
# HEADERS
# =========================

headers = {
    "access-token": ACCESS_TOKEN,
    "client-id": CLIENT_ID,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# =========================
# GOLDM JUN FUT
# SECURITY ID = 491727
# SEGMENT = MCX_COMM
# =========================

payload = {
    "MCX_COMM": ["491727"]
}

url = "https://api.dhan.co/v2/marketfeed/ltp"

print("GOLD BOT STARTED", flush=True)

while True:
    try:
        response = requests.post(url, json=payload, headers=headers)

        data = response.json()

        if response.status_code == 200:
            ltp = data["data"]["MCX_COMM"]["491727"]["last_price"]
            print(f"LIVE GOLD PRICE = {ltp}", flush=True)

        else:
            print(f"ERROR = {data}", flush=True)

    except Exception as e:
        print(f"EXCEPTION = {e}", flush=True)

    time.sleep(5)