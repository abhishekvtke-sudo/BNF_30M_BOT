from dhanhq import dhanhq
import os
import time
from datetime import datetime

# =========================
# READ ENV VARIABLES
# =========================

client_id = os.environ["DHAN_CLIENT_ID"]
access_token = os.environ["DHAN_ACCESS_TOKEN"]

print("CLIENT ID LOADED")
print("TOKEN LOADED")

# =========================
# CONNECT DHAN
# =========================

dhan = dhanhq(client_id, access_token)

print("✅ CONNECTED TO DHAN")

# =========================
# LIVE LOOP
# =========================

while True:

    try:

        data = dhan.ohlc_data(
            securities={
                "IDX_I": [25]
            }
        )

        print("================================")
        print("TIME :", datetime.now().strftime("%H:%M:%S"))
        print(data)
        print("================================")

    except Exception as e:
        print("❌ ERROR :", e)

    time.sleep(5)