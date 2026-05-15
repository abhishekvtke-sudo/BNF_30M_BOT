import requests
import time
import os

print("SCRIPT STARTED")

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

while True:

    print("REQUEST SENT")

    try:

        response = requests.post(
            url,
            json=payload,
            headers=headers
        )

        print("STATUS =", response.status_code)

        data = response.json()

        print("FULL DATA =", data)

        if response.status_code == 200:

            price = data["data"]["MCX_COMM"]["491727"]["last_price"]

            print("LIVE PRICE =", price)

    except Exception as e:

        print("ERROR =", e)

    time.sleep(15)