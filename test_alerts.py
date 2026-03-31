import requests
import time
import random
import ftplib
import os

API_URL = "http://localhost:8000"

# Use a session for faster sequential requests
session = requests.Session()

def safe_post(url, data):
    """Safely post data with retry logic for connection errors."""
    try:
        session.post(url, json=data, timeout=2)
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        # Small wait if server is busy/reloading
        time.sleep(0.5)
        try:
            session.post(url, json=data, timeout=2)
        except:
            pass # Skip if still failing

def test_ddos():
    print("[*] Simulating DDoS Attack (High traffic from 1.2.3.4)...")
    for _ in range(110):
        safe_post(f"{API_URL}/packet", {
            "src_ip": "1.2.3.4",
            "dst_ip": "192.168.1.10",
            "protocol": "TCP",
            "size": 64,
            "dst_port": 80
        })
    print("[+] Done. Check dashboard for 'DDoS Attempt' alert.")

def test_port_scan():
    print("[*] Simulating Port Scan (IP 5.6.7.8 scanning 20 ports)...")
    for port in range(1, 21):
        safe_post(f"{API_URL}/packet", {
            "src_ip": "5.6.7.8",
            "dst_ip": "192.168.1.10",
            "protocol": "TCP",
            "size": 64,
            "dst_port": port
        })
    print("[+] Done. Check dashboard for 'Port Scan' alert.")

def test_udp_flood():
    print("[*] Simulating UDP Flood Attack (High UDP traffic from 3.3.3.3)...")
    for _ in range(60):
        safe_post(f"{API_URL}/packet", {
            "src_ip": "3.3.3.3",
            "dst_ip": "192.168.1.50",
            "protocol": "UDP",
            "size": 1400,
            "dst_port": 53 # DNS
        })
    print("[+] Done. Check dashboard for 'UDP Flood' alert.")

def test_traffic_spike():
    print("[*] Simulating Traffic Spike (>200 packets/sec)...")
    for _ in range(250):
        safe_post(f"{API_URL}/packet", {
            "src_ip": f"9.9.9.{random.randint(1,100)}",
            "dst_ip": "192.168.1.10",
            "protocol": random.choice(["TCP", "UDP"]),
            "size": random.randint(100, 1500),
            "dst_port": 443
        })
    print("[+] Done. Check dashboard for 'Traffic Spike' alert.")

def test_new_connection():
    print("[*] Simulating New Device Connection (Low Severity Alert)...")
    new_ip = f"172.16.0.{random.randint(1, 254)}"
    safe_post(f"{API_URL}/packet", {
        "src_ip": new_ip,
        "dst_ip": "192.168.1.10",
        "protocol": "TCP",
        "size": 60,
        "dst_port": 443
    })
    print(f"[+] Done. Check dashboard for 'New Connection' (Green) alert from {new_ip}.")

def test_ftp_brute_force():
    print("[*] Simulating FTP Brute Force (5 failed logins)...")
    for _ in range(5):
        safe_post(f"{API_URL}/ftp-event", {
            "event": "login",
            "ip": "10.0.0.1",
            "username": "admin",
            "status": "failed",
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })
    print("[+] Done. Check dashboard for 'FTP Brute Force' alert.")

def test_ftp_success_login():
    print("[*] Simulating Successful FTP Login...")
    safe_post(f"{API_URL}/ftp-event", {
        "event": "login",
        "ip": "10.0.0.5",
        "username": "user1",
        "status": "success",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })
    print("[+] Done.")

def test_ftp_activities():
    print("[*] Simulating FTP Uploads and Downloads...")
    for i in range(5):
        safe_post(f"{API_URL}/ftp-event", {
            "event": "upload",
            "ip": "10.0.0.2",
            "username": "user1",
            "filename": f"data_upload_{i}.txt",
            "file_size": 1024 * 50,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })
    for i in range(3):
        safe_post(f"{API_URL}/ftp-event", {
            "event": "download",
            "ip": "10.0.0.2",
            "username": "user1",
            "filename": f"resource_file_{i}.pdf",
            "file_size": 1024 * 1000,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        })
    print("[+] Done.")

