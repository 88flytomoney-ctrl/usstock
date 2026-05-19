import { LineChart, Line, ResponsiveContainer, Tooltip } from 'recharts';

export default function MiniChart({ prices, isUp }) {
  const data = prices.map(p => ({
    date: p.dateShort,
    close: p.close,
    volume: p.volumeM,
  }));

  const color = isUp ? '#22c55e' : '#ef4444';

  return (
    <div className="h-20">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
          <Tooltip
            contentStyle={{
              background: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '8px',
              fontSize: '12px',
              color: '#e2e8f0',
            }}
            labelStyle={{ color: '#94a3b8' }}
            formatter={(value) => [value.toFixed(2), '收盤']}
          />
          <Line
            type="monotone"
            dataKey="close"
            stroke={color}
            strokeWidth={2}
            dot={{ r: 3, fill: color, strokeWidth: 0 }}
            activeDot={{ r: 5, fill: color, strokeWidth: 0 }}
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}