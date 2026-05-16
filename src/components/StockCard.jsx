import MiniChart from './MiniChart.jsx';

const SIGNAL_COLORS = {
  'strong buy': { bg: 'bg-blue-900/40', text: 'text-blue-400', label: '💎 強烈買入' },
  'buy': { bg: 'bg-blue-900/30', text: 'text-blue-300', label: '✅ 買入' },
  'hold': { bg: 'bg-slate-800', text: 'text-slate-300', label: '⏸ 持有' },
  'watch': { bg: 'bg-yellow-900/30', text: 'text-yellow-400', label: '👁 觀望' },
  'sell': { bg: 'bg-orange-900/30', text: 'text-orange-400', label: '⚠️ 賣出' },
  'strong sell': { bg: 'bg-red-900/40', text: 'text-red-400', label: '🔴 強烈賣出' },
  'neutral': { bg: 'bg-slate-800', text: 'text-slate-400', label: '➖ 中性' },
};

function getSignalStyle(signal) {
  return SIGNAL_COLORS[signal] || SIGNAL_COLORS['neutral'];
}

export default function StockCard({ stock }) {
  const { code, name, symbol, prices, fiveDayPct, analysis } = stock;
  const isUp = fiveDayPct >= 0;
  const arrow = isUp ? '▲' : '▼';

  const sigStyle = getSignalStyle(analysis?.signal || 'neutral');
  const trendIcon = analysis?.trend === 'uptrend' ? '↗' : analysis?.trend === 'downtrend' ? '↘' : '→';
  const volIcon = analysis?.volumeSignal === 'volume surge' ? '🔥' : analysis?.volumeSignal === 'volume decline' ? '📉' : '➡';

  return (
    <div className="card space-y-3">
      <div className="flex items-start justify-between">
        <div>
          <div className="flex items-center gap-2">
            <span className="font-mono text-sm text-slate-400">{code}</span>
            <span className={`badge ${isUp ? 'badge-up' : 'badge-down'}`}>
              {arrow} {Math.abs(fiveDayPct).toFixed(2)}%
            </span>
          </div>
          <h3 className="font-bold text-white text-base mt-0.5">{name}</h3>
          <p className="text-xs text-slate-500">{symbol}</p>
        </div>
        <div className={`badge ${sigStyle.bg} ${sigStyle.text} text-xs`}>
          {sigStyle.label}
        </div>
      </div>

      {prices?.length > 0 && (
        <MiniChart prices={prices} isUp={isUp} />
      )}

      {prices?.length > 0 && (
        <div className="flex items-baseline justify-between border-t border-slate-700 pt-2">
          <div>
            <span className="text-2xl font-bold text-white">
              ${prices[prices.length - 1].close.toFixed(2)}
            </span>
            <span className="text-sm text-slate-400 ml-1">USD</span>
          </div>
          <div className="text-right text-xs text-slate-400 space-y-0.5">
            <p>5日高 ${prices[prices.length - 1].high?.toFixed(2) || '–'}</p>
            <p>5日低 ${prices[prices.length - 1].low?.toFixed(2) || '–'}</p>
          </div>
        </div>
      )}

      <div className="flex items-center justify-between text-xs text-slate-400">
        <div className="flex items-center gap-3">
          <span>趨勢 {trendIcon}</span>
          <span>量 {volIcon}</span>
        </div>
        {analysis?.support > 0 && (
          <span className="text-green-400">撐 ${analysis.support.toFixed(2)}</span>
        )}
        {analysis?.resistance > 0 && (
          <span className="text-red-400">壓 ${analysis.resistance.toFixed(2)}</span>
        )}
      </div>

      {analysis?.summary && (
        <div className="bg-slate-900/60 rounded-lg p-3 text-xs text-slate-300 leading-relaxed">
          🤖 {analysis.summary}
        </div>
      )}

      {prices?.length > 0 && (
        <div className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-slate-500 border-b border-slate-700">
                <th className="text-left py-1">日期</th>
                <th className="text-right">開</th>
                <th className="text-right">高</th>
                <th className="text-right">低</th>
                <th className="text-right">收</th>
                <th className="text-right">量(M)</th>
              </tr>
            </thead>
            <tbody>
              {prices.map((p, i) => (
                <tr key={p.date} className={`border-b border-slate-800 ${i === prices.length - 1 ? 'bg-slate-700/30' : ''}`}>
                  <td className="py-1 text-slate-400">{p.dateShort}</td>
                  <td className="text-right text-slate-300">${p.open?.toFixed(2)}</td>
                  <td className="text-right text-red-400">${p.high?.toFixed(2)}</td>
                  <td className="text-right text-green-400">${p.low?.toFixed(2)}</td>
                  <td className={`text-right font-medium ${i > 0 && p.close > prices[i-1]?.close ? 'text-red-400' : 'text-green-400'}`}>
                    ${p.close.toFixed(2)}
                  </td>
                  <td className="text-right text-slate-400">{p.volumeM}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}