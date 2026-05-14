from dhanhq import dhanhq
import os
import time
from datetime import datetime

client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")

dhan = dhanhq(client_id, access_token)

print("================================")
print("✅ CONNECTED TO DHAN")
print("================================")

while True:

    try:

        data = dhan.ohlc_data(
            securities={
                "IDX_I": [25]
            }
        )

        print("================================")
        print("TIME :", datetime.now().strftime("%H:%M:%S"))
        print("BANKNIFTY DATA :")
        print(data)
        print("================================")

    except Exception as e:
        print("❌ ERROR :", e)

    time.sleep(5)