import React from 'react';

const severityConfig = {
  high:   { badge: 'badge-high',   icon: '🔴', border: 'border-l-red-500' },
  medium: { badge: 'badge-medium', icon: '🟡', border: 'border-l-yellow-500' },
  low:    { badge: 'badge-low',    icon: '🟢', border: 'border-l-green-500' },
};

export default function AlertsPanel({ alerts }) {
  const data = alerts || [];

  return (
    <div className="glass-card p-5 animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-nw-text">⚠️ Alerts</h3>
          <p className="text-xs text-nw-muted mt-0.5">
            {data.length} active alert{data.length !== 1 ? 's' : ''}
          </p>
        </div>
        {data.length > 0 && (
          <span className="badge badge-high animate-pulse">{data.length}</span>
        )}
      </div>

      <div className="space-y-2 max-h-80 overflow-y-auto pr-1">
        {data.length === 0 ? (
          <div className="text-center py-8 text-nw-muted text-sm">
            <p className="text-2xl mb-2">✅</p>
            <p>No alerts detected</p>
          </div>
        ) : (
          data.map((alert, idx) => {
            const config = severityConfig[alert.severity] || severityConfig.low;
            return (
              <div
                key={alert.id || idx}
                className={`bg-nw-bg/60 rounded-lg p-3 border-l-4 ${config.border} animate-slide-in`}
                style={{ animationDelay: `${idx * 50}ms` }}
              >
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className={`badge ${config.badge}`}>{alert.severity}</span>
                      <span className="text-xs font-medium text-nw-text">{alert.type}</span>
                    </div>
                    <p className="text-xs text-nw-muted truncate">{alert.message}</p>
                    <div className="flex items-center gap-3 mt-1.5">
                      {alert.source_ip && alert.source_ip !== 'N/A' && (
                        <span className="text-xs font-mono text-blue-600/80 dark:text-blue-400/80">{alert.source_ip}</span>
                      )}
                      {alert.blocked && (
                        <span className="px-1.5 py-0.5 rounded text-[0.6rem] font-bold bg-red-600/20 text-red-500 border border-red-500/50 animate-pulse tracking-widest uppercase">
                          Blocked 🛑
                        </span>
                      )}
                      <span className="text-xs text-nw-muted/60">
                        {alert.timestamp ? new Date(alert.timestamp).toLocaleTimeString() : ''}
                      </span>
                    </div>
                  </div>
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
