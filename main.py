import requests
import time
from datetime import datetime
from config import CLIENT_ID, ACCESS_TOKEN

# =====================================================
# CONFIG
# =====================================================

SECURITY_ID = "25"          # BANKNIFTY
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

last_5m_bucket = None
last_30m_bucket = None

print("30M BREAKOUT BOT STARTED", flush=True)

# =====================================================
# LOOP
# =====================================================

while True:

    try:

        now = datetime.now()

        # =============================================
        # MARKET TIME
        # =============================================

        if now.hour < 0 or (now.hour == 0 and now.minute < 0):
            time.sleep(5)
            continue

        if now.hour > 23 or (now.hour == 23 and now.minute > 59):
            print("MARKET CLOSED", flush=True)
            break

        # =============================================
        # FETCH LIVE PRICE
        # =============================================

        response = requests.post(url, json=payload, headers=headers)

        data = response.json()

        feed_data = data["data"]

        first_segment = list(feed_data.keys())[0]

        live_price = feed_data[first_segment][SECURITY_ID]["last_price"]

        # =============================================
        # PRINT LIVE PRICE ONLY WHEN CHANGED
        # =============================================

        print(f"LIVE BANKNIFTY = {live_price}", flush=True)

        # =============================================
        # BUILD 5M CANDLE
        # =============================================

        current_5m = now.minute // 5

        if last_5m_bucket is None:
            last_5m_bucket = current_5m

            candle_open = live_price
            candle_high = live_price
            candle_low = live_price

        if current_5m == last_5m_bucket:

            candle_high = max(candle_high, live_price)
            candle_low = min(candle_low, live_price)
            candle_close = live_price

        else:

            # =========================================
            # 5M CANDLE CLOSED
            # =========================================

            print(
                f"5M CLOSED -> "
                f"O={candle_open} "
                f"H={candle_high} "
                f"L={candle_low} "
                f"C={candle_close}",
                flush=True
            )

            prices_5m.append({
                "open": candle_open,
                "high": candle_high,
                "low": candle_low,
                "close": candle_close
            })

            # Keep last 6 candles only
            if len(prices_5m) > 6:
                prices_5m.pop(0)

            # =========================================
            # EVERY 30 MIN UPDATE LEVELS
            # =========================================

            current_30m = now.minute // 30

            if last_30m_bucket is None:
                last_30m_bucket = current_30m

            elif current_30m != last_30m_bucket:

                if len(prices_5m) == 6:

                    highs = [x["high"] for x in prices_5m]
                    lows = [x["low"] for x in prices_5m]

                    level_high = max(highs)
                    level_low = min(lows)

                    print(
                        f"NEW 30M LEVELS -> "
                        f"HIGH={level_high} "
                        f"LOW={level_low}",
                        flush=True
                    )

                last_30m_bucket = current_30m

            # =========================================
            # ENTRY LOGIC
            # =========================================

            if not trade_running and level_high and level_low:

                # LONG ENTRY
                if candle_close > level_high:

                    trade_running = True
                    trade_side = "LONG"

                    entry_price = candle_close

                    sl_price = entry_price - SL_POINTS
                    target_price = entry_price + TARGET_POINTS

                    trail_sl = sl_price

                    print(
                        f"LONG ENTRY = {entry_price} | "
                        f"SL={sl_price} | "
                        f"TARGET={target_price}",
                        flush=True
                    )

                # SHORT ENTRY
                elif candle_close < level_low:

                    trade_running = True
                    trade_side = "SHORT"

                    entry_price = candle_close

                    sl_price = entry_price + SL_POINTS
                    target_price = entry_price - TARGET_POINTS

                    trail_sl = sl_price

                    print(
                        f"SHORT ENTRY = {entry_price} | "
                        f"SL={sl_price} | "
                        f"TARGET={target_price}",
                        flush=True
                    )

            # =========================================
            # RESET NEW 5M CANDLE
            # =========================================

            candle_open = live_price
            candle_high = live_price
            candle_low = live_price
            candle_close = live_price

            last_5m_bucket = current_5m

        # =============================================
        # TRAILING SL MANAGEMENT
        # =============================================

        if trade_running:

            # =========================================
            # LONG TRADE
            # =========================================

            if trade_side == "LONG":

                profit = live_price - entry_price

                if profit >= TRAIL_START:

                    new_trail = live_price - TRAIL_GAP

                    if new_trail > trail_sl:
                        trail_sl = new_trail

                        print(
                            f"LONG TRAIL SL UPDATED = {trail_sl}",
                            flush=True
                        )

                # EXIT CONDITIONS

                if live_price <= trail_sl:

                    print(
                        f"LONG EXIT TRAIL SL = {live_price}",
                        flush=True
                    )

                    trade_running = False

                elif live_price >= target_price:

                    print(
                        f"LONG TARGET HIT = {live_price}",
                        flush=True
                    )

                    trade_running = False

            # =========================================
            # SHORT TRADE
            # =========================================

            elif trade_side == "SHORT":

                profit = entry_price - live_price

                if profit >= TRAIL_START:

                    new_trail = live_price + TRAIL_GAP

                    if new_trail < trail_sl:
                        trail_sl = new_trail

                        print(
                            f"SHORT TRAIL SL UPDATED = {trail_sl}",
                            flush=True
                        )

                # EXIT CONDITIONS

                if live_price >= trail_sl:

                    print(
                        f"SHORT EXIT TRAIL SL = {live_price}",
                        flush=True
                    )

                    trade_running = False

                elif live_price <= target_price:

                    print(
                        f"SHORT TARGET HIT = {live_price}",
                        flush=True
                    )

                    trade_running = False

        time.sleep(5)

    except Exception as e:

        print("ERROR =", e, flush=True)

        time.sleep(5)