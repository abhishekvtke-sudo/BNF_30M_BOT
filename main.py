import requests
import time
import os

print("STEP 1")

CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

print("STEP 2")

print("CLIENT =", CLIENT_ID)

headers = {
    "access-token": ACCESS_TOKEN,
    "client-id": CLIENT_ID,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

print("STEP 3")

url = "https://api.dhan.co/v2/marketfeed/ltp"

payload = {
    "MCX_COMM": [491727]
}

print("STEP 4")

while True:

    print("LOOP START")

    try:

        response = requests.post(
            url,
            json=payload,
            headers=headers
        )

        print("STATUS =", response.status_code)

        print(response.text)

    except Exception as e:

        print("ERROR =", e)

    time.sleep(15)