import os
import time
from datetime import datetime

from dhanhq import DhanContext, dhanhq

# =========================================
# LOAD ENV VARIABLES
# =========================================

client_id = os.environ["DHAN_CLIENT_ID"]
access_token = os.environ["DHAN_ACCESS_TOKEN"]

print("CLIENT ID LOADED")
print("TOKEN LOADED")

# =========================================
# DHAN LOGIN
# =========================================

dhan_context = DhanContext(
    client_id,
    access_token
)

dhan = dhanhq(dhan_context)

print("CONNECTED TO DHAN")

# =========================================
# LIVE LOOP
# =========================================

while True:

    try:

        # BANKNIFTY OHLC
        data = dhan.ohlc_data(
            securities={
                "IDX_I": [25]
            }
        )

        print("\n==============================")
        print("TIME :", datetime.now().strftime("%H:%M:%S"))
        print("==============================")
        print(data)
        print("==============================")

    except Exception as e:

        print("\nERROR :", e)

    time.sleep(5)