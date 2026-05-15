import requests
import time
from datetime import datetime
from config import CLIENT_ID, ACCESS_TOKEN

# =========================================
# SETTINGS
# =========================================

SECURITY_ID = 491727
SEGMENT = "MCX_COMM"

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
# API
# =========================================

LTP_URL = "https://api.dhan.co/v2/marketfeed/ltp"

# =========================================
# VARIABLES
# =========================================

trade_running = False
trade_side = None

entry_price = 0
trail_sl = 0
tp_price = 0

# 5M candle
five_open = None
five_high = None
five_low = None
five_close = None

# 30M candle
thirty_high = None
thirty_low = None

current_5m_block = None
current_30m_block = None

# =========================================
# GET LIVE PRICE
# =========================================

def get_ltp():

    payload = {
        SEGMENT: [SECURITY_ID]
    }

    response = requests.post(
        LTP_URL,
        json=payload,
        headers=headers
    )

    data = response.json()

    ltp = data["data"][SEGMENT][str(SECURITY_ID)]["last_price"]

    return float(ltp)

# =========================================
# GET 5M BLOCK
# =========================================

def get_5m_block():

    now = datetime.now()

    minute = (now.minute // 5) * 5

    return f"{now.hour}:{minute}"

# =========================================
# GET 30M BLOCK
# =========================================

def get_30m_block():

    now = datetime.now()

    minute = (now.minute // 30) * 30

    return f"{now.hour}:{minute}"

# =========================================
# START
# =========================================

print("30M BREAKOUT BOT STARTED", flush=True)

while True:

    try:

        ltp = get_ltp()

        print(f"LIVE GOLD PRICE = {ltp}", flush=True)

        # =====================================
        # BUILD 5M CANDLE
        # =====================================

        new_5m_block = get_5m_block()

        if current_5m_block != new_5m_block:

            # Previous candle completed
            if five_close is not None:

                print(
                    f"5M CLOSED -> "
                    f"O={five_open} "
                    f"H={five_high} "
                    f"L={five_low} "
                    f"C={five_close}",
                    flush=True
                )

                # =================================
                # ENTRY LOGIC
                # =================================

                if (
                    not trade_running and
                    thirty_high is not None and
                    five_close > thirty_high
                ):

                    trade_running = True
                    trade_side = "LONG"

                    entry_price = five_close

                    trail_sl = entry_price - SL_POINTS
                    tp_price = entry_price + TP_POINTS

                    print(
                        f"LONG ENTRY = {entry_price}",
                        flush=True
                    )

                elif (
                    not trade_running and
                    thirty_low is not None and
                    five_close < thirty_low
                ):

                    trade_running = True
                    trade_side = "SHORT"

                    entry_price = five_close

                    trail_sl = entry_price + SL_POINTS
                    tp_price = entry_price - TP_POINTS

                    print(
                        f"SHORT ENTRY = {entry_price}",
                        flush=True
                    )

            # Start new candle
            current_5m_block = new_5m_block

            five_open = ltp
            five_high = ltp
            five_low = ltp
            five_close = ltp

        else:

            five_high = max(five_high, ltp)
            five_low = min(five_low, ltp)
            five_close = ltp

        # =====================================
        # BUILD 30M LEVELS
        # =====================================

        new_30m_block = get_30m_block()

        if current_30m_block != new_30m_block:

            current_30m_block = new_30m_block

            thirty_high = five_high
            thirty_low = five_low

            print(
                f"\nNEW 30M LEVELS -> "
                f"HIGH={thirty_high} "
                f"LOW={thirty_low}",
                flush=True
            )

        else:

            thirty_high = max(thirty_high, ltp)
            thirty_low = min(thirty_low, ltp)

        # =====================================
        # TRADE MANAGEMENT
        # =====================================

        if trade_running:

            # LONG
            if trade_side == "LONG":

                profit = ltp - entry_price

                # Trailing
                if profit >= TRAIL_START:

                    new_sl = ltp - TRAIL_GAP

                    if new_sl > trail_sl:

                        trail_sl = new_sl

                        print(
                            f"TRAIL SL = {trail_sl}",
                            flush=True
                        )

                # SL HIT
                if ltp <= trail_sl:

                    print(
                        f"LONG EXIT SL = {ltp}",
                        flush=True
                    )

                    trade_running = False

                # TP HIT
                elif ltp >= tp_price:

                    print(
                        f"LONG EXIT TP = {ltp}",
                        flush=True
                    )

                    trade_running = False

            # SHORT
            elif trade_side == "SHORT":

                profit = entry_price - ltp

                # Trailing
                if profit >= TRAIL_START:

                    new_sl = ltp + TRAIL_GAP

                    if new_sl < trail_sl:

                        trail_sl = new_sl

                        print(
                            f"TRAIL SL = {trail_sl}",
                            flush=True
                        )

                # SL HIT
                if ltp >= trail_sl:

                    print(
                        f"SHORT EXIT SL = {ltp}",
                        flush=True
                    )

                    trade_running = False

                # TP HIT
                elif ltp <= tp_price:

                    print(
                        f"SHORT EXIT TP = {ltp}",
                        flush=True
                    )

                    trade_running = False

        # =====================================
        # LOOP SPEED
        # =====================================

        time.sleep(5)

    except Exception as e:

        print(f"ERROR = {e}", flush=True)

        time.sleep(5)