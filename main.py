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
dhan_context = DhanContext(CLIENT_ID, ACCESS_TOKEN)

print("================================")
print("🟢 DHAN CONNECTED SUCCESSFULLY")
print("================================")

# =========================
# BANKNIFTY INSTRUMENT
# =========================
instruments = [
    (MarketFeed.IDX_I, "25", MarketFeed.Ticker)
]

# =========================
# CREATE FEED
# =========================
feed = MarketFeed(
    dhan_context,
    instruments,
    version="v2"
)

# IMPORTANT
feed.run_forever()

# =========================
# LIVE DATA LOOP
# =========================
while True:
    response = feed.get_data()

    print("================================")
    print("📈 LIVE BANKNIFTY DATA")
    print(response)
    print("================================")