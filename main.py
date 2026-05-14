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
# BANKNIFTY FEED
# =========================
instruments = [
    (MarketFeed.IDX, "25", MarketFeed.Ticker)
]

# =========================
# CONTINUOUS LOOP
# =========================
while True:

    try:

        print("================================")
        print("📡 CONNECTING TO MARKET FEED...")
        print("================================")

        market_feed = MarketFeed(
            dhan_context,
            instruments,
            "v2"
        )

        market_feed.run_forever()

    except Exception as e:

        print("================================")
        print("❌ ERROR :", e)
        print("🔄 RECONNECTING IN 5 SECONDS...")
        print("================================")

        time.sleep(5)