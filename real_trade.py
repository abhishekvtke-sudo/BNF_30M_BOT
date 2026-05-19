import requests
import time
import pytz
from datetime import datetime, timedelta, time as dt_time

from config import CLIENT_ID, ACCESS_TOKEN

IST = pytz.timezone("Asia/Kolkata")
# =========================================================
# DHAN CLIENT
# =========================================================

headers = {
    "access-token": ACCESS_TOKEN,
    "client-id": CLIENT_ID,
    "Content-Type": "application/json"
}

# =========================================================
# CONFIG
# =========================================================

INDEX_SECURITY_ID = 25
INDEX_SEGMENT = "IDX_I"

BANKNIFTY_LOT_SIZE = 30
NUM_LOTS = 1

REAL_QTY = (
    BANKNIFTY_LOT_SIZE *
    NUM_LOTS
)

OPTION_SL = 40
OPTION_TARGET = 800

TRAIL_START = 100
TRAIL_GAP = 80

EXPIRY = "2026-05-26"

# =========================================================
# URLS
# =========================================================

LTP_URL = (
    "https://api.dhan.co/v2/marketfeed/ltp"
)

OPTION_CHAIN_URL = (
    "https://api.dhan.co/v2/optionchain"
)

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

    current_time = datetime.now(IST).strftime(
        "%Y-%m-%d %H:%M:%S"
    )

    final_message = (
        f"{current_time} -> {message}"
    )

    print(final_message, flush=True)

    with open(
        "trade_logs.txt",
        "a"
    ) as file:

        file.write(
            final_message + "\n"
        )

# =========================================================
# GET BANKNIFTY LTP
# =========================================================

def get_banknifty_ltp():

    try:

        response = requests.post(

            LTP_URL,
            json=index_payload,
            headers=headers

        )

        data = response.json()

        if "data" not in data:
            return None

        if "IDX_I" not in data["data"]:
            return None

        return float(

            data["data"]["IDX_I"]["25"]["last_price"]

        )

    except Exception as e:

        write_log(
            f"LTP ERROR = {e}"
        )

        return None

# =========================================================
# GET ATM OPTIONS
# =========================================================

def get_atm_options(live_price):

    try:

        response = requests.post(

            OPTION_CHAIN_URL,
            json=option_payload,
            headers=headers

        )

        data = response.json()

        if "data" not in data:
            return None

        option_data = data["data"]

        if "oc" not in option_data:
            return None

        oc = option_data["oc"]

        atm_strike = round(
            live_price / 100
        ) * 100

        ce_strike = atm_strike
        pe_strike = atm_strike+100

        ce_strike_key = None
        pe_strike_key = None

        for strike in oc.keys():

            strike_int = int(float(strike))

            if strike_int == ce_strike:
                ce_strike_key = strike

            if strike_int == pe_strike:
                pe_strike_key = strike

        if ce_strike_key is None or pe_strike_key is None:
            return None

        ce_data = oc[ce_strike_key]["ce"]
        pe_data = oc[pe_strike_key]["pe"]

        return {

            "atm": atm_strike,

            "ce_security_id": ce_data.get(
                "security_id"
            ),

            "pe_security_id": pe_data.get(
                "security_id"
            ),

            "ce_ltp": float(
                ce_data.get(
                    "last_price",
                    0
                )
            ),

            "pe_ltp": float(
                pe_data.get(
                    "last_price",
                    0
                )
            )

        }

    except Exception as e:

        write_log(
            f"OPTION CHAIN ERROR = {e}"
        )

        return None


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

entry_security_id = None

day_pnl = 0

last_option_fetch_price = None

option_data = None

atm_ce_ltp = 0
atm_pe_ltp = 0



# =========================================================
# START
# =========================================================

write_log("")
write_log("====================================")
write_log("REAL AUTO TRADING BOT STARTED")
write_log("====================================")

