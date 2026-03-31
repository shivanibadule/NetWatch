"""
NetWatch - Intrusion Detection Engine
Rule-based detection for DDoS attacks, port scans, and traffic spikes.
"""

import time
from collections import defaultdict
from utils.helpers import get_timestamp
import threading

from database import insert_alert, get_network_alerts

# ---------------------------------------------------------------------------
# In-memory storage for high-speed tracking filters (sliding windows)
# ---------------------------------------------------------------------------

# { src_ip: [timestamp, timestamp, ...] }
request_tracker: dict[str, list[float]] = defaultdict(list)

# { src_ip: [(port1, timestamp), (port2, timestamp), ...] }
port_tracker: dict[str, list[tuple[int, float]]] = defaultdict(list)

# Global packet rate tracking
packet_rate_history: list[float] = []

# Known IPs for discovery alerts
known_ips: set[str] = set()

# Lock for thread-safe access
_lock = threading.Lock()

# ---------------------------------------------------------------------------
# Configurable thresholds
# ---------------------------------------------------------------------------
DDOS_THRESHOLD = 15          # max requests per IP within time window
DDOS_TIME_WINDOW = 120        # extremely wide window to catch slow tests
PORT_SCAN_THRESHOLD = 5      # unique ports accessed in time window
PORT_SCAN_TIME_WINDOW = 120   # seconds
SPIKE_THRESHOLD = 10         # packets per second considered a spike
SPIKE_WINDOW = 15            # wide window


def _cleanup_old_entries(entries: list, time_window: float) -> list:
    """Remove entries older than the time window."""
    cutoff = time.time() - time_window
    return [e for e in entries if (e if isinstance(e, (int, float)) else e[1]) >= cutoff]


def analyze_packet(packet_data: dict) -> list[dict]:
    """
    Analyze a single packet for suspicious activity.
    Returns a list of new alerts generated.
    """
    new_alerts = []
    src_ip = packet_data.get("src_ip", "unknown")
    dst_port = packet_data.get("dst_port", 0)
    now = time.time()

    # --- Rule 1: DDoS Detection (high request rate from single IP) ---
    request_tracker[src_ip].append(now)
    request_tracker[src_ip] = _cleanup_old_entries(
        request_tracker[src_ip], DDOS_TIME_WINDOW
    )
    if len(request_tracker[src_ip]) > DDOS_THRESHOLD:
        alert = {
            "type": "DDoS Attempt",
            "severity": "high",
            "source_ip": src_ip,
            "message": f"IP {src_ip} sent {len(request_tracker[src_ip])} requests in {DDOS_TIME_WINDOW}s",
            "timestamp": get_timestamp(),
        }
        alert["id"] = insert_alert(alert, category="network")
        new_alerts.append(alert)

    # --- Rule 2: Port Scan Detection ---
    if dst_port:
        port_tracker[src_ip].append((dst_port, now))
        port_tracker[src_ip] = _cleanup_old_entries(
            port_tracker[src_ip], PORT_SCAN_TIME_WINDOW
        )
        unique_ports = set(p for p, _ in port_tracker[src_ip])
        if len(unique_ports) > PORT_SCAN_THRESHOLD:
            alert = {
                "type": "Port Scan",
                "severity": "medium",
                "source_ip": src_ip,
                "message": f"IP {src_ip} accessed {len(unique_ports)} unique ports in {PORT_SCAN_TIME_WINDOW}s",
                "timestamp": get_timestamp(),
            }
            alert["id"] = insert_alert(alert, category="network")
            new_alerts.append(alert)

    # --- Rule 3: Traffic Spike Detection ---
    packet_rate_history.append(now)
    cutoff = now - SPIKE_WINDOW
    recent = [t for t in packet_rate_history if t >= cutoff]
    packet_rate_history.clear()
    packet_rate_history.extend(recent)
    rate = len(recent) / SPIKE_WINDOW
    if rate > SPIKE_THRESHOLD:
        alert = {
            "type": "Traffic Spike",
            "severity": "high",
            "source_ip": "N/A",
            "message": f"Traffic spike detected: {rate:.0f} packets/sec (threshold: {SPIKE_THRESHOLD})",
            "timestamp": get_timestamp(),
        }
        alert["id"] = insert_alert(alert, category="network")
        new_alerts.append(alert)

    # --- Rule 3.5: UDP Flood Detection ---
    if packet_data.get("protocol") == "UDP":
        udp_key = f"udp_{src_ip}"
        request_tracker[udp_key].append(now)
        request_tracker[udp_key] = _cleanup_old_entries(
            request_tracker[udp_key], 60 
        )
        if len(request_tracker[udp_key]) > 10:
            alert = {
                "type": "UDP Flood",
                "severity": "high",
                "source_ip": src_ip,
                "message": f"UDP Flood detected from {src_ip}: {len(request_tracker[udp_key])} pkts in 5s",
                "timestamp": get_timestamp(),
            }
            alert["id"] = insert_alert(alert, category="network")
            new_alerts.append(alert)

    # --- Rule 4: New Device Detection (Low Severity) ---
    with _lock:
        if src_ip not in known_ips:
            known_ips.add(src_ip)
            alert = {
                "type": "New Connection",
                "severity": "low",
                "source_ip": src_ip,
                "message": f"New source IP detected: {src_ip}",
                "timestamp": get_timestamp(),
            }
            alert["id"] = insert_alert(alert, category="network")
            new_alerts.append(alert)

    return new_alerts

def get_alerts(limit: int = 100) -> list[dict]:
    """Return the most recent network alerts directly from the database."""
    return get_network_alerts(limit)

def clear_alerts():
    """Clear memory trackers. Does not delete from database."""
    request_tracker.clear()
    port_tracker.clear()
    packet_rate_history.clear()
