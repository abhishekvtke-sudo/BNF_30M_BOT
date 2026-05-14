from dhanhq import dhanhq
from datetime import datetime, time as dtime
import os
import time

# ==============================
# DHAN CREDENTIALS (FROM RENDER ENV)
# ==============================
CLIENT_CODE = os.getenv("DHAN_CLIENT_CODE")
ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")

# ==============================
# DHAN LOGIN
# ==============================
dhan = dhanhq(ACCESS_TOKEN)

print("======================================")
print("🟢 DHAN CONNECTED SUCCESSFULLY")
print("======================================")

# ==============================
# BANKNIFTY DETAILS
# ==============================
BANKNIFTY_SECURITY_ID = "25"   # BankNifty Index ID
EXCHANGE_SEGMENT = "IDX_I"

# ==============================
# MARKET TIMINGS
# ==============================
MARKET_START = dtime(9, 15)
MARKET_END   = dtime(15, 30)

# ==============================
# LIVE LOOP
# ==============================
while True:

    try:
        # Current Time
        now = datetime.now()
        current_time = now.time()

        # Fetch Live BankNifty Price
        data = dhan.quote_data(
            security_id=BANKNIFTY_SECURITY_ID,
            exchange_segment=EXCHANGE_SEGMENT
        )

        # Extract LTP
        ltp = data['data']['last_price']

        # Time Left for Market Open
        if current_time < MARKET_START:
            seconds_left = (
                datetime.combine(now.date(), MARKET_START)
                - now
            ).seconds

            mins = seconds_left // 60
            secs = seconds_left % 60

            market_status = f"⏳ MARKET OPENS IN {mins}m {secs}s"

        elif MARKET_START <= current_time <= MARKET_END:
            market_status = "🟢 MARKET IS LIVE"

        else:
            market_status = "🔴 MARKET CLOSED"

        # Clear Display
        print("\n" * 2)

        print("======================================")
        print("🟢 DHAN CONNECTED")
        print("======================================")

        print(f"📈 BANKNIFTY LIVE PRICE : {ltp}")
        print(f"🕒 CURRENT TIME         : {now.strftime('%H:%M:%S')}")
        print(f"{market_status}")

        print("======================================")

        # Refresh every 5 seconds
        time.sleep(5)

    except Exception as e:
        print("❌ ERROR :", e)
        time.sleep(5)