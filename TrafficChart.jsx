import React from 'react';
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Area, AreaChart,
} from 'recharts';
import { useTheme } from '../context/ThemeContext';

const CustomTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="glass-card p-3 !border-nw-accent/40 text-xs text-nw-text">
      <p className="opacity-70 mb-1">{label}</p>
      <p className="text-nw-accent font-semibold">
        {payload[0].value} packets
      </p>
    </div>
  );
};

export default function TrafficChart({ traffic }) {
  const { theme } = useTheme();
  const isDark = theme === 'dark';

  const gridColor = isDark ? '#1e293b' : '#e2e8f0';
  const axisColor = isDark ? '#475569' : '#94a3b8';
  const tickColor = isDark ? '#94a3b8' : '#64748b';

  const data = (traffic || []).map((item) => ({
    time: item.time ? item.time.slice(11, 19) : '',
    packets: item.packets || 0,
  }));

  return (
    <div className="glass-card p-5 animate-fade-in">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-sm font-semibold text-nw-text">Network Traffic</h3>
          <p className="text-xs text-nw-muted mt-0.5">Real-time packet flow</p>
        </div>
        <div className="flex items-center gap-2">
          <div className="glow-dot blue" />
          <span className="text-xs text-nw-muted">Live</span>
        </div>
      </div>

      <div className="h-64">
        {data.length === 0 ? (
          <div className="h-full flex items-center justify-center text-nw-muted text-sm">
            Waiting for traffic data...
          </div>
        ) : (
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={data} margin={{ top: 5, right: 5, left: -20, bottom: 0 }}>
              <defs>
                <linearGradient id="trafficGradient" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#3b82f6" stopOpacity={isDark ? 0.3 : 0.5} />
                  <stop offset="95%" stopColor="#3b82f6" stopOpacity={0} />
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
              <XAxis
                dataKey="time"
                stroke={axisColor}
                tick={{ fill: tickColor, fontSize: 10 }}
                tickLine={false}
                axisLine={false}
              />
              <YAxis
                stroke={axisColor}
                tick={{ fill: tickColor, fontSize: 10 }}
                tickLine={false}
                axisLine={false}
              />
              <Tooltip content={<CustomTooltip />} />
              <Area
                type="monotone"
                dataKey="packets"
                stroke="#3b82f6"
                strokeWidth={2}
                fill="url(#trafficGradient)"
                dot={false}
                activeDot={{ r: 4, fill: '#3b82f6', stroke: isDark ? '#0a0e1a' : '#ffffff', strokeWidth: 2 }}
              />
            </AreaChart>
          </ResponsiveContainer>
        )}
      </div>
    </div>
  );
}
