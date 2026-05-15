import os
import time

from datetime import datetime
from zoneinfo import ZoneInfo

from dhanhq import dhanhq

# =========================================
# ENV VARIABLES
# =========================================

client_id = os.environ["DHAN_CLIENT_ID"]
access_token = os.environ["DHAN_ACCESS_TOKEN"]

print("CLIENT ID LOADED", flush=True)
print("TOKEN LOADED", flush=True)

# =========================================
# CONNECT TO DHAN
# =========================================

dhan = dhanhq(access_token)

print("CONNECTED TO DHAN", flush=True)

# =========================================
# LIVE LOOP
# =========================================

while True:

    try:

        print("\n========================", flush=True)

        print(
            f"TIME : "
            f"{datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%H:%M:%S')}",
            flush=True
        )

        # =====================================
        # BANKNIFTY INDEX LTP
        # =====================================

        data = dhan.ltp_data(
            {
                "NSE_IDX": [25]
            }
        )

        print("BANKNIFTY DATA :", flush=True)

        print(data, flush=True)

        print("========================", flush=True)

    except Exception as e:

        print(f"ERROR : {e}", flush=True)

    time.sleep(1)