def test_large_file_transfer():
    print("[*] Simulating Large File Transfer (75 MB file)...")
    safe_post(f"{API_URL}/ftp-event", {
        "event": "upload",
        "ip": "10.0.0.3",
        "username": "admin",
        "filename": "database_backup_huge.sql",
        "file_size": 75 * 1024 * 1024,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    })
    print("[+] Done.")

def test_custom_ftp_event():
    print("\n[*] Custom FTP Event Simulator")
    event_type = input("Enter event (upload/download/login) [upload]: ").strip().lower() or "upload"
    username = input("Enter username [admin]: ").strip() or "admin"
    ip = input("Enter IP address [10.0.0.99]: ").strip() or "10.0.0.99"
    
    payload = {
        "event": event_type,
        "ip": ip,
        "username": username,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    }
    
    if event_type in ["upload", "download"]:
        filename = input("Enter filename [custom_file.txt]: ").strip() or "custom_file.txt"
        try:
            size_mb = float(input("Enter file size in MB [1.5]: ").strip() or "1.5")
        except ValueError:
            size_mb = 1.5
        payload["filename"] = filename
        payload["file_size"] = int(size_mb * 1024 * 1024)
    elif event_type == "login":
        status = input("Enter status (success/failed) [success]: ").strip().lower() or "success"
        payload["status"] = status
        
    safe_post(f"{API_URL}/ftp-event", payload)
    print(f"[+] Custom '{event_type}' event sent to dashboard!")

def real_ftp_transfer():
    print("\n[*] Real FTP File Transfer (Upload/Download actual files to the server)")
    action = input("Enter action (upload/download) [upload]: ").strip().lower() or "upload"
    
    if action == "upload":
        filepath = input("Enter the FULL PATH of the file on your PC to upload: ").strip()
        if not os.path.exists(filepath):
            print("[-] Error: File not found on your PC!")
            return
        filename = os.path.basename(filepath)
    else:
        filename = input("Enter the name of the file on the server to download: ").strip()
        filepath = input("Enter the FULL PATH on your PC where to save it: ").strip()

    try:
        print(f"[*] Connecting to FTP Server on localhost:2121...")
        ftp = ftplib.FTP()
        ftp.connect("localhost", 2121)
        ftp.login("admin", "admin123")
        
        if action == "upload":
            with open(filepath, "rb") as f:
                ftp.storbinary(f"STOR {filename}", f)
            print(f"[+] Successfully uploaded '{filename}'!")
        else:
            with open(filepath, "wb") as f:
                ftp.retrbinary(f"RETR {filename}", f.write)
            print(f"[+] Successfully saved '{filename}' to {filepath}!")
            
        ftp.quit()
    except Exception as e:
        print(f"[-] FTP Error: {e}")

if __name__ == "__main__":
    print("=== NetWatch Enhanced Testing Tool v2 ===")
    print("1. Network Alerts (DDoS, Port Scan, UDP Flood, Spike, New IP)")
    print("2. FTP Activities (Success, Uploads, Downloads)")
    print("3. FTP Alerts (Brute Force, Large File)")
    print("4. Run ALL Tests")
    print("5. Custom FTP Event Simulator (Fake event)")
    print("6. Real FTP File Transfer (Upload/Download an ACTUAL file from your PC)")
    
    choice = input("\nSelect a test (1-6): ")
    print("-" * 50)
    
    if choice == '1':
        test_new_connection()
        test_ddos()
        test_port_scan()
        test_udp_flood()
        test_traffic_spike()
    elif choice == '2':
        test_ftp_success_login()
        test_ftp_activities()
    elif choice == '3':
        test_ftp_brute_force()
        test_large_file_transfer()
    elif choice == '4':
        test_ftp_success_login()
        test_ftp_activities()
        time.sleep(0.5)
        test_new_connection()
        test_udp_flood()
        test_ftp_brute_force()
        test_ddos()
        test_port_scan()
        test_large_file_transfer()
        test_traffic_spike()
    elif choice == '5':
        test_custom_ftp_event()
    elif choice == '6':
        real_ftp_transfer()
    else:
        print("Invalid choice.")
