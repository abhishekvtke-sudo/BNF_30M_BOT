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
dhan_context = DhanContext(CLIENT_ID, ACCESS_TOKEN)

print("================================")
print("🟢 DHAN CONNECTED SUCCESSFULLY")
print("================================")

# =========================
# BANKNIFTY LIVE FEED
# =========================
instruments = [
    ("IDX_I", "25", MarketFeed.Ticker)
]

feed = MarketFeed(
    dhan_context,
    instruments,
    version="v2"
)

# =========================
# CONNECT WEBSOCKET
# =========================
feed.run_forever()

# =========================
# LIVE LOOP
# =========================
while True:
    try:
        data = feed.get_data()

        print("================================")
        print("📈 LIVE BANKNIFTY DATA")
        print(data)
        print("================================")

        time.sleep(1)

    except Exception as e:
        print("ERROR :", e)
        time.sleep(5)