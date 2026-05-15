import os
import time

from datetime import datetime
from zoneinfo import ZoneInfo

from Dhan_Tradehull import Tradehull

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

print("CONNECTING TO DHAN...", flush=True)

tsl = Tradehull(
    client_id,
    access_token,
    mode="access_token"
)

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

        print("FETCHING LIVE DATA...", flush=True)

        # =====================================
        # LIVE DATA
        # =====================================

        live_data = tsl.get_ltp_data("BANKNIFTY")

        print("RAW DATA RECEIVED", flush=True)

        # =====================================
        # CHECK DATA
        # =====================================

        if not live_data:

            print("NO LIVE DATA", flush=True)

            time.sleep(1)

            continue

        # =====================================
        # EXTRACT LTP
        # =====================================

        ltp = float(list(live_data.values())[0])

        print(f"LIVE LTP : {ltp}", flush=True)

        print(live_data, flush=True)

        print("==============================", flush=True)

    except Exception as e:

        print(f"ERROR : {e}", flush=True)

    time.sleep(5)