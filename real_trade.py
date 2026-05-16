import requests
import time
from datetime import datetime
from config import CLIENT_ID, ACCESS_TOKEN

# =========================================================
# CONFIG
# =========================================================

INDEX_SECURITY_ID = "25"      # BANKNIFTY
INDEX_SEGMENT = "IDX_I"

# =========================================================
# OPTION CONFIG
# =========================================================

LOT_SIZE = 30

OPTION_SL = 10
OPTION_TARGET = 20

TRAIL_START = 10
TRAIL_GAP = 5

EXPIRY = "26 MAY"

# =========================================================
# MANUAL OPTION SECURITY IDS
# UPDATE DAILY
# =========================================================

CE_SECURITY_ID = "123456"
PE_SECURITY_ID = "654321"

# =========================================================
# API
# =========================================================

url = "https://api.dhan.co/v2/marketfeed/ltp"

headers = {
    "access-token": ACCESS_TOKEN,
    "client-id": CLIENT_ID,
    "Content-Type": "application/json"
}

# =========================================================
# INDEX PAYLOAD
# =========================================================

index_payload = {
    INDEX_SEGMENT: [int(INDEX_SECURITY_ID)]
}

# =========================================================
# LOG FUNCTION
# =========================================================

def write_log(message):

    current_time = datetime.now().strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    final_message = (
        f"{current_time} -> {message}"
    )

    print(final_message)

    with open("trade_logs.txt", "a") as file:
        file.write(final_message + "\n")

# =========================================================
# OPTION LTP FUNCTION
# =========================================================

def get_option_ltp(security_id):

    option_payload = {
        "NSE_FNO": [int(security_id)]
    }

    response = requests.post(
        url,
        json=option_payload,
        headers=headers
    )

    data = response.json()

    option_price = float(
        data["data"]["NSE_FNO"][str(security_id)]["last_price"]
    )

    return option_price

# =========================================================
# VARIABLES
# =========================================================

prices_5m = []

candle_open = None
candle_high = None
candle_low = None
candle_close = None

level_high = None
level_low = None

last_5m_time = None
last_30m_time = None

trade_running = False
trade_side = None

spot_entry = None

option_symbol = None
option_security_id = None

option_entry_price = None
option_exit_price = None

option_sl_price = None
option_target_price = None
trail_sl = None

day_pnl = 0

last_print_price = None

# =========================================================
# START
# =========================================================

write_log("======================================")
write_log("REAL OPTION PREMIUM BOT STARTED")
write_log("======================================")

# =========================================================
# MAIN LOOP
# =========================================================

