import argparse
import json
import sqlite3
from pathlib import Path


REQUIRED = {"event_id", "event_time", "store_id", "product_id", "quantity", "unit_price"}


def valid(event: dict) -> bool:
    return REQUIRED.issubset(event) and event["quantity"] > 0 and event["unit_price"] >= 0


def persist(events, database: Path) -> tuple[int, int]:
    database.parent.mkdir(parents=True, exist_ok=True)
    accepted = rejected = 0
    with sqlite3.connect(database) as conn:
        conn.execute("CREATE TABLE IF NOT EXISTS sales (event_id TEXT PRIMARY KEY, event_time TEXT, store_id TEXT, product_id TEXT, quantity INTEGER, unit_price REAL)")
        for event in events:
            if not valid(event):
                rejected += 1
                continue
            cursor = conn.execute("INSERT OR IGNORE INTO sales VALUES (?, ?, ?, ?, ?, ?)", tuple(event[key] for key in ["event_id", "event_time", "store_id", "product_id", "quantity", "unit_price"]))
            accepted += cursor.rowcount
        conn.execute("CREATE VIEW IF NOT EXISTS product_metrics AS SELECT product_id, SUM(quantity) units_sold, ROUND(SUM(quantity * unit_price), 2) revenue FROM sales GROUP BY product_id")
    return accepted, rejected


def file_events(path: Path):
    for line in path.read_text(encoding="utf-8").splitlines():
        yield json.loads(line)


def kafka_events(bootstrap: str):
    from kafka import KafkaConsumer
    consumer = KafkaConsumer("retail-sales", bootstrap_servers=bootstrap, auto_offset_reset="earliest", value_deserializer=lambda value: json.loads(value.decode()))
    for message in consumer:
        yield message.value


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=Path("data/events.jsonl"))
    parser.add_argument("--database", type=Path, default=Path("output/retail.db"))
    parser.add_argument("--kafka", action="store_true")
    parser.add_argument("--bootstrap", default="localhost:9092")
    args = parser.parse_args()
    stream = kafka_events(args.bootstrap) if args.kafka else file_events(args.input)
    accepted, rejected = persist(stream, args.database)
    print(f"accepted={accepted} rejected={rejected}")

