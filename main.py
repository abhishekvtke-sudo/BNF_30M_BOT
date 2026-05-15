import requests
import os
import time

print("SCRIPT STARTED", flush=True)

CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

headers = {
    "access-token": ACCESS_TOKEN,
    "client-id": CLIENT_ID,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

url = "https://api.dhan.co/v2/marketfeed/ltp"

payload = {
    "MCX_COMM": [114]
}

while True:

    response = requests.post(
        url,
        headers=headers,
        json=payload
    )

    data = response.json()

    try:
        price = data["data"]["MCX_COMM"]["114"]["last_price"]
        print("LIVE PRICE =", price, flush=True)

    except Exception as e:
        print("ERROR =", data, flush=True)

    time.sleep(2)