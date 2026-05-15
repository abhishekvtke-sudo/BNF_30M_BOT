import os
from dhanhq import dhanhq, marketfeed

# =========================================
# LOAD ENV VARIABLES
# =========================================

client_id = os.environ["DHAN_CLIENT_ID"]
access_token = os.environ["DHAN_ACCESS_TOKEN"]

print("CLIENT ID LOADED", flush=True)
print("TOKEN LOADED", flush=True)

# =========================================
# CONNECT TO DHAN
# =========================================

dhan = dhanhq(access_token)

print("CONNECTED TO DHAN", flush=True)

# =========================================
# INSTRUMENTS
# =========================================

instruments = [
    (marketfeed.IDX_I, "25", 17)
]

# =========================================
# CALLBACKS
# =========================================

def on_connect(instance):
    print("CONNECTED TO DHAN LIVE FEED", flush=True)

def on_message(instance, message):
    print("BANKNIFTY DATA :", flush=True)
    print(message, flush=True)

# =========================================
# START LIVE FEED
# =========================================

feed = marketfeed.DhanFeed(
    client_id,
    access_token,
    instruments,
    on_connect=on_connect,
    on_message=on_message
)

print("STARTED", flush=True)

feed.run_forever()