import sqlite3
import threading
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "netwatch.db")
_db_lock = threading.Lock()

def get_connection():
    """Get a thread-safe connection to the SQLite database."""
    # check_same_thread=False allows FastAPI threads to share the connection 
    # if necessary, though we will try to use context blocks
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row  # Return dict-like rows
    # Enable WAL mode for better concurrency performance
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

def init_db():
    """Initialize the database schema."""
    with _db_lock:
        conn = get_connection()
        c = conn.cursor()
        
        # Packets Table
        c.execute('''
            CREATE TABLE IF NOT EXISTS packets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                src_ip TEXT,
                dst_ip TEXT,
                protocol TEXT,
                size INTEGER,
                timestamp TEXT,
                src_port INTEGER,
                dst_port INTEGER
            )
        ''')
        
        # Alerts Table
        c.execute('''
            CREATE TABLE IF NOT EXISTS alerts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                severity TEXT,
                source_ip TEXT,
                message TEXT,
                timestamp TEXT,
                category TEXT,
                blocked BOOLEAN DEFAULT 0
            )
        ''')
        
        # FTP Events Table
        c.execute('''
            CREATE TABLE IF NOT EXISTS ftp_events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                event TEXT,
                ip TEXT,
                username TEXT,
                status TEXT,
                filename TEXT,
                file_size INTEGER,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
        print(f"[*] SQLite Database initialized at {DB_PATH}")

# ---------------------------------------------------------
# Insert Functions
# ---------------------------------------------------------

def insert_packet(pkt: dict):
    with _db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO packets (src_ip, dst_ip, protocol, size, timestamp, src_port, dst_port)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            pkt.get('src_ip', ''), pkt.get('dst_ip', ''), pkt.get('protocol', 'TCP'),
            pkt.get('size', 0), pkt.get('timestamp', ''), pkt.get('src_port', 0),
            pkt.get('dst_port', 0)
        ))
        conn.commit()
        conn.close()

def insert_alert(alert: dict, category: str = 'network'):
    with _db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO alerts (type, severity, source_ip, message, timestamp, category, blocked)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            alert.get('type', ''), alert.get('severity', ''), alert.get('source_ip', ''),
            alert.get('message', ''), alert.get('timestamp', ''), category,
            1 if alert.get('blocked') else 0
        ))
        inserted_id = c.lastrowid
        conn.commit()
        conn.close()
        return inserted_id

def insert_ftp_event(event: dict):
    with _db_lock:
        conn = get_connection()
        c = conn.cursor()
        c.execute('''
            INSERT INTO ftp_events (event, ip, username, status, filename, file_size, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            event.get('event', ''), event.get('ip', ''), event.get('username', ''),
            event.get('status', ''), event.get('filename', ''), event.get('file_size', 0),
            event.get('timestamp', '')
        ))
        conn.commit()
        conn.close()

# ---------------------------------------------------------
# Default Queries for Endpoints
# ---------------------------------------------------------

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def query_db(query, args=(), one=False):
    conn = get_connection()
    conn.row_factory = dict_factory
    cur = conn.execute(query, args)
    rv = cur.fetchall()
    cur.close()
    conn.close()
    return (rv[0] if rv else None) if one else rv

def get_recent_packets(limit=50):
    return query_db('SELECT * FROM packets ORDER BY id DESC LIMIT ?', [limit])

def get_recent_alerts(limit=50):
    return query_db('SELECT * FROM alerts ORDER BY timestamp DESC LIMIT ?', [limit])

def get_ftp_alerts(limit=50):
    return query_db('SELECT * FROM alerts WHERE category = "ftp" ORDER BY timestamp DESC LIMIT ?', [limit])

def get_network_alerts(limit=50):
    return query_db('SELECT * FROM alerts WHERE category = "network" ORDER BY timestamp DESC LIMIT ?', [limit])

def get_ftp_activity(limit=50):
    return query_db('SELECT * FROM ftp_events ORDER BY timestamp DESC LIMIT ?', [limit])

# ---------------------------------------------------------
# Stats Queries
# ---------------------------------------------------------

def get_total_packets_count():
    res = query_db('SELECT COUNT(id) as count FROM packets', one=True)
    return res['count'] if res else 0

def get_active_ips_count():
    res = query_db('SELECT COUNT(DISTINCT src_ip) as count FROM packets', one=True)
    return res['count'] if res else 0

def get_top_ips(limit=10):
    return query_db('''
        SELECT src_ip as ip, COUNT(id) as count 
        FROM packets 
        GROUP BY src_ip 
        ORDER BY count DESC 
        LIMIT ?
    ''', [limit])

def get_protocol_distribution():
    res = query_db('''
        SELECT protocol as name, COUNT(id) as value 
        FROM packets 
        GROUP BY protocol
    ''')
    return res

def get_traffic_timeline(limit=60):
    # Groups by exact second timestamp (YYYY-MM-DDTHH:MM:SS format typically limits to second)
    res = query_db('''
        SELECT substr(timestamp, 1, 19) as time, COUNT(id) as packets 
        FROM packets 
        GROUP BY time 
        ORDER BY time DESC 
        LIMIT ?
    ''', [limit])
    # Reverse so oldest is first for the graph
    return list(reversed(res))

def get_ftp_stats():
    res_uploads = query_db('SELECT COUNT(id) as c FROM ftp_events WHERE event = "upload"', one=True)
    res_downloads = query_db('SELECT COUNT(id) as c FROM ftp_events WHERE event = "download"', one=True)
    res_logins = query_db('SELECT COUNT(id) as c FROM ftp_events WHERE event = "login"', one=True)
    res_failed = query_db('SELECT COUNT(id) as c FROM ftp_events WHERE event = "login" AND status = "failed"', one=True)
    res_unique_ips = query_db('SELECT COUNT(DISTINCT ip) as c FROM ftp_events', one=True)
    
    return {
        "uploads": res_uploads['c'] if res_uploads else 0,
        "downloads": res_downloads['c'] if res_downloads else 0,
        "logins": res_logins['c'] if res_logins else 0,
        "failed_logins": res_failed['c'] if res_failed else 0,
        "unique_ips": res_unique_ips['c'] if res_unique_ips else 0
    }
