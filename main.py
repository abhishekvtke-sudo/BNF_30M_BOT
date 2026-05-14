from dhanhq import DhanContext, MarketFeed
import os
import asyncio
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
# INSTRUMENTS
# =========================
instruments = [
    ("IDX_I", "25", MarketFeed.Ticker)
]

# =========================
# MARKET FEED
# =========================
feed = MarketFeed(
    dhan_context,
    instruments,
    version="v2"
)

# =========================
# MAIN FUNCTION
# =========================
async def start_feed():

    await feed.connect()

    while True:
        try:
            data = await feed.get_instrument_data()

            print("================================")
            print("📈 LIVE BANKNIFTY DATA")
            print(data)
            print("================================")

            time.sleep(1)

        except Exception as e:
            print("ERROR :", e)
            await asyncio.sleep(5)

# =========================
# RUN
# =========================
asyncio.run(start_feed())