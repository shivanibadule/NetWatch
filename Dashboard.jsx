import React, { useState, useEffect, useCallback } from 'react';
import StatsCards from '../components/StatsCards';
import TrafficChart from '../components/TrafficChart';
import AlertsPanel from '../components/AlertsPanel';
import PacketTable from '../components/PacketTable';
import TopIPs from '../components/TopIPs';
import FTPPanel from '../components/FTPPanel';
import ThemeToggle from '../components/ThemeToggle';
import {
  fetchStats,
  fetchPackets,
  fetchAlerts,
  fetchFTPActivity,
  fetchTrafficData,
  fetchTopIPs,
  fetchProtocols,
  checkHealth,
} from '../services/api';

const POLL_INTERVAL = 5000; // 5 seconds

export default function Dashboard() {
  const [stats, setStats] = useState(null);
  const [packets, setPackets] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [ftpActivity, setFtpActivity] = useState([]);
  const [traffic, setTraffic] = useState([]);
  const [topIPs, setTopIPs] = useState([]);
  const [protocols, setProtocols] = useState([]);
  const [connected, setConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(null);

  const loadData = useCallback(async () => {
    try {
      const [
        statsRes,
        packetsRes,
        alertsRes,
        ftpRes,
        trafficRes,
        topIPsRes,
        protocolsRes,
        healthRes,
      ] = await Promise.allSettled([
        fetchStats(),
        fetchPackets(50),
        fetchAlerts(50),
        fetchFTPActivity(50),
        fetchTrafficData(60),
        fetchTopIPs(10),
        fetchProtocols(),
        checkHealth(),
      ]);

      if (statsRes.status === 'fulfilled') setStats(statsRes.value);
      if (packetsRes.status === 'fulfilled') setPackets(packetsRes.value.packets || []);
      if (alertsRes.status === 'fulfilled') setAlerts(alertsRes.value.alerts || []);
      if (ftpRes.status === 'fulfilled') setFtpActivity(ftpRes.value.activity || []);
      if (trafficRes.status === 'fulfilled') setTraffic(trafficRes.value.traffic || []);
      if (topIPsRes.status === 'fulfilled') setTopIPs(topIPsRes.value.top_ips || []);
      if (protocolsRes.status === 'fulfilled') setProtocols(protocolsRes.value.protocols || []);
      if (healthRes.status === 'fulfilled') setConnected(healthRes.value.connected);

      setLastUpdate(new Date());
    } catch (err) {
      setConnected(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, POLL_INTERVAL);
    return () => clearInterval(interval);
  }, [loadData]);

  return (
    <div className="min-h-screen bg-nw-bg text-nw-text transition-colors duration-300">
      {/* Header */}
      <header className="sticky top-0 z-50 bg-nw-bg/80 backdrop-blur-xl border-b border-nw-border">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 py-3 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="w-9 h-9 rounded-xl bg-gradient-to-br from-blue-500 to-violet-600 flex items-center justify-center shadow-lg shadow-blue-500/20">
              <span className="text-white text-lg">🛡</span>
            </div>
            <div>
              <h1 className="text-lg font-bold gradient-text tracking-tight">NetWatch</h1>
              <p className="text-[0.6rem] text-nw-muted -mt-0.5">Network Monitoring & IDS</p>
            </div>
          </div>

          <div className="flex items-center gap-4">
            {lastUpdate && (
              <span className="text-[0.65rem] text-nw-muted hidden sm:block">
                Updated {lastUpdate.toLocaleTimeString()}
              </span>
            )}
            <div className="flex items-center gap-3 ps-4 border-l border-nw-border/50">
              <div className="flex items-center gap-2">
                <div className={`glow-dot ${connected ? 'green' : 'red'}`} />
                <span className={`text-xs font-medium ${connected ? 'text-emerald-500' : 'text-red-500'}`}>
                  {connected ? 'Connected' : 'Disconnected'}
                </span>
              </div>
              <ThemeToggle />
            </div>
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-[1600px] mx-auto px-4 sm:px-6 py-6 space-y-4">
        {/* Stats Cards */}
        <StatsCards stats={stats} />

        {/* Charts Row */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
          <div className="lg:col-span-2">
            <TrafficChart traffic={traffic} />
          </div>
          <div>
            <AlertsPanel alerts={alerts} />
          </div>
        </div>

        {/* Top IPs + Protocol Distribution */}
        <TopIPs topIPs={topIPs} protocols={protocols} />

        {/* FTP Panel */}
        <FTPPanel activity={ftpActivity} alerts={alerts} />

        {/* Packet Table */}
        <PacketTable packets={packets} />
      </main>

      {/* Footer */}
      <footer className="border-t border-nw-border py-4 mt-8">
        <div className="max-w-[1600px] mx-auto px-4 sm:px-6 flex items-center justify-between">
          <p className="text-xs text-nw-muted">
            NetWatch v1.0 — Real-Time Network Monitoring & Intrusion Detection
          </p>
          <p className="text-xs text-nw-muted">
            Polling every {POLL_INTERVAL / 1000}s
          </p>
        </div>
      </footer>
    </div>
  );
}
