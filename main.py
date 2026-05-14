from dhanhq import dhanhq
from zoneinfo import ZoneInfo
from datetime import datetime
import os
import time

client_id = os.environ["DHAN_CLIENT_ID"]
access_token = os.environ["DHAN_ACCESS_TOKEN"]

print("CLIENT ID LOADED")
print("TOKEN LOADED")

dhan = dhanhq(client_id, access_token)

print("CONNECTED TO DHAN")

while True:

    try:

        print("\n==============================")

        india_time = datetime.now(
            ZoneInfo("Asia/Kolkata")
        )

        print(
            f"TIME : "
            f"{india_time.strftime('%H:%M:%S')}"
        )

        data = dhan.quote_data(
            securities={
                "IDX_I": ["13"]
            }
        )

        print("BANKNIFTY DATA :")

        print(data)

        print("==============================")

    except Exception as e:

        print(f"ERROR : {e}")

    time.sleep(5)