import requests
import ipaddress
import threading

# In-memory cache to prevent repeatedly hitting the external Geo API
_geo_cache = {}
_geo_lock = threading.Lock()

def get_geo(ip_str):
    """
    Returns geographical mapping {country, city} for a given IP.
    Uses an in-memory cache and ip-api.com for public IPs.
    """
    if not ip_str:
        return {"country": "Unknown", "city": "Unknown"}
        
    with _geo_lock:
        if ip_str in _geo_cache:
            return _geo_cache[ip_str]
            
    try:
        # Avoid external lookup for private/local IP ranges
        ip_obj = ipaddress.ip_address(ip_str)
        if ip_obj.is_private or ip_obj.is_loopback:
            geo = {"country": "Local", "city": "Network"}
            with _geo_lock:
                _geo_cache[ip_str] = geo
            return geo
            
        # External lookup via free API
        resp = requests.get(f"http://ip-api.com/json/{ip_str}", timeout=2)
        if resp.status_code == 200:
            data = resp.json()
            if data.get("status") == "success":
                geo = {
                    "country": data.get("countryCode", "Unknown"),
                    "city": data.get("city", "Unknown")
                }
                with _geo_lock:
                    _geo_cache[ip_str] = geo
                return geo
    except Exception:
        # Fail gracefully on network errors or invalid IPs
        pass

    geo = {"country": "Unknown", "city": "Unknown"}
    with _geo_lock:
        _geo_cache[ip_str] = geo
    return geo
