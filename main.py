import requests
import time
from datetime import datetime
from config import CLIENT_ID, ACCESS_TOKEN

# =====================================================
# CONFIG
# =====================================================

SECURITY_ID = "25"      # BANKNIFTY
SEGMENT = "IDX_I"

SL_POINTS = 75
TARGET_POINTS = 1500

TRAIL_START = 200
TRAIL_GAP = 100

# =====================================================
# HEADERS
# =====================================================

headers = {
    "access-token": ACCESS_TOKEN,
    "client-id": CLIENT_ID,
    "Content-Type": "application/json"
}

url = "https://api.dhan.co/v2/marketfeed/ltp"

payload = {
    SEGMENT: [int(SECURITY_ID)]
}

# =====================================================
# VARIABLES
# =====================================================

prices_5m = []

candle_open = None
candle_high = None
candle_low = None
candle_close = None

level_high = None
level_low = None

trade_running = False
trade_side = None

entry_price = None
sl_price = None
target_price = None
trail_sl = None

last_5m_time = None
last_30m_time = None

last_print_price = None

print("30M BREAKOUT BOT STARTED", flush=True)

# =====================================================
# MAIN LOOP
# =====================================================

while True:

    try:

        now = datetime.now()

        # =================================================
        # MARKET TIME
        # =================================================

        if now.hour < 0 or (now.hour == 0 and now.minute < 1):
            time.sleep(1)
            continue

        if now.hour > 23 or (now.hour == 23 and now.minute > 59):
            print("\nMARKET CLOSED", flush=True)
            break

        # =================================================
        # FETCH LIVE PRICE
        # =================================================

        response = requests.post(
            url,
            json=payload,
            headers=headers
        )

        data = response.json()

        feed_data = data["data"]

        first_segment = list(feed_data.keys())[0]

        live_price = feed_data[first_segment][SECURITY_ID]["last_price"]

        live_price = float(live_price)

        # =================================================
        # PRINT ONLY WHEN PRICE CHANGES
        # =================================================

        if live_price != last_print_price:

            print(
                f"LIVE BANKNIFTY = {live_price}",
                flush=True
            )

            last_print_price = live_price

        # =================================================
        # 5 MIN ALIGNMENT
        # CLOSE ONLY AT:
        # 10,15,20,25,30,35,40...
        # =================================================

        current_5m_time = (
            now.hour,
            now.minute // 5
        )

        # =================================================
        # FIRST CANDLE
        # =================================================

        if last_5m_time is None:

            last_5m_time = current_5m_time

            candle_open = live_price
            candle_high = live_price
            candle_low = live_price
            candle_close = live_price

        # =================================================
        # BUILD CURRENT 5M CANDLE
        # =================================================

        if current_5m_time == last_5m_time:

            candle_high = max(candle_high, live_price)
            candle_low = min(candle_low, live_price)
            candle_close = live_price

        # =================================================
        # 5M CANDLE CLOSED
        # =================================================

        else:

            print(
                f"\n5M CLOSED -> "
                f"O={candle_open} "
                f"H={candle_high} "
                f"L={candle_low} "
                f"C={candle_close}",
                flush=True
            )

            # =============================================
            # SAVE 5M CANDLE
            # =============================================

            prices_5m.append({
                "open": float(candle_open),
                "high": float(candle_high),
                "low": float(candle_low),
                "close": float(candle_close)
            })

            # KEEP ONLY LAST 6 CANDLES
            if len(prices_5m) > 6:
                prices_5m.pop(0)

            # =============================================
            # 30M ALIGNMENT
            # LEVELS ONLY AT:
            # 9:15
            # 9:45
            # 10:15
            # 10:45
            # etc
            # =============================================

            valid_30m = (
                now.minute == 15 or
                now.minute == 45
            )

            current_30m_time = (
                now.hour,
                now.minute
            )

            if valid_30m:

                if current_30m_time != last_30m_time:

                    if len(prices_5m) == 6:

                        highs = [
                            candle["high"]
                            for candle in prices_5m
                        ]

                        lows = [
                            candle["low"]
                            for candle in prices_5m
                        ]

                        level_high = max(highs)
                        level_low = min(lows)

                        print(
                            f"\nNEW 30M LEVELS -> "
                            f"HIGH={level_high} "
                            f"LOW={level_low}",
                            flush=True
                        )

                    last_30m_time = current_30m_time

            # =============================================
            # ENTRY CONDITIONS
            # =============================================

            if not trade_running and level_high and level_low:

                # =========================================
                # LONG ENTRY
                # =========================================

                if candle_close > level_high:

                    trade_running = True
                    trade_side = "LONG"

                    entry_price = candle_close

                    sl_price = entry_price - SL_POINTS
                    target_price = entry_price + TARGET_POINTS

                    trail_sl = sl_price

                    print(
                        f"\nLONG ENTRY = {entry_price} "
                        f"| SL={sl_price} "
                        f"| TARGET={target_price}",
                        flush=True
                    )

                # =========================================
                # SHORT ENTRY
                # =========================================

                elif candle_close < level_low:

                    trade_running = True
                    trade_side = "SHORT"

                    entry_price = candle_close

                    sl_price = entry_price + SL_POINTS
                    target_price = entry_price - TARGET_POINTS

                    trail_sl = sl_price

                    print(
                        f"\nSHORT ENTRY = {entry_price} "
                        f"| SL={sl_price} "
                        f"| TARGET={target_price}",
                        flush=True
                    )

            # =============================================
            # START NEW 5M CANDLE
            # =============================================

            candle_open = live_price
            candle_high = live_price
            candle_low = live_price
            candle_close = live_price

            last_5m_time = current_5m_time

        # =================================================
        # TRAILING STOPLOSS
        # =================================================

        if trade_running:

            # =============================================
            # LONG TRADE
            # =============================================

            if trade_side == "LONG":

                profit = live_price - entry_price

                # START TRAILING
                if profit >= TRAIL_START:

                    new_trail = live_price - TRAIL_GAP

                    if new_trail > trail_sl:

                        trail_sl = new_trail

                        print(
                            f"\nLONG TRAIL SL = {trail_sl}",
                            flush=True
                        )

                # EXIT TRAIL
                if live_price <= trail_sl:

                    print(
                        f"\nLONG EXIT = {live_price}",
                        flush=True
                    )

                    trade_running = False

                # TARGET HIT
                elif live_price >= target_price:

                    print(
                        f"\nLONG TARGET HIT = {live_price}",
                        flush=True
                    )

                    trade_running = False

            # =============================================
            # SHORT TRADE
            # =============================================

            elif trade_side == "SHORT":

                profit = entry_price - live_price

                # START TRAILING
                if profit >= TRAIL_START:

                    new_trail = live_price + TRAIL_GAP

                    if new_trail < trail_sl:

                        trail_sl = new_trail

                        print(
                            f"\nSHORT TRAIL SL = {trail_sl}",
                            flush=True
                        )

                # EXIT TRAIL
                if live_price >= trail_sl:

                    print(
                        f"\nSHORT EXIT = {live_price}",
                        flush=True
                    )

                    trade_running = False

                # TARGET HIT
                elif live_price <= target_price:

                    print(
                        f"\nSHORT TARGET HIT = {live_price}",
                        flush=True
                    )

                    trade_running = False

        time.sleep(1)

    except Exception as e:

        print(f"\nERROR = {e}", flush=True)

        time.sleep(5)