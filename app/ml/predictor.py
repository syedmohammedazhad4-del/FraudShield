"""
Prediction module: accepts human-readable form data, encodes, scales, predicts.
"""
import numpy as np
import joblib
from app.field_mappings import FEATURE_ORDER, LABEL_ENCODINGS, NUMERIC_FIELDS

_model = None
_scaler = None
_threshold = None


def _load_artifacts():
    global _model, _scaler, _threshold
    if _model is None:
        _model = joblib.load('models/model.pkl')
        _scaler = joblib.load('models/scaler.pkl')
        try:
            _threshold = joblib.load('models/threshold.pkl')
        except Exception:
            _threshold = 0.5


def encode_input(form_data: dict) -> list:
    """Convert human-readable form data to encoded numeric values."""
    encoded = []
    for field in FEATURE_ORDER:
        raw_value = form_data.get(field, '')

        if field in NUMERIC_FIELDS:
            encoded.append(float(raw_value))
        elif field in LABEL_ENCODINGS:
            mapping = LABEL_ENCODINGS[field]
            if raw_value in mapping:
                encoded.append(float(mapping[raw_value]))
            else:
                raise ValueError(f"Unknown value '{raw_value}' for field '{field}'")
        else:
            encoded.append(float(raw_value))

    return encoded


def predict(form_data: dict) -> dict:
    """Run prediction on human-readable form data.

    Returns dict with 'result', 'confidence', 'encoded_data', 'probabilities'.
    """
    _load_artifacts()

    encoded = encode_input(form_data)
    import pandas as pd
    from app.field_mappings import FEATURE_ORDER
    encoded_df = pd.DataFrame([encoded], columns=FEATURE_ORDER)
    scaled = _scaler.transform(encoded_df)

    probabilities = _model.predict_proba(scaled)[0]
    fraud_prob = float(probabilities[1])
    legit_prob = float(probabilities[0])

    if fraud_prob >= _threshold:
        result = 'Fraud'
        confidence = fraud_prob
    else:
        result = 'Legitimate'
        confidence = legit_prob

    return {
        'result': result,
        'confidence': round(confidence * 100, 1),
        'fraud_probability': round(fraud_prob * 100, 1),
        'legitimate_probability': round(legit_prob * 100, 1),
        'encoded_data': encoded
    }
