from model import generate_synthetic_data, train_model


def test_training_pipeline():
    data = generate_synthetic_data(rows=500)
    bundle = train_model(data)
    assert 0.5 <= bundle.auc <= 1.0
    assert len(bundle.probabilities) == len(bundle.y_test)
    assert bundle.probabilities.min() >= 0
    assert bundle.probabilities.max() <= 1
