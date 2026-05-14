from dhanhq import DhanContext, MarketFeed
from datetime import datetime
import os
import time

CLIENT_CODE = os.getenv("DHAN_CLIENT_CODE")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

dhan_context = DhanContext(
    CLIENT_CODE,
    ACCESS_TOKEN
)

print("================================")
print("🟢 DHAN CONNECTED SUCCESSFULLY")
print("================================")

# BANKNIFTY INDEX
instruments = [
    (MarketFeed.IDX, "25", MarketFeed.Ticker)
]

version = "v2"

feed = MarketFeed(
    dhan_context,
    instruments,
    version
)

while True:
    feed.run_forever()

    response = feed.get_data()

    print("================================")
    print("⏰", datetime.now().strftime("%H:%M:%S"))
    print(response)
    print("================================")

    time.sleep(1)