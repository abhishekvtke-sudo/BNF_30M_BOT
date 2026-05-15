import os
import time

from dhanhq import dhanhq
from datetime import datetime
from zoneinfo import ZoneInfo

# =====================================
# ENV VARIABLES
# =====================================

client_id = os.environ["DHAN_CLIENT_ID"]
access_token = os.environ["DHAN_ACCESS_TOKEN"]

print("CLIENT ID LOADED", flush=True)
print("TOKEN LOADED", flush=True)

# =====================================
# DHAN CONNECTION
# =====================================

dhan = dhanhq(access_token)

print("CONNECTED TO DHAN", flush=True)

# =====================================
# LOOP
# =====================================

while True:

    try:

        print("\n====================", flush=True)

        print(
            f"TIME : {datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%H:%M:%S')}",
            flush=True
        )

        data = dhan.quote_data(
            securities={
                "IDX_I": ["25"]
            }
        )

        print("BANKNIFTY DATA :", flush=True)
        print(data, flush=True)

    except Exception as e:

        print(f"ERROR : {e}", flush=True)

    time.sleep(1)