import os
import time

print("STARTED", flush=True)

from Dhan_Tradehull import Tradehull

print("TRADEHULL IMPORTED", flush=True)

# =========================================
# ENV
# =========================================

client_id = os.getenv("DHAN_CLIENT_ID")
access_token = os.getenv("DHAN_ACCESS_TOKEN")

print("CLIENT ID :", client_id, flush=True)
print("TOKEN FOUND :", bool(access_token), flush=True)

# =========================================
# LOGIN
# =========================================

print("CONNECTING...", flush=True)

tsl = Tradehull(
    client_id,
    access_token,
    mode="access_token"
)

print("CONNECTED", flush=True)

# =========================================
# LOOP
# =========================================

while True:

    try:

        print("FETCHING...", flush=True)

        live_data = tsl.get_ltp_data("BANKNIFTY")

        print("DATA :", live_data, flush=True)

    except Exception as e:

        print("ERROR :", e, flush=True)

    time.sleep(5)