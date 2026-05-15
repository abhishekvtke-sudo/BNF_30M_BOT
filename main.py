import os
import time

from datetime import datetime
from zoneinfo import ZoneInfo

print("STARTED", flush=True)

# =========================================
# IMPORT AFTER START
# =========================================

from dhanhq import dhanhq

print("DHANHQ IMPORTED", flush=True)

# =========================================
# ENV
# =========================================

client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")

print("CLIENT ID LOADED", flush=True)
print("TOKEN LOADED", flush=True)

# =========================================
# LOGIN
# =========================================

dhan = dhanhq(
    client_id,
    access_token
)

print("CONNECTED TO DHAN", flush=True)

# =========================================
# TEST LOOP
# =========================================

while True:

    try:

        print("\n====================", flush=True)

        current_time = datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).strftime("%H:%M:%S")

        print(f"TIME : {current_time}", flush=True)

        data = dhan.quote_data(
            securities={
                "IDX_I": ["23"]
            }
        )

        print(data, flush=True)

        print("====================", flush=True)

    except Exception as e:

        print(f"ERROR : {e}", flush=True)

    time.sleep(5)