from dhanhq import DhanContext, MarketFeed
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
dhan_context = DhanContext(
    CLIENT_ID,
    ACCESS_TOKEN
)

print("================================")
print("🟢 DHAN CONNECTED SUCCESSFULLY")
print("================================")

# =========================
# BANKNIFTY LIVE FEED
# =========================
instruments = [
    (MarketFeed.IDX, "25", MarketFeed.Ticker)
]

version = "v2"

market_feed = MarketFeed(
    dhan_context,
    instruments,
    version
)

# =========================
# START FEED
# =========================
try:
    print("================================")
    print("📡 CONNECTING TO MARKET FEED...")
    print("================================")

    market_feed.run_forever()

except Exception as e:
    print("ERROR :", e)

finally:
    market_feed.disconnect()