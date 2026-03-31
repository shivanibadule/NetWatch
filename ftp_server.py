"""
NetWatch - Custom FTP Server
Runs an FTP server on port 2121 with user authentication and activity POSTing to the central API.
"""

import os
import sys
import time
import threading
from datetime import datetime, timezone

try:
    from pyftpdlib.authorizers import DummyAuthorizer
    from pyftpdlib.handlers import FTPHandler
    from pyftpdlib.servers import FTPServer
except ImportError:
    print("ERROR: pyftpdlib is not installed. Run: pip install pyftpdlib")
    sys.exit(1)

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
FTP_HOST = "0.0.0.0"
FTP_PORT = 2121
API_URL = "http://localhost:8000"
FTP_ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ftp_root")

def _notify_api(entry: dict):
    """Notify backend API of FTP events. The API will store it in the SQLite DB."""
    try:
        requests.post(f"{API_URL}/ftp-event", json=entry, timeout=1)
    except requests.exceptions.RequestException:
        pass # Backend might be down, skipping log

# ---------------------------------------------------------------------------
# Custom FTP Handler with logging
# ---------------------------------------------------------------------------

class NetWatchFTPHandler(FTPHandler):
    """FTP handler that sends all significant events to the central NetWatch API."""

    def on_connect(self):
        log_entry = {
            "event": "connect",
            "ip": self.remote_ip,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        _notify_api(log_entry)
        print(f"[FTP] Connection from {self.remote_ip}")

    def on_disconnect(self):
        log_entry = {
            "event": "disconnect",
            "ip": self.remote_ip,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        _notify_api(log_entry)

    def on_login(self, username):
        log_entry = {
            "event": "login",
            "ip": self.remote_ip,
            "username": username,
            "status": "success",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        _notify_api(log_entry)
        print(f"[FTP] Login: {username} from {self.remote_ip}")

    def on_login_failed(self, username, password):
        log_entry = {
            "event": "login",
            "ip": self.remote_ip,
            "username": username,
            "status": "failed",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        _notify_api(log_entry)
        print(f"[FTP] Login FAILED: {username} from {self.remote_ip}")

    def on_file_received(self, file):
        file_size = os.path.getsize(file) if os.path.exists(file) else 0
        log_entry = {
            "event": "upload",
            "ip": self.remote_ip,
            "username": self.username,
            "filename": os.path.basename(file),
            "file_size": file_size,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        _notify_api(log_entry)
        print(f"[FTP] Upload: {os.path.basename(file)} ({file_size} bytes) by {self.username}")

    def on_file_sent(self, file):
        file_size = os.path.getsize(file) if os.path.exists(file) else 0
        log_entry = {
            "event": "download",
            "ip": self.remote_ip,
            "username": self.username,
            "filename": os.path.basename(file),
            "file_size": file_size,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        _notify_api(log_entry)
        print(f"[FTP] Download: {os.path.basename(file)} by {self.username}")


def create_server(host="0.0.0.0", port=2121, admin_user="admin", admin_pass="admin123") -> FTPServer:
    """Create and configure the FTP server."""
    os.makedirs(FTP_ROOT, exist_ok=True)

    authorizer = DummyAuthorizer()
    authorizer.add_user(admin_user, admin_pass, FTP_ROOT, perm="elradfmwMT")
    authorizer.add_user("guest", "guest", FTP_ROOT, perm="elr")  
    authorizer.add_anonymous(FTP_ROOT, perm="elr")  

    handler = NetWatchFTPHandler
    handler.authorizer = authorizer
    handler.banner = "Welcome to NetWatch FTP Server"
    handler.passive_ports = range(60000, 60100)

    server = FTPServer((host, port), handler)
    server.max_cons = 50
    server.max_cons_per_ip = 10

    return server


def main():
    print("=" * 60)
    print("  NetWatch FTP Server Configuration")
    print("=" * 60)
    
    print("Press Enter to keep the default [values].")
    host = input(f"Enter Host IP [{FTP_HOST}]: ").strip() or FTP_HOST
    port_str = input(f"Enter Port [{FTP_PORT}]: ").strip()
    port = int(port_str) if port_str.isdigit() else FTP_PORT
    
    admin_user = input("Enter Admin Username [admin]: ").strip() or "admin"
    admin_pass = input("Enter Admin Password [admin123]: ").strip() or "admin123"

    print("=" * 60)
    print("  Starting NetWatch FTP Server...")
    print("=" * 60)
    print(f"  Host        : {host}")
    print(f"  Port        : {port}")
    print(f"  Root Dir    : {FTP_ROOT}")
    print(f"  DB Storage  : Managed via Central API ({API_URL})")
    print("-" * 60)
    print("  Users:")
    print(f"    {admin_user} / {admin_pass}  (full access)")
    print("    guest / guest     (read-only)")
    print("    anonymous         (read-only)")
    print("=" * 60)
    print("  [*] Press Ctrl+C to stop the server\n")

    server = create_server(host, port, admin_user, admin_pass)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[*] FTP Server shutting down...")
        server.close_all()


if __name__ == "__main__":
    main()
