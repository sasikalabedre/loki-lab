import json
import time
import hashlib
import urllib.request

LOG_FILE = "/var/log/app/app.log"
LOKI_URL = "http://loki:3100/loki/api/v1/push"
MAX_RETRIES = 5

seen = set()


def send_to_loki(line):
    payload = {
        "streams": [
            {
                "stream": {"job": "processor", "service": "shop-api"},
                "values": [[str(time.time_ns()), line]],
            }
        ]
    }
    data = json.dumps(payload).encode()

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            req = urllib.request.Request(
                LOKI_URL, data=data, headers={"Content-Type": "application/json"}
            )
            urllib.request.urlopen(req, timeout=5)
            return True
        except Exception as e:
            wait = 2 ** attempt
            print(f"attempt {attempt} failed: {e}. retrying in {wait}s", flush=True)
            time.sleep(wait)

    print("giving up on this line", flush=True)
    return False


with open(LOG_FILE) as f:
    while True:
        line = f.readline()
        if not line:
            time.sleep(1)
            continue

        line = line.strip()
        key = hashlib.md5(line.encode()).hexdigest()

        if key in seen:
            print("duplicate, skipped", flush=True)
            continue

        seen.add(key)
        send_to_loki(line)
