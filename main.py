from dhanhq import DhanContext, MarketFeed
from datetime import datetime
import asyncio
import os

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
# BANKNIFTY INSTRUMENT
# ====================================
instruments = [
    ("IDX_I", "25", MarketFeed.Ticker)
]

# ====================================
# MARKET FEED
# ====================================
feed = MarketFeed(
    dhan_context,
    instruments,
    "v2"
)

# ====================================
# LIVE FEED LOOP
# ====================================
async def start_feed():

    print("📡 CONNECTING TO MARKET FEED...")

    await feed.connect()

    print("✅ MARKET FEED CONNECTED")

    while True:

        response = await feed.get_instrument_data()

        print("================================")
        print("🕒 TIME :", datetime.now().strftime("%H:%M:%S"))
        print("📈 LIVE BANKNIFTY DATA :")
        print(response)
        print("================================")

        await asyncio.sleep(1)

# ====================================
# START PROGRAM
# ====================================
asyncio.run(start_feed())