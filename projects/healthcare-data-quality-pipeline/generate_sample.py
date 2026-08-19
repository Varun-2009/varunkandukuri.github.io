import argparse
import random
from datetime import date, timedelta
from pathlib import Path

import pandas as pd


def generate(count: int) -> pd.DataFrame:
    random.seed(42)
    rows = []
    for index in range(count):
        service = date(2026, 1, 1) + timedelta(days=random.randint(0, 180))
        rows.append({
            "claim_id": f"SYN-{index:06d}",
            "member_id": f"DEMO-{random.randint(1, max(2, count // 3)):05d}",
            "service_date": service.isoformat(),
            "received_date": (service + timedelta(days=random.randint(0, 7))).isoformat(),
            "diagnosis_code": random.choice(["E11.9", "I10", "J45.2", "E78.5"]),
            "allowed_amount": round(random.uniform(25, 1500), 2),
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--count", type=int, default=100)
    parser.add_argument("--output", type=Path, default=Path("data/sample_claims.csv"))
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    generate(args.count).to_csv(args.output, index=False)
    print(f"generated={args.count} output={args.output}")
