"""
NetWatch - FTP Activity Monitor
Analyzes FTP traffic and activity logs to detect suspicious patterns.
"""

import time
from collections import defaultdict
from utils.helpers import get_timestamp, format_bytes

from database import insert_alert, get_ftp_alerts as db_get_ftp_alerts, get_ftp_stats as db_get_ftp_stats

# ---------------------------------------------------------------------------
# In-memory state for FTP monitoring (sliding windows)
# ---------------------------------------------------------------------------
upload_tracker: dict[str, list[float]] = defaultdict(list)
failed_login_tracker: dict[str, list[float]] = defaultdict(list)

MAX_UPLOADS_PER_IP = 10          
UPLOAD_TIME_WINDOW = 60          
LARGE_FILE_THRESHOLD = 50 * 1024 * 1024  
MAX_FAILED_LOGINS = 5            
FAILED_LOGIN_WINDOW = 60         


def _cleanup(entries: list[float], window: float) -> list[float]:
    cutoff = time.time() - window
    return [t for t in entries if t >= cutoff]


def analyze_ftp_event(event: dict) -> list[dict]:
    """
    Analyze an FTP event for suspicious activity.
    Returns a list of new alerts.
    """
    new_alerts = []
    event_type = event.get("event", "")
    ip = event.get("ip", "unknown")
    now = time.time()

    # --- Rule 1: Too many uploads from single IP ---
    if event_type == "upload":
        upload_tracker[ip].append(now)
        upload_tracker[ip] = _cleanup(upload_tracker[ip], UPLOAD_TIME_WINDOW)

        if len(upload_tracker[ip]) > MAX_UPLOADS_PER_IP:
            alert = {
                "type": "Suspicious FTP Upload",
                "severity": "medium",
                "source_ip": ip,
                "message": f"IP {ip} uploaded {len(upload_tracker[ip])} files in {UPLOAD_TIME_WINDOW}s",
                "timestamp": get_timestamp(),
                "category": "ftp",
            }
            alert["id"] = insert_alert(alert, category="ftp")
            new_alerts.append(alert)

    # --- Rule 2: Large file transfer ---
    if event_type in ("upload", "download"):
        file_size = event.get("file_size", 0)
        if file_size > LARGE_FILE_THRESHOLD:
            alert = {
                "type": "Large File Transfer",
                "severity": "medium",
                "source_ip": ip,
                "message": f"Large file {event.get('filename', 'unknown')} ({format_bytes(file_size)}) transferred by {ip}",
                "timestamp": get_timestamp(),
                "category": "ftp",
            }
            alert["id"] = insert_alert(alert, category="ftp")
            new_alerts.append(alert)

    # --- Rule 3: Multiple failed logins ---
    if event_type == "login" and event.get("status") == "failed":
        failed_login_tracker[ip].append(now)
        failed_login_tracker[ip] = _cleanup(
            failed_login_tracker[ip], FAILED_LOGIN_WINDOW
        )

        if len(failed_login_tracker[ip]) >= MAX_FAILED_LOGINS:
            alert = {
                "type": "FTP Brute Force",
                "severity": "high",
                "source_ip": ip,
                "message": f"IP {ip} had {len(failed_login_tracker[ip])} failed login attempts in {FAILED_LOGIN_WINDOW}s",
                "timestamp": get_timestamp(),
                "category": "ftp",
            }
            alert["id"] = insert_alert(alert, category="ftp")
            new_alerts.append(alert)

    return new_alerts


def get_ftp_alerts(limit: int = 100) -> list[dict]:
    """Return recent FTP-specific alerts from the database."""
    return db_get_ftp_alerts(limit)


def get_ftp_stats() -> dict:
    """Return summary statistics for FTP monitoring from the database."""
    return db_get_ftp_stats()
