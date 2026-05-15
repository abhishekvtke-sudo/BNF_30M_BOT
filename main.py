import os
import time

from dhanhq import dhanhq, DhanContext

print("START", flush=True)

client_id = os.environ["DHAN_CLIENT_ID"]
access_token = os.environ["DHAN_ACCESS_TOKEN"]

print("ENV LOADED", flush=True)

context = DhanContext(
    client_id,
    access_token
)

print("CONTEXT CREATED", flush=True)

dhan = dhanhq(context)

print("DHAN OBJECT CREATED", flush=True)

response = dhan.ltp_data({
    "NSE_IDX": [25]
})

print(response, flush=True)

while True:
    print("LOOP OK", flush=True)
    time.sleep(1)