"""
NetWatch - Network Packet Sniffer
Captures real-time network packets using Scapy and sends them to the backend API.

Usage:
    Run with administrator/root privileges:
        python sniffer.py

    Optional arguments:
        --interface <name>   Network interface to sniff on (default: auto-detect)
        --api-url <url>      Backend API URL (default: http://localhost:8000)
        --count <n>          Number of packets to capture, 0 = infinite (default: 0)
"""

import argparse
import sys
import time
import requests
from datetime import datetime, timezone

try:
    from scapy.all import sniff, IP, TCP, UDP, ICMP, conf
except ImportError:
    print("ERROR: Scapy is not installed. Run: pip install scapy")
    sys.exit(1)

from utils.helpers import protocol_name

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
API_URL = "http://localhost:8000"
BATCH_SIZE = 10
BATCH_TIMEOUT = 2  # seconds

# ---------------------------------------------------------------------------
# Upload detection (HTTPS large outbound packets)
# ---------------------------------------------------------------------------
UPLOAD_PACKET_SIZE = 600
UPLOAD_PACKET_THRESHOLD = 5
upload_tracker = {}

packet_buffer: list[dict] = []
last_flush_time: float = time.time()


def extract_packet_info(packet) -> dict | None:
    """Extract relevant fields from a captured packet."""
    if not packet.haslayer(IP):
        return None

    ip_layer = packet[IP]
    info = {
        "src_ip": ip_layer.src,
        "dst_ip": ip_layer.dst,
        "protocol": protocol_name(ip_layer.proto),
        "size": len(packet),
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "src_port": 0,
        "dst_port": 0,
    }

    if packet.haslayer(TCP):
        info["src_port"] = packet[TCP].sport
        info["dst_port"] = packet[TCP].dport
    elif packet.haslayer(UDP):
        info["src_port"] = packet[UDP].sport
        info["dst_port"] = packet[UDP].dport

    return info


def flush_buffer():
    """Send buffered packets to the backend API."""
    global packet_buffer, last_flush_time

    if not packet_buffer:
        return

    for pkt_data in packet_buffer:
        try:
            requests.post(f"{API_URL}/packet", json=pkt_data, timeout=2)
        except requests.exceptions.RequestException:
            pass  # Backend might be down; silently skip

    packet_buffer = []
    last_flush_time = time.time()


def packet_callback(packet):
    """Callback invoked for each captured packet."""
    global last_flush_time

    info = extract_packet_info(packet)
    if info is None:
        return

    src_ip = info["src_ip"]
    dst_ip = info["dst_ip"]
    dst_port = info["dst_port"]
    size = info["size"]

    # ---------------------------------------------------------
    # HTTPS Upload Detection (burst of outbound packets)
    # ---------------------------------------------------------

    # Detect traffic leaving local machine to HTTPS
    if dst_port == 443 and src_ip.startswith(("192.168", "10.", "172.")):

        if size > 500:  # lowered threshold for encrypted uploads

            upload_tracker[src_ip] = upload_tracker.get(src_ip, 0) + 1

            # Debug log to see packets
            print(f"PACKET: {src_ip} → {dst_ip} size={size}")

            if upload_tracker[src_ip] >= 6:  # burst threshold

                print(f"[UPLOAD DETECTED] {src_ip} → {dst_ip}")

                try:
                    requests.post(
                        f"{API_URL}/ftp-event",
                        json={
                            "event": "upload",
                            "ip": src_ip,
                            "username": "HTTPS Upload",
                            "filename": "encrypted_transfer",
                            "file_size": size,
                            "timestamp": datetime.now(timezone.utc).isoformat()
                        },
                        timeout=2
                    )
                except requests.exceptions.RequestException:
                    pass

                upload_tracker[src_ip] = 0

    # ---------------------------------------------------------
    # Normal packet buffering (always happens)
    # ---------------------------------------------------------

    packet_buffer.append(info)

    # Flush when buffer full or timeout reached
    if len(packet_buffer) >= BATCH_SIZE or (time.time() - last_flush_time) > BATCH_TIMEOUT:
        flush_buffer()


def main():
    parser = argparse.ArgumentParser(description="NetWatch Packet Sniffer")
    parser.add_argument("--interface", "-i", default=None, help="Network interface")
    parser.add_argument("--api-url", default="http://localhost:8000", help="Backend URL")
    parser.add_argument("--count", "-c", type=int, default=0, help="Packets to capture (0=infinite)")
    args = parser.parse_args()

    global API_URL
    API_URL = args.api_url

    print("=" * 60)
    print("  NetWatch Packet Sniffer")
    print("=" * 60)
    print(f"  Backend API : {API_URL}")
    print(f"  Interface   : {args.interface or 'auto-detect'}")
    print(f"  Count       : {'infinite' if args.count == 0 else args.count}")
    print("=" * 60)
    print("  [!] Make sure you run this with admin/root privileges")
    print("  [*] Press Ctrl+C to stop capturing\n")

    try:
        sniff(
            iface=args.interface,
            prn=packet_callback,
            count=args.count if args.count > 0 else 0,
            store=False,
        )
    except KeyboardInterrupt:
        print("\n[*] Stopping sniffer...")
    except PermissionError:
        print("\n[!] ERROR: Permission denied. Run as administrator/root.")
        sys.exit(1)
    finally:
        flush_buffer()
        print("[*] Sniffer stopped. Remaining packets flushed.")


if __name__ == "__main__":
    main()
