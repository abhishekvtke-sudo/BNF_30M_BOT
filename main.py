import requests
import time
from datetime import datetime
from config import CLIENT_ID, ACCESS_TOKEN

# ============================================
# CONFIG
# ============================================

SECURITY_ID = 25
SEGMENT = "IDX_I"

SL_POINTS = 75
TARGET_POINTS = 1500

# ============================================
# HEADERS
# ============================================

headers = {
    "access-token": ACCESS_TOKEN,
    "client-id": CLIENT_ID,
    "Content-Type": "application/json"
}

payload = {
    SEGMENT: [SECURITY_ID]
}

url = "https://api.dhan.co/v2/marketfeed/ltp"

print("30M BREAKOUT BOT STARTED", flush=True)

# ============================================
# VARIABLES
# ============================================

current_5m = None
five_min_candles = []

thirty_high = None
thirty_low = None

position = None
entry_price = None

last_print_price = None

# ============================================
# MAIN LOOP
# ============================================

while True:

    try:

        # ====================================
        # GET LIVE PRICE
        # ====================================

        response = requests.post(
            url,
            json=payload,
            headers=headers
        )

        data = response.json()

        live_price = data["data"][SEGMENT][str(SECURITY_ID)]["last_price"]

        # ====================================
        # PRINT ONLY WHEN PRICE CHANGES
        # ====================================

        if live_price != last_print_price:
            print(f"LIVE GOLD PRICE = {live_price}", flush=True)
            last_print_price = live_price

        # ====================================
        # CURRENT TIME
        # ====================================

        now = datetime.now()

        minute_block = now.minute // 5

        # ====================================
        # START NEW 5M CANDLE
        # ====================================

        if current_5m is None:

            current_5m = {
                "block": minute_block,
                "open": live_price,
                "high": live_price,
                "low": live_price,
                "close": live_price
            }

        # ====================================
        # SAME 5M CANDLE
        # ====================================

        elif current_5m["block"] == minute_block:

            current_5m["high"] = max(current_5m["high"], live_price)
            current_5m["low"] = min(current_5m["low"], live_price)
            current_5m["close"] = live_price

        # ====================================
        # 5M CANDLE CLOSED
        # ====================================

        else:

            print(
                f"5M CLOSED -> "
                f"O={current_5m['open']} "
                f"H={current_5m['high']} "
                f"L={current_5m['low']} "
                f"C={current_5m['close']}",
                flush=True
            )

            five_min_candles.append(current_5m)

            # ====================================
            # KEEP ONLY LAST 6 CANDLES
            # ====================================

            if len(five_min_candles) > 6:
                five_min_candles.pop(0)

            # ====================================
            # BUILD TRUE 30M LEVELS
            # ====================================

            if len(five_min_candles) == 6:

                highs = [x["high"] for x in five_min_candles]
                lows = [x["low"] for x in five_min_candles]

                thirty_high = max(highs)
                thirty_low = min(lows)

                print(
                    f"NEW 30M LEVELS -> "
                    f"HIGH={thirty_high} "
                    f"LOW={thirty_low}",
                    flush=True
                )

            # ====================================
            # START NEW CANDLE
            # ====================================

            current_5m = {
                "block": minute_block,
                "open": live_price,
                "high": live_price,
                "low": live_price,
                "close": live_price
            }

        # ====================================
        # ENTRY LOGIC
        # ====================================

        if thirty_high and position is None:

            if live_price > thirty_high:

                position = "LONG"
                entry_price = live_price

                print(
                    f"LONG ENTRY = {entry_price}",
                    flush=True
                )

            elif live_price < thirty_low:

                position = "SHORT"
                entry_price = live_price

                print(
                    f"SHORT ENTRY = {entry_price}",
                    flush=True
                )

        # ====================================
        # LONG EXIT
        # ====================================

        if position == "LONG":

            if live_price >= entry_price + TARGET_POINTS:

                print(
                    f"LONG TARGET HIT = {live_price}",
                    flush=True
                )

                position = None

            elif live_price <= entry_price - SL_POINTS:

                print(
                    f"LONG SL HIT = {live_price}",
                    flush=True
                )

                position = None

        # ====================================
        # SHORT EXIT
        # ====================================

        elif position == "SHORT":

            if live_price <= entry_price - TARGET_POINTS:

                print(
                    f"SHORT TARGET HIT = {live_price}",
                    flush=True
                )

                position = None

            elif live_price >= entry_price + SL_POINTS:

                print(
                    f"SHORT SL HIT = {live_price}",
                    flush=True
                )

                position = None

        time.sleep(1)

    except Exception as e:

        print(f"ERROR = {e}", flush=True)

        time.sleep(5)