import requests
import time
from datetime import datetime
from config import CLIENT_ID, ACCESS_TOKEN

# =========================================
# SETTINGS
# =========================================

SYMBOL = "GOLDM JUN FUT"

SECURITY_ID = 491727
EXCHANGE_SEGMENT = "MCX_COMM"

QTY = 1

SL_POINTS = 75
TP_POINTS = 1500

TRAIL_START = 200
TRAIL_GAP = 150

# =========================================
# HEADERS
# =========================================

headers = {
    "access-token": ACCESS_TOKEN,
    "client-id": CLIENT_ID,
    "Content-Type": "application/json"
}

# =========================================
# URLS
# =========================================

HISTORICAL_URL = "https://api.dhan.co/v2/charts/intraday"

# =========================================
# TRADE VARIABLES
# =========================================

trade_running = False
trade_side = None

entry_price = 0
sl_price = 0
tp_price = 0
trail_sl = 0

last_5m_time = None

# =========================================
# GET CANDLES
# =========================================

def get_candles(interval):

    payload = {
        "securityId": str(SECURITY_ID),
        "exchangeSegment": EXCHANGE_SEGMENT,
        "instrument": "FUTCOM",
        "interval": interval
    }

    response = requests.post(
        HISTORICAL_URL,
        json=payload,
        headers=headers
    )

    data = response.json()

    print(data, flush=True)

    return data

# =========================================
# GET LATEST 30M LEVELS
# =========================================

def get_30m_levels():

    data = get_candles("30")

    candles = data["data"]

    highs = candles["high"]
    lows = candles["low"]

    last_high = highs[-2]
    last_low = lows[-2]

    return float(last_high), float(last_low)

# =========================================
# GET LATEST 5M CANDLE
# =========================================

def get_latest_5m():

    data = get_candles("5")

    candles = data["data"]

    opens = candles["open"]
    highs = candles["high"]
    lows = candles["low"]
    closes = candles["close"]
    times = candles["start_Time"]

    latest = {
        "time": times[-2],
        "open": float(opens[-2]),
        "high": float(highs[-2]),
        "low": float(lows[-2]),
        "close": float(closes[-2])
    }

    return latest

# =========================================
# MAIN LOOP
# =========================================

print("30M BREAKOUT BOT STARTED", flush=True)

while True:

    try:

        now = datetime.now()

        # =====================================
        # MARKET TIME
        # =====================================

        if now.hour < 9 or (now.hour == 9 and now.minute < 15):

            time.sleep(10)
            continue

        if now.hour > 23 or (now.hour == 23 and now.minute > 15):

            print("MARKET CLOSED", flush=True)
            break

        # =====================================
        # GET LEVELS
        # =====================================

        level_high, level_low = get_30m_levels()

        print(f"\n30M HIGH = {level_high}", flush=True)
        print(f"30M LOW = {level_low}", flush=True)

        # =====================================
        # GET LATEST 5M CANDLE
        # =====================================

        candle_5m = get_latest_5m()

        candle_time = candle_5m["time"]

        # Skip duplicate candle
        if candle_time == last_5m_time:

            time.sleep(10)
            continue

        last_5m_time = candle_time

        close_price = candle_5m["close"]

        print(f"5M CLOSE = {close_price}", flush=True)

        # =====================================
        # ENTRY LOGIC
        # =====================================

        if not trade_running:

            # LONG ENTRY
            if close_price > level_high:

                trade_running = True
                trade_side = "LONG"

                entry_price = close_price

                sl_price = entry_price - SL_POINTS
                tp_price = entry_price + TP_POINTS

                trail_sl = sl_price

                print("\nLONG ENTRY", flush=True)
                print(f"ENTRY = {entry_price}", flush=True)
                print(f"SL = {trail_sl}", flush=True)
                print(f"TP = {tp_price}", flush=True)

            # SHORT ENTRY
            elif close_price < level_low:

                trade_running = True
                trade_side = "SHORT"

                entry_price = close_price

                sl_price = entry_price + SL_POINTS
                tp_price = entry_price - TP_POINTS

                trail_sl = sl_price

                print("\nSHORT ENTRY", flush=True)
                print(f"ENTRY = {entry_price}", flush=True)
                print(f"SL = {trail_sl}", flush=True)
                print(f"TP = {tp_price}", flush=True)

        # =====================================
        # TRADE MANAGEMENT
        # =====================================

        else:

            current_price = close_price

            # =================================
            # LONG
            # =================================

            if trade_side == "LONG":

                profit = current_price - entry_price

                # TRAILING
                if profit >= TRAIL_START:

                    new_sl = current_price - TRAIL_GAP

                    if new_sl > trail_sl:

                        trail_sl = new_sl

                        print(f"TRAIL SL = {trail_sl}", flush=True)

                # SL HIT
                if current_price <= trail_sl:

                    print(f"LONG SL HIT = {current_price}", flush=True)

                    trade_running = False

                # TP HIT
                elif current_price >= tp_price:

                    print(f"LONG TP HIT = {current_price}", flush=True)

                    trade_running = False

            # =================================
            # SHORT
            # =================================

            elif trade_side == "SHORT":

                profit = entry_price - current_price

                # TRAILING
                if profit >= TRAIL_START:

                    new_sl = current_price + TRAIL_GAP

                    if new_sl < trail_sl:

                        trail_sl = new_sl

                        print(f"TRAIL SL = {trail_sl}", flush=True)

                # SL HIT
                if current_price >= trail_sl:

                    print(f"SHORT SL HIT = {current_price}", flush=True)

                    trade_running = False

                # TP HIT
                elif current_price <= tp_price:

                    print(f"SHORT TP HIT = {current_price}", flush=True)

                    trade_running = False

        # =====================================
        # WAIT
        # =====================================

        time.sleep(10)

    except Exception as e:

        print(f"ERROR = {e}", flush=True)

        time.sleep(10)