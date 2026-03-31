import React, { useState } from 'react';

const protocolColors = {
  TCP: 'text-blue-600 dark:text-blue-400',
  UDP: 'text-emerald-600 dark:text-emerald-400',
  ICMP: 'text-amber-600 dark:text-amber-400',
};

export default function PacketTable({ packets }) {
  const [filter, setFilter] = useState('');
  const data = packets || [];

  const filtered = data.filter((pkt) => {
    if (!filter) return true;
    const q = filter.toLowerCase();
    return (
      (pkt.src_ip || '').toLowerCase().includes(q) ||
      (pkt.dst_ip || '').toLowerCase().includes(q) ||
      (pkt.protocol || '').toLowerCase().includes(q)
    );
  });

  return (
    <div className="glass-card p-5 animate-fade-in">
      <div className="flex items-center justify-between mb-4 flex-wrap gap-2">
        <div>
          <h3 className="text-sm font-semibold text-nw-text">📦 Packet Log</h3>
          <p className="text-xs text-nw-muted mt-0.5">
            Showing {filtered.length} of {data.length} packets
          </p>
        </div>
        <input
          type="text"
          placeholder="Filter by IP or protocol..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="bg-nw-bg border border-nw-border rounded-lg px-3 py-1.5 text-xs
                     text-nw-text placeholder-nw-muted/50 focus:outline-none focus:border-nw-accent/50
                     transition-colors w-56"
        />
      </div>

      <div className="overflow-x-auto max-h-96 overflow-y-auto">
        <table className="data-table">
          <thead>
            <tr>
              <th>Time</th>
              <th>Source IP</th>
              <th>Location</th>
              <th>Dest IP</th>
              <th>Protocol</th>
              <th>Src Port</th>
              <th>Dst Port</th>
              <th>Size</th>
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={8} className="text-center py-8 text-nw-muted !font-sans">
                  {data.length === 0 ? 'No packets captured yet...' : 'No matching packets'}
                </td>
              </tr>
            ) : (
              filtered.slice(0, 100).map((pkt, idx) => (
                <tr key={idx}>
                  <td className="text-nw-muted/80 text-[0.7rem]">
                    {pkt.timestamp ? new Date(pkt.timestamp).toLocaleTimeString() : '--'}
                  </td>
                  <td className="text-nw-accent font-medium">{pkt.src_ip}</td>
                  <td className="text-[0.65rem] text-nw-text/80 whitespace-nowrap">
                    {pkt.src_geo && pkt.src_geo.country !== 'Unknown' && pkt.src_geo.country !== 'Local' ? (
                      <span title={`${pkt.src_geo.city}, ${pkt.src_geo.country}`}>🌍 {pkt.src_geo.country}</span>
                    ) : pkt.src_geo && pkt.src_geo.country === 'Local' ? (
                      <span title="Local Network">🏠 Local</span>
                    ) : (
                      <span className="text-nw-muted">--</span>
                    )}
                  </td>
                  <td className="text-nw-text/80">{pkt.dst_ip}</td>
                  <td>
                    <span className={`font-semibold ${protocolColors[pkt.protocol] || 'text-nw-muted'}`}>
                      {pkt.protocol}
                    </span>
                  </td>
                  <td className="text-nw-muted">{pkt.src_port || '--'}</td>
                  <td className="text-nw-muted">{pkt.dst_port || '--'}</td>
                  <td className="text-nw-muted">{pkt.size ? `${pkt.size} B` : '--'}</td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
