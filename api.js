import axios from 'axios';

const API_BASE = 'http://localhost:8000';

const api = axios.create({
  baseURL: API_BASE,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// ── Dashboard Stats ──
export const fetchStats = async () => {
  const { data } = await api.get('/stats');
  return data;
};

// ── Packets ──
export const fetchPackets = async (limit = 50) => {
  const { data } = await api.get(`/packets?limit=${limit}`);
  return data;
};

// ── Alerts ──
export const fetchAlerts = async (limit = 50) => {
  const { data } = await api.get(`/alerts?limit=${limit}`);
  return data;
};

// ── FTP Activity ──
export const fetchFTPActivity = async (limit = 50) => {
  const { data } = await api.get(`/ftp-activity?limit=${limit}`);
  return data;
};

// ── Traffic Timeline ──
export const fetchTrafficData = async (limit = 60) => {
  const { data } = await api.get(`/traffic-data?limit=${limit}`);
  return data;
};

// ── Top IPs ──
export const fetchTopIPs = async (limit = 10) => {
  const { data } = await api.get(`/top-ips?limit=${limit}`);
  return data;
};

// ── Protocol Distribution ──
export const fetchProtocols = async () => {
  const { data } = await api.get('/protocols');
  return data;
};

// ── Health Check ──
export const checkHealth = async () => {
  try {
    const { data } = await api.get('/health');
    return { connected: true, ...data };
  } catch {
    return { connected: false, status: 'disconnected' };
  }
};

export default api;
