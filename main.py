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

print("CLIENT ID LOADED")
print("TOKEN LOADED")

# =========================================
# LOGIN
# =========================================

dhan = dhanhq(client_id, access_token)

print("CONNECTED TO DHAN")

# =========================================
# LOOP
# =========================================

while True:

    try:

        india_time = datetime.now(
            ZoneInfo("Asia/Kolkata")
        )

        print("\n==============================")

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