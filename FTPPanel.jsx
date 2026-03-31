import React from 'react';

const eventIcons = {
  upload: '⬆️',
  download: '⬇️',
  login: '🔑',
  connect: '🔗',
  disconnect: '🔌',
  ftp_traffic: '📡',
};

const eventColors = {
  upload: 'text-emerald-600 dark:text-emerald-400',
  download: 'text-blue-600 dark:text-blue-400',
  login: 'text-amber-600 dark:text-amber-400',
  connect: 'text-cyan-600 dark:text-cyan-400',
  disconnect: 'text-nw-muted',
  ftp_traffic: 'text-violet-600 dark:text-violet-400',
};

export default function FTPPanel({ activity, alerts }) {
  const activityData = activity || [];
  const alertsData = (alerts || []).filter((a) => a.category === 'ftp');

  const uploads = activityData.filter((a) => a.event === 'upload');
  const downloads = activityData.filter((a) => a.event === 'download');
  const logins = activityData.filter((a) => a.event === 'login');

  return (
    <div className="glass-card p-5 animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-nw-text">📂 FTP Activity</h3>
          <p className="text-xs text-nw-muted mt-0.5">File transfer & authentication logs</p>
        </div>
      </div>

      {/* FTP Mini Stats */}
      <div className="grid grid-cols-4 gap-3 mb-4">
        {[
          { label: 'Uploads', value: uploads.length, color: 'text-emerald-600 dark:text-emerald-400' },
          { label: 'Downloads', value: downloads.length, color: 'text-blue-600 dark:text-blue-400' },
          { label: 'Logins', value: logins.length, color: 'text-amber-600 dark:text-amber-400' },
          { label: 'FTP Alerts', value: alertsData.length, color: 'text-red-600 dark:text-red-400' },
        ].map((stat) => (
          <div key={stat.label} className="bg-nw-bg/50 rounded-lg p-2.5 text-center">
            <p className={`text-lg font-bold ${stat.color}`}>{stat.value}</p>
            <p className="text-[0.65rem] text-nw-muted uppercase tracking-wider">{stat.label}</p>
          </div>
        ))}
      </div>

      {/* FTP Alerts */}
      {alertsData.length > 0 && (
        <div className="mb-4">
          <h4 className="text-xs font-semibold text-red-600 dark:text-red-400 uppercase tracking-wider mb-2">
            🚨 FTP Alerts
          </h4>
          <div className="space-y-1.5 max-h-32 overflow-y-auto">
            {alertsData.map((alert, idx) => (
              <div key={idx} className="bg-red-500/5 dark:bg-red-500/10 border border-red-500/20 rounded-lg p-2 text-xs">
                <div className="flex items-center justify-between">
                  <span className="text-red-600 dark:text-red-400 font-medium">{alert.type}</span>
                  <span className="badge badge-high">{alert.severity}</span>
                </div>
                <p className="text-nw-muted mt-1 text-[0.7rem]">{alert.message}</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Activity Log */}
      <div className="space-y-1.5 max-h-60 overflow-y-auto pr-1">
        {activityData.length === 0 ? (
          <div className="text-center py-6 text-nw-muted text-sm">
            <p className="text-2xl mb-2">📂</p>
            <p>No FTP activity yet</p>
            <p className="text-xs mt-1">Start the FTP server and connect to see activity</p>
          </div>
        ) : (
          activityData.slice(0, 50).map((item, idx) => (
            <div
              key={idx}
              className="flex items-center gap-3 bg-nw-bg/40 rounded-lg px-3 py-2 text-xs"
            >
              <span className="text-base flex-shrink-0">{eventIcons[item.event] || '📄'}</span>
              <div className="flex-1 min-w-0">
                <span className={`font-medium ${eventColors[item.event] || 'text-nw-text'}`}>
                  {item.event?.toUpperCase()}
                </span>
                {item.username && (
                  <span className="text-nw-muted ml-2">by {item.username}</span>
                )}
                {item.filename && (
                  <span className="text-nw-text/70 ml-2 font-mono">{item.filename}</span>
                )}
                {item.status === 'failed' && (
                  <span className="badge badge-high ml-2">FAILED</span>
                )}
              </div>
              <span className="text-nw-muted/60 flex-shrink-0 font-mono text-[0.65rem]">
                {item.ip}
              </span>
              <span className="text-nw-muted/40 flex-shrink-0 text-[0.6rem]">
                {item.timestamp ? new Date(item.timestamp).toLocaleTimeString() : ''}
              </span>
            </div>
          ))
        )}
      </div>
    </div>
  );
}
