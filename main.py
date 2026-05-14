from dhanhq import DhanContext, MarketFeed
from datetime import datetime
import os

# ==================================
# DHAN CREDENTIALS
# ==================================

CLIENT_CODE = os.getenv("DHAN_CLIENT_CODE")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

# ==================================
# DHAN CONNECTION
# ==================================

dhan_context = DhanContext(
    CLIENT_CODE,
    ACCESS_TOKEN
)

print("================================")
print("🟢 DHAN CONNECTED SUCCESSFULLY")
print("================================")

# ==================================
# BANKNIFTY LIVE FEED
# ==================================

instruments = [
    (MarketFeed.IDX, "25", MarketFeed.Ticker)
]

version = "v2"

feed = MarketFeed(
    dhan_context,
    instruments,
    version
)

# ==================================
# LIVE DATA LOOP
# ==================================

while True:

    response = feed.get_data()

    print("================================")
    print("⏰ TIME :", datetime.now().strftime("%H:%M:%S"))
    print("📈 BANKNIFTY LIVE DATA")
    print(response)
    print("================================")