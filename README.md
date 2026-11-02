# Loki Lab: Logging with Loki, Alloy and Grafana

A hands-on lab that collects Nginx and application logs, parses and redacts them, stores them in Loki and queries them in Grafana.

## Flow

App / Nginx -> log files -> Alloy -> Loki -> Grafana

- **App and Nginx** write JSON logs to files.
- **Alloy** reads the files, parses, adds labels, redacts secrets and sends logs to Loki.
- **Loki** stores the logs and indexes only the labels.
- **Grafana** queries Loki with LogQL.

## Project structure

```
loki-lab/
├── docker-compose.yaml
├── loki/loki-config.yaml
├── alloy/config.alloy
├── nginx/nginx.conf
├── app/app.py
└── processor/processor.py
```

## Run it

```
docker compose up -d
```

- Grafana: http://localhost:3000 (add Loki data source with URL `http://loki:3100`)
- Nginx: http://localhost:8080
- Alloy UI: http://localhost:12345

## Concepts learned

- **Structured logs** (JSON) are easy to parse; unstructured text needs regex.
- **Labels** identify a stream. Keep them few and low cardinality (job, service, status, level). Never use ip, user_id or path as labels.
- **Chunks and index**: Loki stores log lines in compressed chunks and indexes only the labels.
- **Pipeline order**: collect, parse, enrich, redact, send.

## Hands-on tasks

1. **Deploy Loki and connect to Grafana**: Docker Compose with Loki and Grafana, Loki added as a data source.
2. **Collect Nginx and app logs**: both write JSON logs to files; Alloy reads them with `local.file_match` and `loki.source.file`.
3. **Parse JSON logs**: `stage.json` extracts status, latency_ms, path and level; `stage.labels` makes status and level labels.
4. **LogQL queries**:
   - 5xx: `{job="app", status=~"5.."}`
   - 4xx and 5xx: `{job="app", status=~"4..|5.."}`
   - Slow requests: `{job="app"} | json | latency_ms > 1000`
   - Errors per minute: `sum(count_over_time({job="app", status=~"5.."}[1m]))`
5. **Log-processing script**: Python script that skips duplicate lines (hash of the line) and retries with exponential backoff (2, 4, 8, 16, 32 s).
6. **Redaction**: `stage.replace` masks token and email values and the last IP octet before ingestion.
7. **Loki downtime**: stopped Loki, Alloy logged `error sending batch, will retry`, logs waited in the file and arrived after Loki came back.

## Lessons and gotchas

- In `stage.replace`, only the text inside the brackets `( )` is replaced. Using `${1}` in `replace` prints it literally.
- Redaction only affects new logs. Logs already stored in Loki are never changed, so redact before ingestion.
- Nginx `$request_time` is in seconds, the app's `latency_ms` is in milliseconds.
- The `processor` script sends raw lines, so its logs are not redacted.
- Container name conflicts (`grafana` already in use) are fixed with `docker rm -f`.
- Log files created by containers are owned by root, so use `sudo tee -a` to append to them.
