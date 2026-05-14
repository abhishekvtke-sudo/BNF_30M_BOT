from dhanhq import DhanContext, dhanhq
from datetime import datetime
import os
import time

# ==============================
# DHAN CONFIG
# ==============================

CLIENT_ID = os.getenv("DHAN_CLIENT_ID")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

# ==============================
# CONNECT DHAN
# ==============================

dhan_context = DhanContext(CLIENT_ID, ACCESS_TOKEN)
dhan = dhanhq(dhan_context)

print("================================", flush=True)
print("🟢 DHAN CONNECTED SUCCESSFULLY", flush=True)
print("================================", flush=True)

# ==============================
# LIVE LOOP
# ==============================

while True:

    try:

        data = dhan.ohlc_data(
            securities={
                "IDX_I": [25]
            }
        )

        print("================================", flush=True)
        print("🕒 TIME :", datetime.now().strftime("%H:%M:%S"), flush=True)
        print("📈 BANKNIFTY DATA :", flush=True)
        print(data, flush=True)
        print("================================", flush=True)

    except Exception as e:

        print("❌ ERROR :", e, flush=True)

    time.sleep(5)