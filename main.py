"""
NetWatch - Main FastAPI Backend Application
Central API server that receives packet data, runs detection, and serves data to the frontend.
"""

import sys
import os
import time
import threading
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional

# Ensure the backend directory is in Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from detector import analyze_packet
from ftp_monitor import analyze_ftp_event
from utils.geo import get_geo
from utils.blocker import block_ip_windows
from ai_chat import generate_chat_response

from database import (
    init_db, insert_packet, insert_ftp_event,
    get_recent_packets, get_recent_alerts, get_ftp_activity,
    get_total_packets_count, get_active_ips_count, get_ftp_stats,
    get_top_ips, get_protocol_distribution, get_traffic_timeline
)

# Try to load ML model
try:
    from model import load_model, predict, is_available as ml_available
    if ml_available():
        load_model()
        print("[*] ML anomaly detection model loaded.")
    else:
        print("[*] ML dependencies not available. Running without ML.")
except Exception as e:
    print(f"[*] ML model not loaded: {e}")
    ml_available = lambda: False
    predict = lambda x: {"is_anomaly": False, "score": 0.0, "available": False}

# ---------------------------------------------------------------------------
# FastAPI App
# ---------------------------------------------------------------------------
app = FastAPI(
    title="NetWatch API",
    description="Real-Time Network Monitoring, Intrusion Detection & FTP Activity Analysis",
    version="1.0.0",
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Pydantic Models
# ---------------------------------------------------------------------------
class PacketData(BaseModel):
    src_ip: str
    dst_ip: str
    protocol: str = "TCP"
    size: int = 0
    timestamp: Optional[str] = None
    src_port: int = 0
    dst_port: int = 0


class FTPEvent(BaseModel):
    event: str       # connect, disconnect, login, upload, download
    ip: str
    username: Optional[str] = None
    status: Optional[str] = None
    filename: Optional[str] = None
    file_size: Optional[int] = 0
    timestamp: Optional[str] = None


class ChatRequest(BaseModel):
    query: str



# ---------------------------------------------------------------------------
# API Endpoints
# ---------------------------------------------------------------------------

@app.post("/packet")
async def receive_packet(packet: PacketData):
    """Receive a packet from the sniffer and run detection."""
    
    # Use model_dump for Pydantic V2 compatibility
    try:
        pkt = packet.model_dump()
    except Exception:
        pkt = packet.dict()
        
    if not pkt.get("timestamp"):
        pkt["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Store packet into SQLite DB
    insert_packet(pkt)

    # Run detection
    new_alerts = analyze_packet(pkt)
    
    # [NEW] Active IP Blocking for High/Medium Severity
    if new_alerts:
        for alert in new_alerts:
            if alert.get("severity") in ["high", "medium"]:
                ip_to_block = alert.get("source_ip")
                if ip_to_block and ip_to_block not in ["N/A", "unknown", "Local Browser"]:
                    alert["blocked"] = True
                    threading.Thread(target=block_ip_windows, args=(ip_to_block,), daemon=True).start()

    # Run ML prediction if available
    ml_result = predict(pkt)

    # Check if this is FTP traffic (port 2121)
    if pkt.get("dst_port") == 2121 or pkt.get("src_port") == 2121:
        ftp_event = {
            "event": "ftp_traffic",
            "ip": pkt["src_ip"],
            "timestamp": pkt["timestamp"],
        }
        analyze_ftp_event(ftp_event)

    return {
        "status": "received",
        "alerts_generated": len(new_alerts),
        "ml_anomaly": ml_result.get("is_anomaly", False),
    }


@app.post("/ftp-event")
async def receive_ftp_event(event: FTPEvent):
    """Receive an FTP event for monitoring and detection."""
    evt = event.dict()
    if not evt.get("timestamp"):
        evt["timestamp"] = datetime.now(timezone.utc).isoformat()

    # Store FTP event into SQLite DB
    insert_ftp_event(evt)

    # Run FTP-specific detection
    new_alerts = analyze_ftp_event(evt)

    # [NEW] Active IP Blocking for High/Medium Severity
    if new_alerts:
        for alert in new_alerts:
            if alert.get("severity") in ["high", "medium"]:
                ip_to_block = alert.get("source_ip")
                if ip_to_block and ip_to_block not in ["N/A", "unknown", "Local Browser"]:
                    alert["blocked"] = True
                    threading.Thread(target=block_ip_windows, args=(ip_to_block,), daemon=True).start()

    return {
        "status": "received",
        "ftp_alerts_generated": len(new_alerts),
    }


@app.get("/packets")
async def get_packets(limit: int = 50):
    """Return recent packets with geolocation injected."""
    data = get_recent_packets(limit)
        
    for pkt in data:
        pkt["src_geo"] = get_geo(pkt.get("src_ip"))
        
    return {"packets": data, "total": get_total_packets_count()}


@app.get("/alerts")
async def get_all_alerts(limit: int = 50):
    """Return all alerts (network + FTP combined)."""
    # SQLite 'alerts' table contains both categories, natively sorted by timestamp
    data = get_recent_alerts(limit)
    return {"alerts": data, "total": len(data)}


@app.get("/ftp-activity")
async def get_ftp_activity_endpoint(limit: int = 50):
    """Return FTP activity logs."""
    activity = get_ftp_activity(limit)
    stats = get_ftp_stats()

    return {
        "activity": activity,
        "stats": stats,
        "total": len(activity),
    }


@app.get("/stats")
async def get_stats():
    """Return dashboard summary statistics."""
    ftp_stats = get_ftp_stats()
    # A lightweight query for recent alerts can be used or 
    # we can explicitly query COUNT for alerts. To keep it simple:
    alerts_count = len(get_recent_alerts(1000))

    return {
        "total_packets": get_total_packets_count(),
        "alerts_count": alerts_count,
        "active_ips": get_active_ips_count(),

        # counters for dashboard
        "uploads": ftp_stats.get("uploads", 0),
        "downloads": ftp_stats.get("downloads", 0),
        "logins": ftp_stats.get("logins", 0),

        "ftp_activity_count": len(get_ftp_activity(1000)),
        "ml_available": ml_available(),
    }


@app.get("/traffic-data")
async def get_traffic_data(limit: int = 60):
    """Return time-series traffic data for charts."""
    data = get_traffic_timeline(limit)
    return {"traffic": data}


@app.get("/top-ips")
async def get_top_ips_endpoint(limit: int = 10):
    """Return top source IPs by packet count along with geolocation."""
    data = get_top_ips(limit)

    for item in data:
        item["geo"] = get_geo(item["ip"])

    return {"top_ips": data}


@app.get("/protocols")
async def get_protocols_endpoint():
    """Return protocol distribution."""
    data = get_protocol_distribution()
    return {"protocols": data}


@app.post("/chat")
async def chat_endpoint(request: ChatRequest):
    """Answers user queries using Gemini AI context."""
    # Get recent context
    recent_alerts = get_recent_alerts(20)
    recent_packets = get_recent_packets(20)
    
    # Generate response
    ai_response = generate_chat_response(request.query, recent_packets, recent_alerts)
    return {"response": ai_response}


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat()}


# ---------------------------------------------------------------------------
# Startup
# ---------------------------------------------------------------------------
@app.on_event("startup")
async def startup_event():
    # Initialize the SQLite Database
    init_db()
    
    print("=" * 60)
    print("  NetWatch API Server")
    print("=" * 60)
    print("  Endpoints:")
    print("    POST /packet       - Receive packet data")
    print("    POST /ftp-event    - Receive FTP event")
    print("    GET  /packets      - Get recent packets")
    print("    GET  /alerts       - Get alerts")
    print("    GET  /ftp-activity - Get FTP activity")
    print("    GET  /stats        - Get dashboard stats")
    print("    GET  /traffic-data - Get traffic timeline")
    print("    GET  /top-ips      - Get top source IPs")
    print("    GET  /protocols    - Get protocol distribution")
    print("=" * 60)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
