import React from 'react';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell,
} from 'recharts';
import { useTheme } from '../context/ThemeContext';

const BAR_COLORS = ['#3b82f6', '#6366f1', '#8b5cf6', '#a855f7', '#c084fc', '#d8b4fe', '#818cf8', '#60a5fa', '#38bdf8', '#22d3ee'];
const PIE_COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444', '#8b5cf6', '#06b6d4'];

const CustomBarTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  const { ip, count, geo } = payload[0].payload;
  return (
    <div className="glass-card p-3 !border-nw-accent/40 text-xs">
      <p className="text-nw-accent font-mono mb-1">{ip}</p>
      {geo && geo.country !== 'Unknown' && (
        <p className="text-[0.65rem] text-nw-text/80 mb-1 flex items-center gap-1">
           {geo.country === 'Local' ? '🏠 Local Network' : `🌍 ${geo.city !== 'Unknown' ? geo.city + ', ' : ''}${geo.country}`}
        </p>
      )}
      <p className="text-nw-text font-semibold">{count} packets</p>
    </div>
  );
};

const CustomPieTooltip = ({ active, payload }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-card p-3 !border-nw-accent/40 text-xs text-nw-text">
      <p className="font-semibold">{payload[0].name}</p>
      <p className="opacity-70">{payload[0].value} packets</p>
    </div>
  );
};

export default function TopIPs({ topIPs, protocols }) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const gridColor = isDark ? '#1e293b' : '#e2e8f0';
  const axisColor = isDark ? '#475569' : '#94a3b8';
  const tickColor = isDark ? '#94a3b8' : '#64748b';

  const barData = (topIPs || []).map((item) => ({
    ip: item.ip?.length > 15 ? item.ip.slice(0, 12) + '...' : item.ip,
    fullIp: item.ip,
    count: item.count,
    geo: item.geo,
  }));

  const pieData = protocols || [];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* Top IPs Bar Chart */}
      <div className="glass-card p-5 animate-fade-in">
        <div className="mb-4">
          <h3 className="text-sm font-semibold text-nw-text">🌐 Top Source IPs</h3>
          <p className="text-xs text-nw-muted mt-0.5">Most active source addresses</p>
        </div>
        <div className="h-56">
          {barData.length === 0 ? (
            <div className="h-full flex items-center justify-center text-nw-muted text-sm">
              No IP data yet...
            </div>
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
                <XAxis
                  dataKey="ip"
                  stroke={axisColor}
                  tick={{ fill: tickColor, fontSize: 9 }}
                  tickLine={false}
                  axisLine={false}
                  angle={-30}
                  textAnchor="end"
                  height={50}
                />
                <YAxis
                  stroke={axisColor}
                  tick={{ fill: tickColor, fontSize: 10 }}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip content={<CustomBarTooltip />} />
                <Bar dataKey="count" radius={[4, 4, 0, 0]}>
                  {barData.map((_, idx) => (
                    <Cell key={idx} fill={BAR_COLORS[idx % BAR_COLORS.length]} />
                  ))}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          )}
        </div>
      </div>

      {/* Protocol Distribution Pie Chart */}
      <div className="glass-card p-5 animate-fade-in">
        <div className="mb-4">
          <h3 className="text-sm font-semibold text-nw-text">📊 Protocol Distribution</h3>
          <p className="text-xs text-nw-muted mt-0.5">Breakdown by protocol type</p>
        </div>
        <div className="h-56 flex items-center">
          {pieData.length === 0 ? (
            <div className="w-full text-center text-nw-muted text-sm">
              No protocol data yet...
            </div>
          ) : (
            <div className="flex items-center w-full gap-4">
              <div className="flex-1">
                <ResponsiveContainer width="100%" height={200}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      innerRadius={50}
                      outerRadius={80}
                      paddingAngle={3}
                      dataKey="value"
                      stroke={isDark ? '#111827' : '#ffffff'}
                      strokeWidth={2}
                    >
                      {pieData.map((_, idx) => (
                        <Cell key={idx} fill={PIE_COLORS[idx % PIE_COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomPieTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
              <div className="flex flex-col gap-2 min-w-[100px]">
                {pieData.map((entry, idx) => (
                  <div key={idx} className="flex items-center gap-2 text-xs">
                    <div
                      className="w-3 h-3 rounded-sm flex-shrink-0"
                      style={{ backgroundColor: PIE_COLORS[idx % PIE_COLORS.length] }}
                    />
                    <span className="text-nw-muted">{entry.name}</span>
                    <span className="text-nw-text font-medium ml-auto">{entry.value}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
