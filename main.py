from dhanhq import DhanContext, MarketFeed
import os

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

market_feed = MarketFeed(
    dhan_context,
    instruments,
    "v2"
)

# =========================
# START WEBSOCKET
# =========================
print("================================")
print("📡 CONNECTING TO MARKET FEED...")
print("================================")

market_feed.run_forever()