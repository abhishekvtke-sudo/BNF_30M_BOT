import os
import time

from datetime import datetime
from zoneinfo import ZoneInfo

from dhanhq import DhanContext, dhanhq

# =========================================
# LOAD ENV VARIABLES
# =========================================

client_id = os.environ["DHAN_CLIENT_ID"]
access_token = os.environ["DHAN_ACCESS_TOKEN"]

print("CLIENT ID LOADED", flush=True)
print("TOKEN LOADED", flush=True)

# =========================================
# CONNECT TO DHAN
# =========================================

dhan_context = DhanContext(
    client_id,
    access_token
)

dhan = dhanhq(dhan_context)

print("CONNECTED TO DHAN", flush=True)

# =========================================
# LIVE LOOP
# =========================================

while True:

    try:

        print("\n==============================", flush=True)

        print(
            f"TIME : "
            f"{datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%H:%M:%S')}",
            flush=True
        )

        # =====================================
        # BANKNIFTY QUOTE
        # SECURITY ID = 23
        # =====================================

        data = dhan.quote_data(
            securities={
                "IDX_I": ["23"]
            }
        )

        print("BANKNIFTY DATA :", flush=True)

        print(data, flush=True)

        print("==============================", flush=True)

    except Exception as e:

        print(f"ERROR : {e}", flush=True)

    time.sleep(5)