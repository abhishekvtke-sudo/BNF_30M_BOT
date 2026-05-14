from dhanhq import DhanContext, MarketFeed
from datetime import datetime
import os
import time

# ==========================================
# DHAN CREDENTIALS FROM RENDER ENV VARIABLES
# ==========================================
CLIENT_ID = os.getenv("DHAN_CLIENT_CODE")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

# ==========================================
# DHAN CONTEXT
# ==========================================
dhan_context = DhanContext(
    CLIENT_ID,
    ACCESS_TOKEN
)

print("================================")
print("🟢 DHAN CONNECTED SUCCESSFULLY")
print("================================")

# ==========================================
# BANKNIFTY LIVE MARKET FEED
# ==========================================
# Format:
# (exchange_segment, security_id, subscription_type)

instruments = [
    ("IDX_I", "25", MarketFeed.Ticker)
]

version = "v2"

# ==========================================
# CREATE MARKET FEED
# ==========================================
feed = MarketFeed(
    dhan_context,
    instruments,
    version
)

# ==========================================
# CONNECT TO WEBSOCKET
# ==========================================
print("================================")
print("📡 CONNECTING TO MARKET FEED...")
print("================================")

feed.run_forever()

# ==========================================
# LIVE DATA LOOP
# ==========================================
while True:

    try:

        response = feed.get_data()

        print("================================")
        print("🕒 TIME :", datetime.now().strftime("%H:%M:%S"))
        print("📈 LIVE BANKNIFTY DATA :")
        print(response)
        print("================================")

        time.sleep(1)

    except Exception as e:

        print("❌ ERROR :", e)
        print("🔄 RETRYING IN 5 SECONDS...")
        time.sleep(5)