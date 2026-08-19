import pandas as pd

from pipeline import validate_claims


def test_valid_and_invalid_claims():
    frame = pd.DataFrame([
        {"claim_id": "C1", "member_id": "M1", "service_date": "2026-01-01", "received_date": "2026-01-02", "diagnosis_code": "E11.9", "allowed_amount": 10},
        {"claim_id": "C2", "member_id": "", "service_date": "2026-01-03", "received_date": "2026-01-02", "diagnosis_code": "BAD", "allowed_amount": -1},
    ])
    result = validate_claims(frame)
    assert result["is_valid"].tolist() == [True, False]
    assert "missing_member_id" in result.loc[1, "validation_errors"]

