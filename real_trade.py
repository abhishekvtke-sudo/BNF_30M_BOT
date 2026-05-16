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

OPTION_CHAIN_REFRESH = 60

# =========================================================
# API URLS
# =========================================================

BASE_URL = "https://api.dhan.co/v2"

LTP_URL = f"{BASE_URL}/marketfeed/ltp"

OPTION_CHAIN_URL = f"{BASE_URL}/optionchain"

EXPIRY_LIST_URL = f"{BASE_URL}/optionchain/expirylist"

# =========================================================
# HEADERS
# =========================================================

headers = {
    "access-token": ACCESS_TOKEN,
    "client-id": CLIENT_ID,
    "Content-Type": "application/json",
    "Accept": "application/json"
}

# =========================================================
# PAYLOAD
# =========================================================

index_payload = {
    INDEX_SEGMENT: [INDEX_SECURITY_ID]
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
# FETCH BANKNIFTY PRICE
# =========================================================

def get_banknifty_ltp():

    response = requests.post(
        LTP_URL,
        json=index_payload,
        headers=headers
    )

    data = response.json()

    live_price = float(
        data["data"]["IDX_I"]["25"]["last_price"]
    )

    return live_price

# =========================================================
# FETCH EXPIRY LIST
# =========================================================

def get_expiry_list():

    payload = {
        "UnderlyingScrip": INDEX_SECURITY_ID,
        "UnderlyingSeg": INDEX_SEGMENT
    }

    response = requests.post(
        EXPIRY_LIST_URL,
        json=payload,
        headers=headers
    )

    data = response.json()

    return data["data"]

# =========================================================
# FETCH OPTION CHAIN
# =========================================================

def get_option_chain(expiry):

    payload = {
        "UnderlyingScrip": INDEX_SECURITY_ID,
        "UnderlyingSeg": INDEX_SEGMENT,
        "Expiry": expiry
    }

    response = requests.post(
        OPTION_CHAIN_URL,
        json=payload,
        headers=headers
    )

    data = response.json()

    return data["data"]

# =========================================================
# ATM CE PE FETCH
# =========================================================

def get_atm_options(option_chain_data, live_price):

    atm_strike = round(
        live_price / 100
    ) * 100

    oc = option_chain_data["oc"]

    strike_key = f"{atm_strike:.6f}"

    atm_data = oc.get(strike_key)

    if atm_data is None:

        available_strikes = [
            float(x)
            for x in oc.keys()
        ]

        nearest = min(
            available_strikes,
            key=lambda x: abs(x - atm_strike)
        )

        strike_key = f"{nearest:.6f}"

        atm_data = oc[strike_key]

        atm_strike = nearest

    ce_data = atm_data["ce"]

    pe_data = atm_data["pe"]

    ce_security_id = ce_data["securityId"]
    pe_security_id = pe_data["securityId"]

    ce_ltp = float(ce_data["last_price"])
    pe_ltp = float(pe_data["last_price"])

    return {

        "strike": atm_strike,

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

level_high = None
level_low = None

last_5m_time = None
last_30m_time = None

trade_running = False
trade_side = None

entry_price = None
exit_price = None

target_price = None
sl_price = None
trail_sl = None

day_pnl = 0

last_print_price = None

option_chain_data = None
last_option_refresh = 0

atm_ce_security_id = None
atm_pe_security_id = None

atm_ce_ltp = None
atm_pe_ltp = None

atm_strike = None

# =========================================================
# START
# =========================================================

write_log("======================================")
write_log("REAL OPTION PREMIUM BOT STARTED")
write_log("======================================")

# =========================================================
# FETCH INITIAL EXPIRY
# =========================================================

expiry_list = get_expiry_list()

current_expiry = expiry_list[0]

write_log(f"ACTIVE EXPIRY = {current_expiry}")

# =========================================================
# MAIN LOOP
# =========================================================

while True:

    try:

        now = datetime.now()

        # =================================================
        # FETCH BANKNIFTY
        # =================================================

        live_price = get_banknifty_ltp()

        # =================================================
        # OPTION CHAIN REFRESH
        # =================================================

        current_time = time.time()

        if (
            current_time - last_option_refresh
            >= OPTION_CHAIN_REFRESH
        ):

            option_chain_data = get_option_chain(
                current_expiry
            )

            atm_data = get_atm_options(
                option_chain_data,
                live_price
            )

            atm_strike = atm_data["strike"]

            atm_ce_security_id = atm_data[
                "ce_security_id"
            ]

            atm_pe_security_id = atm_data[
                "pe_security_id"
            ]

            atm_ce_ltp = atm_data["ce_ltp"]

            atm_pe_ltp = atm_data["pe_ltp"]

            write_log("")
            write_log(
                f"ATM STRIKE = {atm_strike}"
            )

            write_log(
                f"ATM CE ID = "
                f"{atm_ce_security_id}"
            )

            write_log(
                f"ATM PE ID = "
                f"{atm_pe_security_id}"
            )

            write_log(
                f"ATM CE PREMIUM = "
                f"{atm_ce_ltp}"
            )

            write_log(
                f"ATM PE PREMIUM = "
                f"{atm_pe_ltp}"
            )

            last_option_refresh = current_time

        # =================================================
        # PRINT LIVE PRICE
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

                trade_running = True
                trade_side = "CE"

                entry_price = atm_ce_ltp

                sl_price = (
                    entry_price - OPTION_SL
                )

                target_price = (
                    entry_price + OPTION_TARGET
                )

                trail_sl = sl_price

                write_log("")
                write_log("================================")
                write_log("BUY CE")
                write_log("================================")

                write_log(
                    f"ATM STRIKE = {atm_strike}"
                )

                write_log(
                    f"ENTRY PREMIUM = "
                    f"{entry_price}"
                )

                write_log(
                    f"SL = {sl_price}"
                )

                write_log(
                    f"TARGET = {target_price}"
                )

            # =============================================
            # BUY PE
            # =============================================

            elif live_price < level_low:

                trade_running = True
                trade_side = "PE"

                entry_price = atm_pe_ltp

                sl_price = (
                    entry_price - OPTION_SL
                )

                target_price = (
                    entry_price + OPTION_TARGET
                )

                trail_sl = sl_price

                write_log("")
                write_log("================================")
                write_log("BUY PE")
                write_log("================================")

                write_log(
                    f"ATM STRIKE = {atm_strike}"
                )

                write_log(
                    f"ENTRY PREMIUM = "
                    f"{entry_price}"
                )

                write_log(
                    f"SL = {sl_price}"
                )

                write_log(
                    f"TARGET = {target_price}"
                )

        # =================================================
        # TRADE MANAGEMENT
        # =================================================

        if trade_running:

            current_option_price = (
                atm_ce_ltp
                if trade_side == "CE"
                else atm_pe_ltp
            )

            move = (
                current_option_price -
                entry_price
            )

            # =============================================
            # TRAILING
            # =============================================

            if move >= TRAIL_START:

                new_sl = (
                    current_option_price -
                    TRAIL_GAP
                )

                if new_sl > trail_sl:

                    trail_sl = new_sl

                    write_log(
                        f"TRAIL SL = "
                        f"{trail_sl}"
                    )

            # =============================================
            # EXIT
            # =============================================

            if (
                current_option_price <= trail_sl or
                current_option_price >= target_price
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

        time.sleep(5)

    except Exception as e:

        write_log(f"ERROR = {e}")

        time.sleep(5)