import os
from dhanhq import marketfeed

client_id = os.environ["DHAN_CLIENT_ID"]
access_token = os.environ["DHAN_ACCESS_TOKEN"]

print("CLIENT ID LOADED", flush=True)
print("TOKEN LOADED", flush=True)

# BANKNIFTY INDEX
instruments = [
    ("IDX_I", "25", 15)
]

def on_connect(instance):
    print("CONNECTED TO DHAN LIVE FEED", flush=True)

def on_message(instance, message):
    print("BANKNIFTY DATA :", flush=True)
    print(message, flush=True)

feed = marketfeed.DhanFeed(
    client_id,
    access_token,
    instruments,
    on_connect=on_connect,
    on_message=on_message
)

print("STARTED", flush=True)

feed.run_forever()