import requests
import time
from datetime import datetime
from config import CLIENT_ID, ACCESS_TOKEN

# =========================================================
# CONFIG
# =========================================================

INDEX_SECURITY_ID = 25
INDEX_SEGMENT = "IDX_I"

LOT_SIZE = 30

OPTION_SL = 10
OPTION_TARGET = 20

TRAIL_START = 10
TRAIL_GAP = 5

EXPIRY = "2026-05-26"

# =========================================================
# URLS
# =========================================================

LTP_URL = "https://api.dhan.co/v2/marketfeed/ltp"

OPTION_CHAIN_URL = "https://api.dhan.co/v2/optionchain"

# =========================================================
# HEADERS
# =========================================================

headers = {

    "access-token": ACCESS_TOKEN,
    "client-id": CLIENT_ID,
    "Content-Type": "application/json"

}

# =========================================================
# PAYLOADS
# =========================================================

index_payload = {

    "IDX_I": [25]

}

option_payload = {

    "UnderlyingScrip": 25,
    "UnderlyingSeg": "IDX_I",
    "Expiry": EXPIRY

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

    print(final_message, flush=True)

    with open("trade_logs.txt", "a") as file:
        file.write(final_message + "\n")

# =========================================================
# GET BANKNIFTY LTP
# =========================================================

def get_banknifty_ltp():

    response = requests.post(

        LTP_URL,
        json=index_payload,
        headers=headers

    )

    data = response.json()

    if "data" not in data:

        write_log(f"BAD RESPONSE = {data}")
        return None

    if "IDX_I" not in data["data"]:

        write_log(f"BAD RESPONSE = {data}")
        return None

    live_price = float(

        data["data"]["IDX_I"]["25"]["last_price"]

    )

    return live_price

# =========================================================
# GET ATM OPTIONS
# =========================================================

def get_atm_options(live_price):

    response = requests.post(

        OPTION_CHAIN_URL,
        json=option_payload,
        headers=headers

    )

    data = response.json()

    if "data" not in data:

        write_log(f"BAD RESPONSE = {data}")
        return None

    option_data = data["data"]

    if "oc" not in option_data:

        write_log("OC DATA NOT FOUND")
        return None

    oc = option_data["oc"]

    atm_strike = round(
        live_price / 100
    ) * 100

    strike_key = None

    for strike in oc.keys():

        if int(float(strike)) == atm_strike:

            strike_key = strike
            break

    if strike_key is None:

        write_log("ATM STRIKE NOT FOUND")
        return None

    ce_data = oc[strike_key]["ce"]
    pe_data = oc[strike_key]["pe"]

    ce_security_id = ce_data.get(
        "security_id"
    )

    pe_security_id = pe_data.get(
        "security_id"
    )

    ce_ltp = float(
        ce_data.get("last_price", 0)
    )

    pe_ltp = float(
        pe_data.get("last_price", 0)
    )

    return {

        "atm": atm_strike,

        "ce_security_id": ce_security_id,
        "pe_security_id": pe_security_id,

        "ce_ltp": ce_ltp,
        "pe_ltp": pe_ltp

    }

# =========================================================
# VARIABLES
# =========================================================

prices_5m = []

candle_open = None
candle_high = None
candle_low = None
candle_close = None

last_5m_time = None
last_30m_time = None

level_high = None
level_low = None

trade_running = False
trade_side = None

entry_price = None
target_price = None
trail_sl = None

day_pnl = 0

last_print_price = None
last_option_fetch_price = None

# =========================================================
# START
# =========================================================

write_log("")
write_log("====================================")
write_log("REAL OPTION PREMIUM BOT STARTED")
write_log("====================================")

# =========================================================
# MAIN LOOP
# =========================================================

while True:

    try:

        now = datetime.now()

        # =================================================
        # MARKET HOURS FILTER
        # =================================================

        market_open = (

            (
                now.hour > 9 or
                (
                    now.hour == 9 and
                    now.minute >= 15
                )
            )

            and

            (
                now.hour < 15 or
                (
                    now.hour == 15 and
                    now.minute <= 15
                )
            )

        )

        if not market_open:

            write_log("MARKET CLOSED")

            time.sleep(60)

            continue

        # =================================================
        # LIVE BANKNIFTY
        # =================================================

        live_price = get_banknifty_ltp()

        if live_price is None:

            time.sleep(15)
            continue

        if live_price != last_print_price:

            write_log(
                f"LIVE BANKNIFTY = {live_price}"
            )

            last_print_price = live_price

        # =================================================
        # ATM OPTIONS
        # =================================================

        option_data = None

        if live_price != last_option_fetch_price:

           option_data = get_atm_options(live_price)

           last_option_fetch_price = live_price

        if option_data is None:

            time.sleep(15)
            continue

        atm_strike = option_data["atm"]

        atm_ce_ltp = option_data["ce_ltp"]
        atm_pe_ltp = option_data["pe_ltp"]

        write_log(

            f"ATM STRIKE = {atm_strike} | "
            f"ATM CE PREMIUM = {atm_ce_ltp} | "
            f"ATM PE PREMIUM = {atm_pe_ltp}"
        )

        # =================================================
        # BUILD 5M CANDLE
        # =================================================

        current_5m = (

            now.hour,
            now.minute // 5

        )

        if current_5m != last_5m_time:

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

        current_30m = (
            now.hour,
            now.minute
        )

        if valid_30m:

            if current_30m != last_30m_time:

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
                        "30M LEVELS CREATED"
                    )

                    write_log(
                        f"30M HIGH = {level_high}"
                    )

                    write_log(
                        f"30M LOW = {level_low}"
                    )

                last_30m_time = current_30m

        # =================================================
        # ENTRY CONDITIONS
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

                write_log("")
                write_log(
                    "BREAKOUT ABOVE 30M HIGH"
                )

                trade_running = True

                trade_side = "CE"

                entry_price = atm_ce_ltp

                target_price = (
                    entry_price +
                    OPTION_TARGET
                )

                trail_sl = (
                    entry_price -
                    OPTION_SL
                )

                write_log("")
                write_log("==========================")
                write_log("BUY CE")
                write_log("==========================")

                write_log(
                    f"ENTRY PREMIUM = "
                    f"{entry_price}"
                )

                write_log(
                    f"TARGET = "
                    f"{target_price}"
                )

                write_log(
                    f"SL = "
                    f"{trail_sl}"
                )

            # =============================================
            # BUY PE
            # =============================================

            elif live_price < level_low:

                write_log("")
                write_log(
                    "BREAKOUT BELOW 30M LOW"
                )

                trade_running = True

                trade_side = "PE"

                entry_price = atm_pe_ltp

                target_price = (
                    entry_price +
                    OPTION_TARGET
                )

                trail_sl = (
                    entry_price -
                    OPTION_SL
                )

                write_log("")
                write_log("==========================")
                write_log("BUY PE")
                write_log("==========================")

                write_log(
                    f"ENTRY PREMIUM = "
                    f"{entry_price}"
                )

                write_log(
                    f"TARGET = "
                    f"{target_price}"
                )

                write_log(
                    f"SL = "
                    f"{trail_sl}"
                )

        # =================================================
        # TRADE MANAGEMENT
        # =================================================

        if trade_running:

            if trade_side == "CE":

                current_option_price = atm_ce_ltp

            else:

                current_option_price = atm_pe_ltp

            move = (

                current_option_price -
                entry_price

            )

            # =============================================
            # TRAIL SL
            # =============================================

            if move >= TRAIL_START:

                new_trail = (

                    current_option_price -
                    TRAIL_GAP

                )

                if new_trail > trail_sl:

                    trail_sl = new_trail

                    write_log(

                        f"TRAIL SL = "
                        f"{trail_sl}"

                    )

            # =============================================
            # FORCE EXIT
            # =============================================

            force_exit = (

                now.hour == 15 and
                now.minute >= 15

            )

            # =============================================
            # EXIT
            # =============================================

            if (

                current_option_price <= trail_sl or
                current_option_price >= target_price or
                force_exit

            ):

                exit_price = current_option_price

                pnl = (

                    exit_price -
                    entry_price

                ) * LOT_SIZE

                day_pnl += pnl

                write_log("")
                write_log("================================")
                write_log("EXIT TRADE")
                write_log("================================")

                if force_exit:

                    write_log(
                        "EXIT REASON = FORCE EXIT 3:15"
                    )

                write_log(

                    f"EXIT PREMIUM = "
                    f"{exit_price}"

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

        # =================================================
        # LOOP DELAY
        # =================================================

        time.sleep(5)

    except Exception as e:

        write_log(
            f"ERROR = {e}"
        )

        time.sleep(5)