while True:

    try:

        now = datetime.now(IST)

        print(now, flush=True)

        market_start = dt_time(9, 15)
        market_end = dt_time(15, 30)

        # ============================================
        # MARKET CLOSED
        # ============================================

        if now.time() < market_start or now.time() > market_end:

            next_open = IST.localize(
                datetime.combine(now.date(), market_start)
            )

            if now.time() > market_end:
                next_open += timedelta(days=1)

            remaining = next_open - now

            hours = remaining.seconds // 3600
            minutes = (remaining.seconds % 3600) // 60
            seconds = remaining.seconds % 60

            write_log(
                f"MARKET CLOSED | "
                f"ATM CE = {atm_ce_ltp} | "
                f"ATM PE = {atm_pe_ltp} | "
                f"WAITING FOR OPEN = "
                f"{hours}h {minutes}m {seconds}s"
            )

            current_second = datetime.now(IST).second
            sleep_time = 20 - (current_second % 20)

            time.sleep(sleep_time)

            continue

        # ============================================
        # LIVE BANKNIFTY
        # ============================================

        live_price = get_banknifty_ltp()

        print(f"LIVE BANKNIFTY = {live_price}", flush=True)

        if live_price is None:

            time.sleep(3)
            continue

        # ============================================
        # OPTION DATA
        # ============================================

        rounded_price = round(live_price)

        if (
            last_option_fetch_price is None or
            abs(rounded_price - last_option_fetch_price) >= 100
        ):

            new_data = get_atm_options(live_price)

            if new_data is not None:

                option_data = new_data
                last_option_fetch_price = rounded_price

        if option_data is not None:

            atm_strike = option_data["atm"]

            atm_ce_ltp = option_data["ce_ltp"]
            atm_pe_ltp = option_data["pe_ltp"]

            write_log(
                f"LIVE BNF = {live_price} | "
                f"ATM = {atm_strike} | "
                f"CE = {atm_ce_ltp} | "
                f"PE = {atm_pe_ltp}"
            )

        # ============================================
        # BUILD 5M CANDLE
        # ============================================

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

            candle_high = max(candle_high, live_price)
            candle_low = min(candle_low, live_price)
            candle_close = live_price

        # ============================================
        # CREATE 30M LEVELS
        # ============================================

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

                    highs = [x["high"] for x in prices_5m]
                    lows = [x["low"] for x in prices_5m]

                    level_high = max(highs)
                    level_low = min(lows)

                    write_log("30M LEVELS CREATED")
                    write_log(f"30M HIGH = {level_high}")
                    write_log(f"30M LOW = {level_low}")

                last_30m_time = current_30m

        # ============================================
        # ENTRY
        # ============================================

        if (
            trade_running == False and
            level_high is not None and
            level_low is not None and
            option_data is not None
        ):

            # =========================
            # BUY CE
            # =========================

            if live_price > level_high:

                write_log("BUY CE SIGNAL")

                order_payload = {

                    "transactionType": "BUY",
                    "exchangeSegment": "NSE_FNO",
                    "productType": "INTRADAY",
                    "orderType": "MARKET",
                    "validity": "DAY",
                    "securityId": option_data["ce_security_id"],
                    "quantity": REAL_QTY,
                    "price": 0

                }

                response = requests.post(
                    "https://api.dhan.co/v2/orders",
                    headers=headers,
                    json=order_payload,
                    timeout=10
                )

                try:
                    data = response.json()
                    write_log(f"BUY DATA = {data}")
                except:
                    pass

                write_log(f"BUY STATUS = {response.status_code}")
                write_log(f"BUY RESPONSE = {response.text}")

                if response.status_code in [200, 201]:

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

                    write_log(f"ENTRY PRICE = {entry_price}")

                else:

                    write_log("BUY FAILED")

            # =========================
            # BUY PE
            # =========================

            elif live_price < level_low:

                write_log("BUY PE SIGNAL")

                order_payload = {

                    "transactionType": "BUY",
                    "exchangeSegment": "NSE_FNO",
                    "productType": "INTRADAY",
                    "orderType": "MARKET",
                    "validity": "DAY",
                    "securityId": option_data["pe_security_id"],
                    "quantity": REAL_QTY,
                    "price": 0

                }

                response = requests.post(
                    "https://api.dhan.co/v2/orders",
                    headers=headers,
                    json=order_payload,
                    timeout=10
                )

                try:
                    data = response.json()
                    write_log(f"BUY DATA = {data}")
                except:
                    pass

                write_log(f"BUY STATUS = {response.status_code}")
                write_log(f"BUY RESPONSE = {response.text}")

                if response.status_code in [200, 201]:

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

                    write_log(f"ENTRY PRICE = {entry_price}")

                else:

                    write_log("BUY FAILED")

        # ============================================
        # ACTIVE TRADE
        # ============================================

        if trade_running:

            if trade_side == "CE":
                current_option_price = atm_ce_ltp
            else:
                current_option_price = atm_pe_ltp

            move = current_option_price - entry_price

            # =========================
            # TRAILING SL
            # =========================

            if move >= TRAIL_START:

                new_trail = (
                    current_option_price -
                    TRAIL_GAP
                )

                if new_trail > trail_sl:

                    trail_sl = new_trail

                    write_log(
                        f"TRAIL SL UPDATED = {trail_sl}"
                    )

            # =========================
            # FORCE EXIT
            # =========================

            force_exit = (
                now.hour == 15 and
                now.minute >= 15
            )

            # =========================
            # EXIT
            # =========================

            if (
                current_option_price <= trail_sl or
                current_option_price >= target_price or
                force_exit
            ):

                write_log("EXIT TRIGGERED")

                if trade_side == "CE":
                    exit_security_id = option_data["ce_security_id"]
                else:
                    exit_security_id = option_data["pe_security_id"]

                order_payload = {

                    "transactionType": "SELL",
                    "exchangeSegment": "NSE_FNO",
                    "productType": "INTRADAY",
                    "orderType": "MARKET",
                    "validity": "DAY",
                    "securityId": exit_security_id,
                    "quantity": REAL_QTY,
                    "price": 0

                }

                response = requests.post(
                    "https://api.dhan.co/v2/orders",
                    headers=headers,
                    json=order_payload,
                    timeout=10
                )

                try:
                    data = response.json()
                    write_log(f"SELL DATA = {data}")
                except:
                    pass

                write_log(f"SELL STATUS = {response.status_code}")
                write_log(f"SELL RESPONSE = {response.text}")

                if response.status_code in [200, 201]:

                    trade_running = False
                    trade_side = None
                    entry_price = None
                    target_price = None
                    trail_sl = None

        time.sleep(2)

    except Exception as e:

        write_log(f"MAIN LOOP ERROR = {e}")

        time.sleep(5)