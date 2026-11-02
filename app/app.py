import json
import random
import time
from datetime import datetime, timezone

LOG_FILE = "/var/log/app/app.log"

PATHS = ["/home", "/login", "/products", "/orders", "/checkout"]
STATUSES = [200, 200, 200, 200, 201, 404, 500]

while True:
    status = random.choice(STATUSES)
    latency_ms = random.randint(20, 2500)
    path = random.choice(PATHS)

    if path == "/login":
        path = "/login?token=abc123&email=test@example.com"

    log = {
        "time": datetime.now(timezone.utc).isoformat(),
        "level": "error" if status >= 500 else "info",
        "service": "shop-api",
        "ip": "203.0.113." + str(random.randint(1, 254)),
        "method": "GET",
        "path": path,
        "status": status,
        "latency_ms": latency_ms,
    }

    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(log) + "\n")

    time.sleep(1)
