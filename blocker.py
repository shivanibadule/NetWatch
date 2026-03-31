"""
NetWatch IP Blocker Utility
Executes Windows Firewall commands to block malicious IPs.
Requires Administrator privileges to run successfully.
"""
import subprocess
import threading

# Keeping an in-memory set to prevent duplicate firewall rules
_blocked_ips = set()
_lock = threading.Lock()

def block_ip_windows(ip_address: str):
    """
    Blocks an incoming IP address using Windows Firewall (netsh).
    """
    # Prevent blocking absolute local hosts safely
    if not ip_address or ip_address in ["127.0.0.1", "localhost", "0.0.0.0", "Local Browser", "N/A", "unknown"]:
        return

    with _lock:
        if ip_address in _blocked_ips:
            return  # Already blocked in this session, skip
        _blocked_ips.add(ip_address)

    try:
        # Construct the netsh command:
        # netsh advfirewall firewall add rule name="NetWatch Block <IP>" dir=in action=block remoteip=<IP>
        rule_name = f"NetWatch Block {ip_address}"
        command = [
            "netsh", "advfirewall", "firewall", "add", "rule",
            f"name={rule_name}",
            "dir=in",
            "action=block",
            f"remoteip={ip_address}"
        ]
        
        # Execute silently
        # CREATE_NO_WINDOW prevents the cmd window from flashing
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            creationflags=subprocess.CREATE_NO_WINDOW if hasattr(subprocess, 'CREATE_NO_WINDOW') else 0
        )
        
        if result.returncode == 0:
            print(f"\n[IPS] WARNING: Blocked {ip_address} at Windows Firewall")
        else:
            print(f"\n[IPS] ERROR: Failed to block {ip_address} (Did you run backend as Administrator?)")
            # Remove from tracker so it tries again next time
            with _lock:
                _blocked_ips.discard(ip_address)
                
    except Exception as e:
        print(f"\n[IPS] ERROR executing firewall block for {ip_address}: {e}")
        with _lock:
            _blocked_ips.discard(ip_address)