while True:

    try:

        now = datetime.now()

        # =================================================
        # FETCH BANKNIFTY SPOT
        # =================================================

        response = requests.post(
            url,
            json=index_payload,
            headers=headers
        )

        data = response.json()

        live_price = float(
            data["data"]["IDX_I"]["25"]["last_price"]
        )

        # =================================================
        # PRINT ONLY ON CHANGE
        # =================================================

        if live_price != last_print_price:

            write_log(
                f"LIVE BANKNIFTY = {live_price}"
            )

            last_print_price = live_price

        # =================================================
        # BUILD 5M CANDLE
        # =================================================

        current_5m = (
            now.hour,
            now.minute // 5
        )

        if last_5m_time != current_5m:

            if candle_open is not None:

                prices_5m.append({

                    "open": candle_open,
                    "high": candle_high,
                    "low": candle_low,
                    "close": candle_close

                })

                write_log(
                    f"5M CLOSED -> "
                    f"O={candle_open} "
                    f"H={candle_high} "
                    f"L={candle_low} "
                    f"C={candle_close}"
                )

                if len(prices_5m) > 6:
                    prices_5m.pop(0)

            candle_open = live_price
            candle_high = live_price
            candle_low = live_price
            candle_close = live_price

            last_5m_time = current_5m

        else:

            candle_high = max(
                candle_high,
                live_price
            )

            candle_low = min(
                candle_low,
                live_price
            )

            candle_close = live_price

        # =================================================
        # CREATE 30M LEVELS
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
                        x["high"]
                        for x in prices_5m
                    ]

                    lows = [
                        x["low"]
                        for x in prices_5m
                    ]

                    level_high = max(highs)
                    level_low = min(lows)

                    write_log("")
                    write_log(
                        f"30M LEVELS CREATED"
                    )

                    write_log(
                        f"HIGH = {level_high}"
                    )

                    write_log(
                        f"LOW = {level_low}"
                    )

                last_30m_time = current_30m_time

        # =================================================
        # ENTRY
        # =================================================

        if (
            trade_running == False and
            level_high is not None and
            level_low is not None
        ):

            # =============================================
            # BUY CE
            # =============================================

            if live_price > level_high:

                strike = round(
                    live_price / 100
                ) * 100

                option_symbol = (
                    f"BANKNIFTY "
                    f"{EXPIRY} "
                    f"{strike} CE"
                )

                option_security_id = CE_SECURITY_ID

                option_entry_price = get_option_ltp(
                    option_security_id
                )

                option_sl_price = (
                    option_entry_price -
                    OPTION_SL
                )

                option_target_price = (
                    option_entry_price +
                    OPTION_TARGET
                )

                trail_sl = option_sl_price

                spot_entry = live_price

                trade_running = True
                trade_side = "CE"

                write_log("")
                write_log("================================")
                write_log("BUY CE")
                write_log("================================")

                write_log(
                    f"OPTION = {option_symbol}"
                )

                write_log(
                    f"SPOT ENTRY = {spot_entry}"
                )

                write_log(
                    f"OPTION ENTRY = "
                    f"{option_entry_price}"
                )

                write_log(
                    f"OPTION SL = "
                    f"{option_sl_price}"
                )

                write_log(
                    f"OPTION TARGET = "
                    f"{option_target_price}"
                )

            # =============================================
            # BUY PE
            # =============================================

            elif live_price < level_low:

                strike = round(
                    live_price / 100
                ) * 100

                option_symbol = (
                    f"BANKNIFTY "
                    f"{EXPIRY} "
                    f"{strike} PE"
                )

                option_security_id = PE_SECURITY_ID

                option_entry_price = get_option_ltp(
                    option_security_id
                )

                option_sl_price = (
                    option_entry_price -
                    OPTION_SL
                )

                option_target_price = (
                    option_entry_price +
                    OPTION_TARGET
                )

                trail_sl = option_sl_price

                spot_entry = live_price

                trade_running = True
                trade_side = "PE"

                write_log("")
                write_log("================================")
                write_log("BUY PE")
                write_log("================================")

                write_log(
                    f"OPTION = {option_symbol}"
                )

                write_log(
                    f"SPOT ENTRY = {spot_entry}"
                )

                write_log(
                    f"OPTION ENTRY = "
                    f"{option_entry_price}"
                )

                write_log(
                    f"OPTION SL = "
                    f"{option_sl_price}"
                )

                write_log(
                    f"OPTION TARGET = "
                    f"{option_target_price}"
                )

        # =================================================
        # TRADE MANAGEMENT
        # =================================================

        if trade_running:

            option_ltp = get_option_ltp(
                option_security_id
            )

            # =============================================
            # TRAILING
            # =============================================

            move = (
                option_ltp -
                option_entry_price
            )

            if move >= TRAIL_START:

                new_sl = (
                    option_ltp -
                    TRAIL_GAP
                )

                if new_sl > trail_sl:

                    trail_sl = new_sl

                    write_log(
                        f"OPTION TRAIL SL = "
                        f"{trail_sl}"
                    )

            # =============================================
            # EXIT
            # =============================================

            if (
                option_ltp <= trail_sl or
                option_ltp >= option_target_price
            ):

                option_exit_price = option_ltp

                pnl = (
                    option_exit_price -
                    option_entry_price
                ) * LOT_SIZE

                day_pnl += pnl

                write_log("")
                write_log("================================")
                write_log("EXIT TRADE")
                write_log("================================")

                write_log(
                    f"OPTION EXIT = "
                    f"{option_exit_price}"
                )

                write_log(
                    f"TRADE PNL = "
                    f"{pnl}"
                )

                write_log(
                    f"DAY PNL = "
                    f"{day_pnl}"
                )

                trade_running = False
                trade_side = None
                option_symbol = None

        # =================================================
        # FORCE EXIT
        # =================================================

        if now.hour == 15 and now.minute >= 15:

            if trade_running:

                write_log("")
                write_log(
                    "FORCE EXIT 3:15 PM"
                )

                trade_running = False
                trade_side = None

        time.sleep(1)

    except Exception as e:

        write_log(f"ERROR = {e}")

        time.sleep(2)