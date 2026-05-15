import os
import time
import requests

print("START", flush=True)

CLIENT_ID = os.environ["DHAN_CLIENT_ID"]
ACCESS_TOKEN = os.environ["DHAN_ACCESS_TOKEN"]

print("CLIENT_ID =", CLIENT_ID, flush=True)
print("TOKEN_START =", ACCESS_TOKEN[:15], flush=True)

print("ENV LOADED", flush=True)

headers = {
    "access-token": ACCESS_TOKEN,
    "client-id": CLIENT_ID,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

print("HEADERS READY", flush=True)

payload = {
    "NSE_EQ": [1333]
}

while True:

    try:

        response = requests.post(
            "https://api.dhan.co/v2/marketfeed/ltp",
            headers=headers,
            json=payload
        )

        print("====================", flush=True)
        print("STATUS:", response.status_code, flush=True)
        print(response.text, flush=True)

    except Exception as e:
        print("ERROR:", e, flush=True)

    time.sleep(60)