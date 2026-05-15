import requests
import time
import os

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
    "MCX_COMM": [491727]
}

print("SCRIPT STARTED")

while True:

    try:

        response = requests.post(
            url,
            json=payload,
            headers=headers
        )

        data = response.json()

        if response.status_code == 200:

            price = data["data"]["MCX_COMM"]["491727"]["last_price"]

            print("LIVE PRICE =", price)

        else:

            print("ERROR =", data)

    except Exception as e:

        print("EXCEPTION =", e)

    # IMPORTANT
    time.sleep(15)