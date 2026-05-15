import os
import time

from datetime import datetime
from zoneinfo import ZoneInfo

print("STARTED", flush=True)

# =========================================
# IMPORT
# =========================================

from dhanhq import dhanhq
from dhanhq import DhanContext

print("DHANHQ IMPORTED", flush=True)

# =========================================
# ENV VARIABLES
# =========================================

client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")

print("CLIENT ID LOADED", flush=True)
print("TOKEN LOADED", flush=True)

# =========================================
# CREATE DHAN CONTEXT
# =========================================

dhan_context = DhanContext(
    client_id=client_id,
    access_token=access_token
)

print("DHAN CONTEXT CREATED", flush=True)

# =========================================
# CONNECT TO DHAN
# =========================================

dhan = dhanhq(dhan_context)

print("CONNECTED TO DHAN", flush=True)

# =========================================
# LIVE LOOP
# =========================================

while True:

    try:

        print("\n==========================", flush=True)

        current_time = datetime.now(
            ZoneInfo("Asia/Kolkata")
        ).strftime("%H:%M:%S")

        print(f"TIME : {current_time}", flush=True)

        # =====================================
        # BANKNIFTY INDEX DATA
        # =====================================

        data = dhan.quote_data(
            {
                "IDX_I":[23]
                
                }
        )

        print("BANKNIFTY DATA :", flush=True)

        print(data, flush=True)

        print("==========================", flush=True)

    except Exception as e:

        print(f"ERROR : {e}", flush=True)

    time.sleep(5)