import React from 'react';

const icons = {
  packets: (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
    </svg>
  ),
  alerts: (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
    </svg>
  ),
  ips: (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M21 12a9 9 0 01-9 9m9-9a9 9 0 00-9-9m9 9H3m9 9a9 9 0 01-9-9m9 9c1.657 0 3-4.03 3-9s-1.343-9-3-9m0 18c-1.657 0-3-4.03-3-9s1.343-9 3-9m-9 9a9 9 0 019-9" />
    </svg>
  ),
  ftp: (
    <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M3 7v10a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-6l-2-2H5a2 2 0 00-2 2z" />
    </svg>
  ),
};

const colorMap = {
  packets: { 
    gradient: 'from-blue-600 to-cyan-500 dark:from-blue-500 dark:to-cyan-400', 
    bg: 'bg-blue-100 dark:bg-blue-500/10', 
    text: 'text-blue-600 dark:text-blue-400' 
  },
  alerts:  { 
    gradient: 'from-red-600 to-orange-500 dark:from-red-500 dark:to-orange-400', 
    bg: 'bg-red-100 dark:bg-red-500/10', 
    text: 'text-red-600 dark:text-red-400' 
  },
  ips:     { 
    gradient: 'from-violet-600 to-purple-500 dark:from-violet-500 dark:to-purple-400', 
    bg: 'bg-violet-100 dark:bg-violet-500/10', 
    text: 'text-violet-600 dark:text-violet-400' 
  },
  ftp:     { 
    gradient: 'from-emerald-600 to-teal-500 dark:from-emerald-500 dark:to-teal-400', 
    bg: 'bg-emerald-100 dark:bg-emerald-500/10', 
    text: 'text-emerald-600 dark:text-emerald-400' 
  },
};

export default function StatsCards({ stats }) {
  const cards = [
    { key: 'packets', label: 'Total Packets', value: stats?.total_packets ?? 0 },
    { key: 'alerts',  label: 'Alerts',         value: stats?.alerts_count ?? 0 },
    { key: 'ips',     label: 'Active IPs',     value: stats?.active_ips ?? 0 },
    { key: 'ftp',     label: 'FTP Activity',   value: stats?.ftp_activity_count ?? 0 },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map((card, idx) => {
        const color = colorMap[card.key];
        return (
          <div
            key={card.key}
            className="glass-card p-5 animate-fade-in"
            style={{ animationDelay: `${idx * 80}ms` }}
          >
            <div className="flex items-center justify-between mb-3">
              <div className={`p-2.5 rounded-xl ${color.bg}`}>
                <span className={color.text}>{icons[card.key]}</span>
              </div>
              <div className={`glow-dot ${card.key === 'alerts' && card.value > 0 ? 'red' : 'green'}`} />
            </div>

            <p className="text-nw-muted text-xs uppercase tracking-wider font-medium mb-1">
              {card.label}
            </p>
            <p className={`text-3xl font-bold bg-gradient-to-r ${color.gradient} bg-clip-text text-transparent`}>
              {typeof card.value === 'number' ? card.value.toLocaleString() : card.value}
            </p>
          </div>
        );
      })}
    </div>
  );
}
