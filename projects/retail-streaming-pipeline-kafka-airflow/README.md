# Retail Streaming Pipeline

Runnable event-processing demo for retail inventory. A producer emits synthetic sales events; a consumer validates, deduplicates, aggregates, and writes curated inventory metrics to SQLite. Kafka is optional: local JSON Lines mode makes the project easy to evaluate without infrastructure.

## Local demo

```bash
python producer.py --count 100 --output data/events.jsonl
python consumer.py --input data/events.jsonl --database output/retail.db
python -m unittest discover
```

## Kafka mode

```bash
docker compose up -d
pip install -r requirements.txt
python producer.py --count 100 --kafka
python consumer.py --kafka --database output/retail.db
```

The same event contract is used in both modes, which keeps local testing aligned with streaming deployment.
## Architecture

```mermaid
flowchart LR
    P[Event Producer] --> K[Kafka or JSONL]
    K --> V[Validate and Deduplicate]
    V --> S[SQLite Curated Store]
    S --> M[Product Metrics View]
```

## Demo result

The automated test confirms schema validation, rejection handling, and idempotent deduplication. Local mode runs without Kafka; Docker mode exercises the same event contract through Kafka.
