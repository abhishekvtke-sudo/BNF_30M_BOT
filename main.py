from dhanhq import DhanContext, MarketFeed
from datetime import datetime
import threading
import os
import time

# ====================================
# DHAN CREDENTIALS
# ====================================
CLIENT_ID = os.getenv("DHAN_CLIENT_CODE")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

# ====================================
# DHAN CONTEXT
# ====================================
dhan_context = DhanContext(
    CLIENT_ID,
    ACCESS_TOKEN
)

print("================================")
print("🟢 DHAN CONNECTED SUCCESSFULLY")
print("================================")

# ====================================
# BANKNIFTY FEED
# ====================================
instruments = [
    ("IDX_I", "25", MarketFeed.Ticker)
]

feed = MarketFeed(
    dhan_context,
    instruments,
    "v2"
)

# ====================================
# RUN WEBSOCKET IN BACKGROUND
# ====================================
def start_feed():
    try:
        print("📡 CONNECTING TO MARKET FEED...")
        feed.run_forever()
    except Exception as e:
        print("❌ FEED ERROR:", e)

threading.Thread(target=start_feed, daemon=True).start()

# Give websocket time to connect
time.sleep(5)

# ====================================
# LIVE DATA LOOP
# ====================================
while True:

    try:

        print("🟢 BOT RUNNING :", datetime.now().strftime("%H:%M:%S"))

        data = feed.get_data()

        if data:
            print("📈 BANKNIFTY DATA :", data)

    except Exception as e:

        print("❌ ERROR :", e)

    time.sleep(1)