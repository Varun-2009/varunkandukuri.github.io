import argparse
import json
import random
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path


PRODUCTS = ["milk-a2", "buffalo-milk", "curd", "ghee"]


def make_event() -> dict:
    return {
        "event_id": str(uuid.uuid4()),
        "event_time": datetime.now(timezone.utc).isoformat(),
        "store_id": f"S{random.randint(1, 5):03d}",
        "product_id": random.choice(PRODUCTS),
        "quantity": random.randint(1, 8),
        "unit_price": round(random.uniform(2.5, 18.0), 2),
    }


def main(args):
    events = [make_event() for _ in range(args.count)]
    if args.kafka:
        from kafka import KafkaProducer
        producer = KafkaProducer(bootstrap_servers=args.bootstrap, value_serializer=lambda value: json.dumps(value).encode())
        for event in events:
            producer.send("retail-sales", event)
        producer.flush()
    else:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text("\n".join(json.dumps(event) for event in events) + "\n", encoding="utf-8")
    print(f"produced={len(events)}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("data/events.jsonl"))
    parser.add_argument("--kafka", action="store_true")
    parser.add_argument("--bootstrap", default="localhost:9092")
    main(parser.parse_args())

