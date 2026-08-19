import argparse
import json
import re
from pathlib import Path

import pandas as pd


DX_PATTERN = re.compile(r"^[A-Z][0-9]{2}(\.[A-Z0-9]{1,4})?$")


def validate_claims(frame: pd.DataFrame) -> pd.DataFrame:
    df = frame.copy()
    df["service_date"] = pd.to_datetime(df["service_date"], errors="coerce")
    df["received_date"] = pd.to_datetime(df["received_date"], errors="coerce")
    reasons = pd.Series("", index=df.index, dtype="object")

    def add_reason(mask: pd.Series, reason: str) -> None:
        nonlocal reasons
        reasons.loc[mask] = reasons.loc[mask].apply(lambda value: f"{value}|{reason}".strip("|"))

    add_reason(df["claim_id"].isna() | df["claim_id"].astype(str).str.strip().eq(""), "missing_claim_id")
    add_reason(df["member_id"].isna() | df["member_id"].astype(str).str.strip().eq(""), "missing_member_id")
    add_reason(pd.to_numeric(df["allowed_amount"], errors="coerce").lt(0), "negative_allowed_amount")
    add_reason(~df["diagnosis_code"].fillna("").astype(str).str.match(DX_PATTERN), "invalid_diagnosis_code")
    add_reason(df["service_date"].gt(df["received_date"]), "service_after_received")
    add_reason(df.duplicated("claim_id", keep=False), "duplicate_claim_id")
    df["validation_errors"] = reasons
    df["is_valid"] = reasons.eq("")
    return df


def run(input_path: Path, output_dir: Path) -> dict:
    output_dir.mkdir(parents=True, exist_ok=True)
    validated = validate_claims(pd.read_csv(input_path))
    validated[validated["is_valid"]].to_csv(output_dir / "clean_claims.csv", index=False)
    validated[~validated["is_valid"]].to_csv(output_dir / "quarantined_claims.csv", index=False)
    failures = (
        validated.loc[~validated["is_valid"], "validation_errors"]
        .str.split("|").explode().value_counts().to_dict()
    )
    report = {
        "total_rows": int(len(validated)),
        "valid_rows": int(validated["is_valid"].sum()),
        "invalid_rows": int((~validated["is_valid"]).sum()),
        "rule_failures": failures,
    }
    (output_dir / "quality_report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("output"))
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.output), indent=2))

