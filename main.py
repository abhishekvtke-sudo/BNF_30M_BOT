from dhanhq import DhanContext, MarketFeed
from datetime import datetime
import os
import time

# =========================
# DHAN CREDENTIALS
# =========================
CLIENT_CODE = os.getenv("DHAN_CLIENT_CODE")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

# =========================
# DHAN CONTEXT
# =========================
dhan_context = DhanContext(
    CLIENT_CODE,
    ACCESS_TOKEN
)

print("===================================")
print("🟢 DHAN CONNECTED SUCCESSFULLY")
print("===================================")

# =========================
# BANKNIFTY LIVE DATA
# =========================

# BankNifty Index
instruments = [
    (MarketFeed.NSE_FNO, "25", MarketFeed.Ticker)
]

version = "v2"

try:

    data = MarketFeed(
        dhan_context,
        instruments,
        version
    )

    while True:

        data.run_forever()

        response = data.get_data()

        print("===================================")
        print("⏰ TIME :", datetime.now().strftime("%H:%M:%S"))
        print("📈 BANKNIFTY LIVE DATA")
        print(response)
        print("===================================")

        time.sleep(1)

except Exception as e:

    print("ERROR :", e)