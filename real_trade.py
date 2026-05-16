import requests
import time
from datetime import datetime
from config import CLIENT_ID, ACCESS_TOKEN

# =====================================================
# CONFIG
# =====================================================

SECURITY_ID = "25"      # BANKNIFTY
SEGMENT = "IDX_I"

EXPIRY = "26 MAY"

SL_POINTS = 75
TARGET_POINTS = 1500

TRAIL_START = 200
TRAIL_GAP = 100

MAX_TRADES_PER_DAY = 4

LOT_SIZE = 30

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
# LOG FUNCTION
# =====================================================

def write_log(message):

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    final_message = f"{timestamp} -> {message}"

    print(final_message, flush=True)

    with open("trade_logs.txt", "a") as f:
        f.write(final_message + "\n")

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

selected_option = None

option_entry_price = None
option_exit_price = None

DAY_PNL = 0

last_5m_time = None
last_30m_time = None

last_print_price = None

today_trades = 0
last_reset_day = None

write_log("30M BREAKOUT BOT STARTED")

# =====================================================
# MAIN LOOP
# =====================================================

while True:

    try:

        now = datetime.now()

        # =================================================
        # DAILY RESET
        # =================================================

        if last_reset_day != now.date():

            today_trades = 0
            DAY_PNL = 0

            last_reset_day = now.date()

            write_log("DAILY RESET DONE")

        # =================================================
        # MARKET TIME
        # =================================================

        if now.hour < 9 or (now.hour == 9 and now.minute < 15):

            time.sleep(1)

            continue

        if now.hour > 15 or (now.hour == 15 and now.minute > 15):

            write_log("MARKET CLOSED")

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

        # =================================================
        # SAFE DHAN RESPONSE PARSING
        # =================================================

        feed_data = data["data"]

        if len(feed_data) == 0:

            write_log("NO DATA RECEIVED")

            time.sleep(1)

            continue

        first_segment = list(feed_data.keys())[0]

        segment_data = feed_data[first_segment]

        security_data = segment_data(str(SECURITY_ID))

        if security_data is None:

            security_data = segment_data(int(SECURITY_ID))

        if security_data is None:

            write_log("SECURITY DATA NOT FOUND")

            time.sleep(1)

            continue

        live_price = security_data["last_price"]

        live_price = float(live_price)

        # =================================================
        # ATM OPTION CALCULATION
        # =================================================

        atm_strike = round(live_price / 100) * 100

        ce_symbol = f"BANKNIFTY {EXPIRY} {atm_strike} CE"

        pe_symbol = f"BANKNIFTY {EXPIRY} {atm_strike} PE"

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

            write_log(
                f"5M CLOSED -> "
                f"O={candle_open} "
                f"H={candle_high} "
                f"L={candle_low} "
                f"C={candle_close}"
            )

            # =================================================
            # SAVE 5M CANDLE
            # =================================================

            prices_5m.append({
                "open": float(candle_open),
                "high": float(candle_high),
                "low": float(candle_low),
                "close": float(candle_close)
            })

            # KEEP ONLY LAST 6 CANDLES

            if len(prices_5m) > 6:

                prices_5m.pop(0)

            # =================================================
            # 30M LEVEL CREATION
            # =================================================

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

                        write_log(
                            f"NEW 30M LEVELS -> "
                            f"HIGH={level_high} "
                            f"LOW={level_low}"
                        )

                    last_30m_time = current_30m_time

            # =================================================
            # ENTRY CONDITIONS
            # =================================================

            if (
                not trade_running and
                level_high and
                level_low and
                today_trades < MAX_TRADES_PER_DAY
            ):

                # =================================================
                # LONG ENTRY
                # =================================================

                if candle_close > level_high:

                    trade_running = True

                    trade_side = "LONG"

                    selected_option = ce_symbol

                    option_entry_price = round(
                        live_price * 0.02,
                        2
                    )

                    entry_price = candle_close

                    sl_price = entry_price - SL_POINTS

                    target_price = entry_price + TARGET_POINTS

                    trail_sl = sl_price

                    today_trades += 1

                    write_log(
                        f"LONG ENTRY = {entry_price}"
                    )

                    write_log(
                        f"SELECTED OPTION = {selected_option}"
                    )

                    write_log(
                        f"OPTION ENTRY PRICE = {option_entry_price}"
                    )

                    write_log(
                        f"SL={sl_price} | TARGET={target_price}"
                    )

                # =================================================
                # SHORT ENTRY
                # =================================================

                elif candle_close < level_low:

                    trade_running = True

                    trade_side = "SHORT"

                    selected_option = pe_symbol

                    option_entry_price = round(
                        live_price * 0.02,
                        2
                    )

                    entry_price = candle_close

                    sl_price = entry_price + SL_POINTS

                    target_price = entry_price - TARGET_POINTS

                    trail_sl = sl_price

                    today_trades += 1

                    write_log(
                        f"SHORT ENTRY = {entry_price}"
                    )

                    write_log(
                        f"SELECTED OPTION = {selected_option}"
                    )

                    write_log(
                        f"OPTION ENTRY PRICE = {option_entry_price}"
                    )

                    write_log(
                        f"SL={sl_price} | TARGET={target_price}"
                    )

            # =================================================
            # START NEW 5M CANDLE
            # =================================================

            candle_open = live_price

            candle_high = live_price

            candle_low = live_price

            candle_close = live_price

            last_5m_time = current_5m_time

        # =================================================
        # TRAILING STOPLOSS
        # =================================================

        if trade_running:

            # =================================================
            # LONG TRADE
            # =================================================

            if trade_side == "LONG":

                profit = live_price - entry_price

                if profit >= TRAIL_START:

                    new_trail = live_price - TRAIL_GAP

                    if new_trail > trail_sl:

                        trail_sl = new_trail

                        write_log(
                            f"LONG TRAIL SL = {trail_sl}"
                        )

                # EXIT

                if live_price <= trail_sl:

                    option_exit_price = round(
                        live_price * 0.02,
                        2
                    )

                    trade_pnl = (
                        option_exit_price -
                        option_entry_price
                    ) * LOT_SIZE

                    DAY_PNL += trade_pnl

                    write_log(
                        f"LONG EXIT = {live_price}"
                    )

                    write_log(
                        f"OPTION EXIT PRICE = {option_exit_price}"
                    )

                    write_log(
                        f"TRADE PNL = {trade_pnl}"
                    )

                    write_log(
                        f"DAY PNL = {DAY_PNL}"
                    )

                    trade_running = False

                # TARGET HIT

                elif live_price >= target_price:

                    option_exit_price = round(
                        live_price * 0.02,
                        2
                    )

                    trade_pnl = (
                        option_exit_price -
                        option_entry_price
                    ) * LOT_SIZE

                    DAY_PNL += trade_pnl

                    write_log(
                        f"LONG TARGET HIT = {live_price}"
                    )

                    write_log(
                        f"OPTION EXIT PRICE = {option_exit_price}"
                    )

                    write_log(
                        f"TRADE PNL = {trade_pnl}"
                    )

                    write_log(
                        f"DAY PNL = {DAY_PNL}"
                    )

                    trade_running = False

            # =================================================
            # SHORT TRADE
            # =================================================

            elif trade_side == "SHORT":

                profit = entry_price - live_price

                if profit >= TRAIL_START:

                    new_trail = live_price + TRAIL_GAP

                    if new_trail < trail_sl:

                        trail_sl = new_trail

                        write_log(
                            f"SHORT TRAIL SL = {trail_sl}"
                        )

                # EXIT

                if live_price >= trail_sl:

                    option_exit_price = round(
                        live_price * 0.02,
                        2
                    )

                    trade_pnl = (
                        option_exit_price -
                        option_entry_price
                    ) * LOT_SIZE

                    DAY_PNL += trade_pnl

                    write_log(
                        f"SHORT EXIT = {live_price}"
                    )

                    write_log(
                        f"OPTION EXIT PRICE = {option_exit_price}"
                    )

                    write_log(
                        f"TRADE PNL = {trade_pnl}"
                    )

                    write_log(
                        f"DAY PNL = {DAY_PNL}"
                    )

                    trade_running = False

                # TARGET HIT

                elif live_price <= target_price:

                    option_exit_price = round(
                        live_price * 0.02,
                        2
                    )

                    trade_pnl = (
                        option_exit_price -
                        option_entry_price
                    ) * LOT_SIZE

                    DAY_PNL += trade_pnl

                    write_log(
                        f"SHORT TARGET HIT = {live_price}"
                    )

                    write_log(
                        f"OPTION EXIT PRICE = {option_exit_price}"
                    )

                    write_log(
                        f"TRADE PNL = {trade_pnl}"
                    )

                    write_log(
                        f"DAY PNL = {DAY_PNL}"
                    )

                    trade_running = False

        time.sleep(1)

    except Exception as e:

        write_log(f"ERROR = {e}")

        time.sleep(5)