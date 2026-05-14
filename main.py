from Dhan_Tradehull import Tradehull
from config import CLIENT_CODE, ACCESS_TOKEN

import pandas as pd
import time
from datetime import datetime

# =====================================================
# LOGIN
# =====================================================

tsl = Tradehull(
    CLIENT_CODE,
    ACCESS_TOKEN,
    mode="access_token"
)

print("CONNECTED TO DHAN")

# =====================================================
# SETTINGS
# =====================================================

SYMBOL = "BANKNIFTY"

SL_POINTS = 75
TARGET_POINTS = 1500

TRAIL_START = 200
TRAIL_GAP = 150

MAX_LONG_TRADES = 2
MAX_SHORT_TRADES = 2

LOT_SIZE = 30

# =====================================================
# VARIABLES
# =====================================================

candles_5m = []

current_candle = None
current_5m_key = None

position = None

entry_price = 0

trail_sl = 0

option_symbol = ""

long_count = 0
short_count = 0

current_30_high = None
current_30_low = None

previous_30_high = None
previous_30_low = None

trade_taken_this_30m = False

# =====================================================
# DAY RESET
# =====================================================

current_day = datetime.now().date()

# =====================================================
# MAIN LOOP
# =====================================================

while True:

    try:

        now = datetime.now()

        # =================================================
        # RESET DAILY COUNTS
        # =================================================

        if datetime.now().date() != current_day:

            current_day = datetime.now().date()

            long_count = 0
            short_count = 0

            print("\nNEW DAY RESET")

        # =================================================
        # TIME FILTER
        # =================================================

        if (
            now.hour < 9 or
            (now.hour == 9 and now.minute < 45)
        ):

            print(
                f"\rWAITING FOR 9:45 AM : {now.strftime('%H:%M:%S')}",
                end=""
            )

            time.sleep(1)

            continue

        # =================================================
        # FORCE EXIT
        # =================================================

        if (
            now.hour == 15 and
            now.minute >= 15
        ):

            if position is not None:

                print("\nFORCE EXIT POSITION")

            print("\nMARKET CLOSED")

            break

        # =================================================
        # LIVE PRICE
        # =================================================

        live_data = tsl.get_ltp_data(SYMBOL)

        if not live_data:

            time.sleep(1)

            continue

        ltp = float(list(live_data.values())[0])

        # =================================================
        # LIVE DISPLAY
        # =================================================

        if position is None:

            print(
                f"\rLIVE BANKNIFTY : {round(ltp,2)}",
                end=""
            )

        # =================================================
        # CREATE 5 MIN CANDLE
        # =================================================

        minute_block = (now.minute // 5) * 5

        candle_time = now.replace(
            minute=minute_block,
            second=0,
            microsecond=0
        )

        candle_key = candle_time.strftime("%Y-%m-%d %H:%M")

        # =================================================
        # FIRST CANDLE
        # =================================================

        if current_5m_key is None:

            current_5m_key = candle_key

            current_candle = {
                "time": candle_key,
                "open": ltp,
                "high": ltp,
                "low": ltp,
                "close": ltp
            }

        # =================================================
        # NEW 5 MIN CANDLE
        # =================================================

        elif candle_key != current_5m_key:

            candles_5m.append(current_candle)

            print("\n")
            print("=================================")
            print("NEW 5 MIN CANDLE CLOSED")
            print("=================================")

            print(current_candle)

            # =============================================
            # START NEW CANDLE
            # =============================================

            current_5m_key = candle_key

            current_candle = {
                "time": candle_key,
                "open": ltp,
                "high": ltp,
                "low": ltp,
                "close": ltp
            }

            # =============================================
            # BUILD 30M LEVELS
            # =============================================

            candle_dt = datetime.strptime(
                candle_key,
                "%Y-%m-%d %H:%M"
            )

            if candle_dt.minute % 30 == 0:

                previous_30_high = current_30_high
                previous_30_low = current_30_low

                trade_taken_this_30m = False

                current_30_high = current_candle["high"]
                current_30_low = current_candle["low"]

                print("\n=================================")
                print("NEW 30 MIN LEVEL CREATED")
                print("=================================")

                print(f"LEVEL HIGH : {previous_30_high}")
                print(f"LEVEL LOW : {previous_30_low}")

            else:

                if current_30_high is None:

                    current_30_high = current_candle["high"]

                    current_30_low = current_candle["low"]

                else:

                    current_30_high = max(
                        current_30_high,
                        current_candle["high"]
                    )

                    current_30_low = min(
                        current_30_low,
                        current_candle["low"]
                    )

            # =============================================
            # ENTRY CONDITIONS
            # =============================================

            if (
                previous_30_high is not None and
                position is None and
                not trade_taken_this_30m
            ):

                latest_close = candles_5m[-1]["close"]

                # =========================================
                # LONG BREAKOUT
                # =========================================

                if (
                    latest_close > previous_30_high and
                    long_count < MAX_LONG_TRADES
                ):

                    atm = round(ltp / 100) * 100

                    option_symbol = (
                        f"BANKNIFTY 28 MAY {atm} CALL"
                    )

                    try:

                        quote = tsl.get_quote_data(
                            [option_symbol]
                        )

                        entry_price = (
                            quote[option_symbol]["last_price"]
                        )

                        trail_sl = (
                            entry_price - SL_POINTS
                        )

                        position = "LONG"

                        trade_taken_this_30m = True

                        long_count += 1

                        print("\n")
                        print("=================================")
                        print("LONG ENTRY")
                        print("=================================")

                        print(f"OPTION : {option_symbol}")

                        print(f"ENTRY : {entry_price}")

                        print(f"SL : {trail_sl}")

                    except Exception as e:

                        print(f"\nENTRY ERROR : {e}")

                # =========================================
                # SHORT BREAKOUT
                # =========================================

                elif (
                    latest_close < previous_30_low and
                    short_count < MAX_SHORT_TRADES
                ):

                    atm = round(ltp / 100) * 100

                    option_symbol = (
                        f"BANKNIFTY 28 MAY {atm} PUT"
                    )

                    try:

                        quote = tsl.get_quote_data(
                            [option_symbol]
                        )

                        entry_price = (
                            quote[option_symbol]["last_price"]
                        )

                        trail_sl = (
                            entry_price - SL_POINTS
                        )

                        position = "SHORT"

                        trade_taken_this_30m = True

                        short_count += 1

                        print("\n")
                        print("=================================")
                        print("SHORT ENTRY")
                        print("=================================")

                        print(f"OPTION : {option_symbol}")

                        print(f"ENTRY : {entry_price}")

                        print(f"SL : {trail_sl}")

                    except Exception as e:

                        print(f"\nENTRY ERROR : {e}")

        # =================================================
        # UPDATE LIVE CANDLE
        # =================================================

        else:

            current_candle["high"] = max(
                current_candle["high"],
                ltp
            )

            current_candle["low"] = min(
                current_candle["low"],
                ltp
            )

            current_candle["close"] = ltp

        # =================================================
        # TRADE MANAGEMENT
        # =================================================

        if position is not None:

            try:

                quote = tsl.get_quote_data(
                    [option_symbol]
                )

                option_ltp = (
                    quote[option_symbol]["last_price"]
                )

                pnl = option_ltp - entry_price

                # =========================================
                # TRAILING
                # =========================================

                if pnl >= TRAIL_START:

                    new_sl = option_ltp - TRAIL_GAP

                    if new_sl > trail_sl:

                        trail_sl = new_sl

                # =========================================
                # LIVE DISPLAY
                # =========================================

                print(
                    f"\rLIVE BANKNIFTY : {round(ltp,2)} | "
                    f"{position} : {round(option_ltp,2)} | "
                    f"PnL : {round(pnl,2)} | "
                    f"SL : {round(trail_sl,2)}",
                    end=""
                )

                # =========================================
                # TARGET HIT
                # =========================================

                if option_ltp >= (
                    entry_price + TARGET_POINTS
                ):

                    print("\n")
                    print("=================================")
                    print("TARGET HIT")
                    print("=================================")

                    print(f"EXIT : {option_ltp}")

                    print(f"PnL : {pnl}")

                    position = None

                # =========================================
                # SL HIT
                # =========================================

                elif option_ltp <= trail_sl:

                    print("\n")
                    print("=================================")
                    print("SL HIT")
                    print("=================================")

                    print(f"EXIT : {option_ltp}")

                    print(f"PnL : {pnl}")

                    position = None

            except Exception as e:

                print(f"\nLIVE ERROR : {e}")

        time.sleep(1)

    except Exception as e:

        print(f"\nMAIN ERROR : {e}")

        time.sleep(1)