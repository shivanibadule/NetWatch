"""
NetWatch - Utility Helper Functions
Provides common utilities for timestamp formatting, IP validation, and data formatting.
"""

import re
from datetime import datetime, timezone


def get_timestamp() -> str:
    """Return current UTC timestamp in ISO 8601 format."""
    return datetime.now(timezone.utc).isoformat()


def is_valid_ip(ip: str) -> bool:
    """Validate an IPv4 address string."""
    pattern = r"^(\d{1,3}\.){3}\d{1,3}$"
    if not re.match(pattern, ip):
        return False
    return all(0 <= int(octet) <= 255 for octet in ip.split("."))


def protocol_name(proto_num: int) -> str:
    """Map protocol number to human-readable name."""
    protocols = {
        1: "ICMP",
        6: "TCP",
        17: "UDP",
        2: "IGMP",
    }
    return protocols.get(proto_num, f"OTHER({proto_num})")


def truncate(text: str, max_length: int = 100) -> str:
    """Truncate a string to a maximum length, appending '...' if truncated."""
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def format_bytes(size_bytes: int) -> str:
    """Format byte count into a human-readable string."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.1f} GB"


def safe_serialize(obj) -> dict:
    """
    Safely convert an object to a JSON-serializable dict.
    Falls back to string representation for non-serializable fields.
    """
    if isinstance(obj, dict):
        return {k: safe_serialize(v) for k, v in obj.items()}
    elif isinstance(obj, (list, tuple)):
        return [safe_serialize(item) for item in obj]
    elif isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, (int, float, str, bool, type(None))):
        return obj
    else:
        return str(obj)
