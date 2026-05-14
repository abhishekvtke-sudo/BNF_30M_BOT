from dhanhq import DhanContext, dhanhq
from datetime import datetime
import os
import time

# =========================
# DHAN CREDENTIALS
# =========================
CLIENT_ID = os.getenv("DHAN_CLIENT_CODE")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

# =========================
# DHAN LOGIN
# =========================
dhan_context = DhanContext(CLIENT_ID, ACCESS_TOKEN)
dhan = dhanhq(dhan_context)

print("================================")
print("🟢 DHAN CONNECTED SUCCESSFULLY")
print("================================")

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
        print("🕒 TIME :", datetime.now().strftime("%H:%M:%S"))
        print("📈 BANKNIFTY DATA :")
        print(data)
        print("================================")

    except Exception as e:

        print("❌ ERROR :", e)

    time.sleep(5)