import { ComposedChart, Bar, XAxis, YAxis, ResponsiveContainer, Tooltip, Cell } from 'recharts';

function Candlestick({ x, y, width, height, payload }) {
  if (!payload) return null;
  const { open, high, low, close } = payload;
  const isUp = close >= open;
  const color = isUp ? '#22c55e' : '#ef4444';

  const range = high - low;
  const bodyTop = y + (height - (close - open) / range * height);
  const bodyHeight = Math.abs((close - open) / range * height) || 2;
  const cx = x + width / 2;

  return (
    <g>
      <line x1={cx} y1={y} x2={cx} y2={y + height} stroke={color} strokeWidth={1} />
      <rect
        x={x + 1}
        y={bodyTop}
        width={Math.max(width - 2, 4)}
        height={Math.max(bodyHeight, 2)}
        fill={color}
        stroke={color}
        strokeWidth={1}
        rx={1}
      />
    </g>
  );
}

export default function MiniChart({ prices, isUp }) {
  // US Stock: prices[0]=newest(May18), prices[-1]=oldest(May12) — reverse for left→right chronological
  const data = [...prices].reverse().map(p => ({
    date: p.dateShort,
    open: p.open,
    high: p.high,
    low: p.low,
    close: p.close,
    isUp: p.close >= p.open,
  }));

  const minPrice = Math.min(...data.map(d => d.low));
  const maxPrice = Math.max(...data.map(d => d.high));
  const pad = (maxPrice - minPrice) * 0.1;

  return (
    <div className="h-24">
      <ResponsiveContainer width="100%" height="100%">
        <ComposedChart data={data} margin={{ top: 4, right: 4, bottom: 4, left: 4 }}>
          <XAxis
            dataKey="date"
            tick={{ fill: '#64748b', fontSize: 10 }}
            axisLine={{ stroke: '#334155' }}
            tickLine={false}
          />
          <YAxis
            domain={[minPrice - pad, maxPrice + pad]}
            tick={{ fill: '#64748b', fontSize: 10 }}
            axisLine={false}
            tickLine={false}
            width={50}
            tickFormatter={v => v.toFixed(0)}
          />
          <Tooltip
            contentStyle={{
              background: '#1e293b',
              border: '1px solid #334155',
              borderRadius: '8px',
              fontSize: '12px',
              color: '#e2e8f0',
            }}
            labelStyle={{ color: '#94a3b8' }}
            formatter={(value, name) => {
              const labels = { open: '開', high: '高', low: '低', close: '收' };
              return [`${value.toFixed(2)}`, labels[name] || name];
            }}
          />
          <Bar dataKey="close" shape={<Candlestick />} isAnimationActive={false}>
            {data.map((_, i) => <Cell key={i} />)}
          </Bar>
        </ComposedChart>
      </ResponsiveContainer>
    </div>
  );
}
