"""
NetWatch - Machine Learning Anomaly Detection (Optional)
Lightweight Isolation Forest model for anomaly prediction on packet features.

This module can be used alongside the rule-based detector for additional
anomaly scoring. It trains on "normal" traffic patterns and flags outliers.
"""

import os
import numpy as np
import warnings
warnings.filterwarnings("ignore", category=UserWarning)

try:
    from sklearn.ensemble import IsolationForest
    import joblib
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "anomaly_model.pkl")

# Global model instance
_model: "IsolationForest | None" = None


def is_available() -> bool:
    """Check if ML dependencies are installed."""
    return ML_AVAILABLE


def generate_training_data(n_samples: int = 1000) -> np.ndarray:
    """
    Generate synthetic training data representing 'normal' network traffic.
    Features: [packet_size, src_port, dst_port, protocol_num, packets_per_sec]
    """
    rng = np.random.RandomState(42)

    data = np.column_stack([
        rng.normal(500, 200, n_samples).clip(64, 1500),    #packet_size
        rng.randint(1024, 65535, n_samples),                 # src_port
        rng.choice([80, 443, 8080, 53, 22, 3306], n_samples),  # dst_port (common)
        rng.choice([6, 17, 1], n_samples, p=[0.7, 0.2, 0.1]),  # protocol (TCP/UDP/ICMP)
        rng.normal(50, 20, n_samples).clip(1, 200),          # packets_per_sec
    ])

    return data


def train_model(data: np.ndarray = None) -> bool:
    """
    Train the Isolation Forest model.
    Returns True if training was successful.
    """
    global _model

    if not ML_AVAILABLE:
        print("[ML] scikit-learn not available. Skipping model training.")
        return False

    if data is None:
        data = generate_training_data()

    print(f"[ML] Training Isolation Forest on {len(data)} samples...")

    _model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
        n_jobs=-1,
    )
    _model.fit(data)

    # Save model to disk
    joblib.dump(_model, MODEL_PATH)
    print(f"[ML] Model saved to {MODEL_PATH}")

    return True


def load_model() -> bool:
    """Load a previously trained model from disk."""
    global _model

    if not ML_AVAILABLE:
        return False

    if os.path.exists(MODEL_PATH):
        _model = joblib.load(MODEL_PATH)
        print(f"[ML] Model loaded from {MODEL_PATH}")
        return True

    print("[ML] No saved model found. Training a new one...")
    return train_model()


def predict(packet_data: dict) -> dict:
    """
    Predict whether a packet is anomalous.

    Returns:
        dict with 'is_anomaly' (bool), 'score' (float), 'available' (bool)
    """
    if not ML_AVAILABLE or _model is None:
        return {"is_anomaly": False, "score": 0.0, "available": False}

    protocol_map = {"TCP": 6, "UDP": 17, "ICMP": 1}

    features = np.array([[
        packet_data.get("size", 500),
        packet_data.get("src_port", 0),
        packet_data.get("dst_port", 0),
        protocol_map.get(packet_data.get("protocol", "TCP"), 0),
        packet_data.get("packets_per_sec", 50),
    ]])

    prediction = _model.predict(features)[0]  # 1 = normal, -1 = anomaly
    score = _model.decision_function(features)[0]

    return {
        "is_anomaly": bool(prediction == -1),
        "score": round(float(score), 4),
        "available": True,
    }
