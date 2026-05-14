from dhanhq import DhanContext, MarketFeed
from datetime import datetime
import os
import time

# =========================
# DHAN CREDENTIALS
# =========================
CLIENT_ID = os.getenv("DHAN_CLIENT_CODE")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

# =========================
# DHAN CONTEXT
# =========================
dhan_context = DhanContext(CLIENT_ID, ACCESS_TOKEN)

print("================================")
print("🟢 DHAN CONNECTED SUCCESSFULLY")
print("================================")

# =========================
# BANKNIFTY LIVE FEED
# =========================
instruments = [
    (MarketFeed.NSE_IDX, "25", MarketFeed.Ticker)
]

# =========================
# MARKET FEED
# =========================
feed = MarketFeed(
    dhan_context,
    instruments,
    version="v2"
)

# =========================
# LIVE LOOP
# =========================
while True:

    try:

        print("📡 CONNECTING TO MARKET FEED...")

        feed.run_forever()

        while True:

            data = feed.get_data()

            print("================================")
            print("🕒 TIME :", datetime.now().strftime("%H:%M:%S"))
            print("📈 LIVE DATA :", data)
            print("================================")

            time.sleep(1)

    except Exception as e:

        print("❌ ERROR :", e)
        print("🔄 RECONNECTING IN 5 SECONDS...")
        time.sleep(5)