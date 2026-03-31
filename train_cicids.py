import pandas as pd
import numpy as np
import joblib
from sklearn.ensemble import IsolationForest
import os

MODEL_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "anomaly_model.pkl")

def get_column(df, possible_names, default_val=0):
    """Safely extract a column handling whitespace and variations in CIC-IDS CSV names."""
    for name in possible_names:
        if name in df.columns:
            return df[name]
        for c in df.columns:
            if c.strip() == name:
                return df[c]
    return pd.Series([default_val]*len(df))

def train_on_cicids():
    url = "https://raw.githubusercontent.com/Western-OC2-Lab/Intrusion-Detection-System-Using-Machine-Learning/main/data/CICIDS2017_sample_km.csv"
    print(f"[*] Downloading and loading CIC-IDS2017 dataset from {url}...")
    try:
        df = pd.read_csv(url)
        print(f"[+] Loaded {len(df)} network flow records.")
    except Exception as e:
        print(f"[-] Failed to load dataset: {e}")
        return

    # Filter only BENIGN normal traffic to train our Isolation Forest's baseline
    label_col = None
    for c in df.columns:
        if "label" in c.lower():
            label_col = c
            break

    if label_col:
        benign_df = df[df[label_col].astype(str).str.contains("BENIGN", case=False, na=False)]
        if len(benign_df) > 0:
            df = benign_df
            print(f"[*] Filtered out attack traffic. Training strictly on {len(df)} BENIGN real-world samples.")
        else:
            print("[*] No BENIGN traffic found in sample. Training unconditionally.")

    print("[*] Automatically mapping CIC-IDS flow features to real-time packet inputs for NetWatch...")
    
    # Map features for: [packet_size, src_port, dst_port, protocol_num, packets_per_sec]
    packet_size = get_column(df, ["Average Packet Size", "Fwd Packet Length Mean", "Packet Length Mean"], 500)
    
    src_port = get_column(df, ["Source Port"], -1)
    if (src_port == -1).all():
        src_port = np.random.randint(1024, 65535, len(df))
        
    dst_port = get_column(df, ["Destination Port"], 80)
    protocol_num = get_column(df, ["Protocol"], 6)
    
    pps = get_column(df, ["Flow Packets/s"], 50)
    pps = pd.to_numeric(pps, errors='coerce').fillna(0)
    pps = pps.replace([np.inf, -np.inf], 10000)

    # Compile the final feature matrix
    features = np.column_stack([
        packet_size,
        src_port,
        dst_port,
        protocol_num,
        pps
    ])

    features = np.nan_to_num(features, nan=0.0)

    print(f"[*] Commencing intensive Isolation Forest ML training on {len(features)} rows...")
    model = IsolationForest(
        n_estimators=100,
        contamination=0.05,
        random_state=42,
        n_jobs=-1
    )
    model.fit(features)

    # Save to disk overwriting previous synthetic model
    joblib.dump(model, MODEL_PATH)
    print(f"[+] SUPERVISED TRAINING COMPLETE!")
    print(f"[+] Model weights physically serialized to: {MODEL_PATH}")
    print("[*] IMPORTANT: You must restart your FASTAPI server (`python main.py`) for the new weights to activate.")

if __name__ == "__main__":
    train_on_cicids()
