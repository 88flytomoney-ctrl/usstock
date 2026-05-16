#!/usr/bin/env python3
"""
US Stock Data Fetcher
- Fetches top 10 US stocks by turnover from ETNet
- Gets 5-day price data from Alpha Vantage
- Generates public/data/stocks.json for the GitHub Pages frontend
Usage:
    python scripts/fetch_usstock_data.py
"""
import sys
import os
import re
import json
import time
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Config
ETNET_URL = 'https://www.etnet.com.hk/www/tc/us-stocks/top20.php?tab=turnover'
ALPHA_VANTAGE_BASE_URL = 'https://www.alphavantage.co/query'
ALPHA_VANTAGE_API_KEY = os.environ.get('ALPHA_VANTAGE_API_KEY', '')
LIMIT = 10
OUTPUT_FILE = Path('public/data/stocks.json')
HISTORY_DIR = Path('public/data/history')

# US company names (symbol -> full name)
COMPANY_NAMES = {
    "TSLA": "Tesla Inc",
    "NVDA": "NVIDIA Corporation",
    "MU": "Micron Technology Inc",
    "MSFT": "Microsoft Corporation",
    "AMD": "Advanced Micro Devices Inc",
    "AAPL": "Apple Inc",
    "META": "Meta Platforms Inc",
    "GOOGL": "Alphabet Inc (Class A)",
    "AMZN": "Amazon.com Inc",
    "AVGO": "Broadcom Inc",
    "NFLX": "Netflix Inc",
    "ASML": "ASML Holding NV",
    "INTC": "Intel Corporation",
    "PLTR": "Palantir Technologies Inc",
    "MRVL": "Marvell Technology Inc",
    "LRCX": "Lam Research Corporation",
    "AMAT": "Applied Materials Inc",
    "QCOM": "QUALCOMM Inc",
    "TXN": "Texas Instruments Inc",
    "AVGO": "Broadcom Inc",
}


# ── Step 1: Fetch top 10 symbols from ETNet ─────────────────────────────────────
def fetch_etnet_top10():
    """Fetch US stocks top 10 by turnover from ETNet."""
    print('📡 Fetching ETNet US top 20...')
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
    }
    try:
        resp = requests.get(ETNET_URL, headers=headers, timeout=30)
        resp.raise_for_status()
        html = resp.text
    except Exception as e:
        print(f'❌ ETNet fetch failed: {e}')
        return None

    # Parse the embedded turnover chartdata JSON
    pattern = r'"turnover":\s*\{[^}]*"chartdata":\s*(\[[\s\S]*?\])'
    match = re.search(pattern, html)
    if not match:
        print('⚠️  Could not parse ETNet data')
        return None

    json_str = match.group(1)
    try:
        data = json.loads(json_str)
    except json.JSONDecodeError:
        last_valid = json_str.rfind('}]')
        if last_valid > 0:
            data = json.loads(json_str[:last_valid + 2])
        else:
            return None

    stocks = []
    for item in data:
        code = item.get('code', '').strip()
        name = item.get('name', '').strip()
        value = item.get('value', 0)
        if code:
            stocks.append({'code': code, 'name': name, 'turnover': value})

    stocks.sort(key=lambda x: x['turnover'], reverse=True)
    return stocks[:10]


# ── Step 2: Fetch Alpha Vantage daily prices ───────────────────────────────────
def fetch_alpha_vantage_prices(symbol):
    """Fetch 5-day daily prices for a symbol from Alpha Vantage."""
    if not ALPHA_VANTAGE_API_KEY:
        print(f'⚠️  ALPHA_VANTAGE_API_KEY not set, using mock data for {symbol}')
        return get_mock_prices(symbol)

    params = {
        'function': 'TIME_SERIES_DAILY',
        'symbol': symbol,
        'apikey': ALPHA_VANTAGE_API_KEY,
        'outputsize': 'compact',
    }
    try:
        resp = requests.get(ALPHA_VANTAGE_BASE_URL, params=params, timeout=30)
        data = resp.json()

        if 'Time Series (Daily)' not in data:
            error_msg = data.get('Note', data.get('Error Message', 'No data'))
            if 'rate limit' in error_msg.lower():
                print(f'⚠️  Rate limit hit')
                return None
            print(f'⚠️  {symbol}: {error_msg[:50]}')
            return get_mock_prices(symbol)

        time_series = data['Time Series (Daily)']
        sorted_dates = sorted(time_series.keys(), reverse=True)[:5]

        rows = []
        for date in sorted_dates:
            daily = time_series[date]
            rows.append({
                'date': date,
                'dateShort': datetime.strptime(date, '%Y-%m-%d').strftime('%m/%d'),
                'close': float(daily['4. close']),
                'open': float(daily['1. open']),
                'high': float(daily['2. high']),
                'low': float(daily['3. low']),
                'volume': int(daily['5. volume']),
                'volumeM': round(int(daily['5. volume']) / 1e6, 2),
            })
        return rows

    except Exception as e:
        print(f'❌ {symbol} fetch error: {e}')
        return get_mock_prices(symbol)


# ── Mock data ─────────────────────────────────────────────────────────────────
def get_mock_prices(symbol):
    """Return mock 5-day price data for a symbol."""
    import random
    random.seed(hash(symbol) % 1000)
    base_prices = {
        'TSLA': 250, 'NVDA': 500, 'AAPL': 180, 'MSFT': 400,
        'META': 500, 'GOOGL': 175, 'AMZN': 185, 'AMD': 160,
        'AVGO': 1200, 'NFLX': 600, 'ASML': 850, 'INTC': 30,
    }
    base = base_prices.get(symbol, 100)
    today = datetime.now().date()
    rows = []
    for i in range(5):
        d = today - timedelta(days=4 - i)
        close = round(base * (1 + random.uniform(-0.03, 0.03)), 2)
        open_p = round(close * (1 + random.uniform(-0.01, 0.01)), 2)
        high = round(max(close, open_p) * (1 + random.uniform(0, 0.01)), 2)
        low = round(min(close, open_p) * (1 - random.uniform(0, 0.01)), 2)
        vol = int(random.uniform(5e6, 50e6))
        rows.append({
            'date': d.strftime('%Y-%m-%d'),
            'dateShort': d.strftime('%m/%d'),
            'close': close, 'open': open_p, 'high': high, 'low': low,
            'volume': vol, 'volumeM': round(vol / 1e6, 1),
        })
        base = close
    return rows


# ── Analysis ───────────────────────────────────────────────────────────────────
def analyze_stock(stock):
    """Simple rule-based analysis."""
    prices = stock.get('prices', [])
    if not prices:
        return _empty_analysis()

    last = prices[-1]['close']
    first = prices[0]['close']
    pct = stock.get('fiveDayPct', 0)
    high = stock.get('high5', last)
    low = stock.get('low5', last)

    # Trend
    if len(prices) >= 3:
        mid = len(prices) // 2
        first_half = sum(p['close'] for p in prices[:mid]) / mid
        second_half = sum(p['close'] for p in prices[mid:]) / (len(prices) - mid)
        if second_half > first_half * 1.02:
            trend = 'uptrend'
        elif second_half < first_half * 0.98:
            trend = 'downtrend'
        else:
            trend = 'sideways'
    else:
        trend = 'neutral'

    # Volume signal
    vols = [p['volume'] for p in prices]
    if len(vols) >= 3:
        recent_avg = sum(vols[-2:]) / 2
        older_avg = sum(vols[:-2]) / max(len(vols) - 2, 1)
        if recent_avg > older_avg * 1.3:
            vol_signal = 'volume surge'
        elif recent_avg < older_avg * 0.7:
            vol_signal = 'volume decline'
        else:
            vol_signal = 'stable'
    else:
        vol_signal = 'neutral'

    # Signal
    if pct > 5 and trend == 'uptrend' and vol_signal == 'volume surge':
        signal = 'strong buy'
    elif pct > 2 and trend == 'uptrend':
        signal = 'buy'
    elif pct > 0 and vol_signal == 'volume surge':
        signal = 'buy'
    elif pct < -5 and trend == 'downtrend' and vol_signal == 'volume surge':
        signal = 'strong sell'
    elif pct < -3:
        signal = 'sell'
    elif pct < -1:
        signal = 'watch'
    else:
        signal = 'hold'

    # Support / Resistance
    support = round(low * 1.02, 2)
    resistance = round(high * 0.98, 2)

    # Summary
    name = stock.get('name', stock.get('code', ''))
    trend_map = {'uptrend': '上升', 'downtrend': '下跌', 'sideways': '震盪', 'neutral': '中性'}
    trend_cn = trend_map.get(trend, '震盪')
    signal_map = {
        'strong buy': '強烈買入', 'buy': '買入', 'hold': '持有',
        'watch': '觀望', 'sell': '賣出', 'strong sell': '強烈賣出',
    }
    signal_cn = signal_map.get(signal, '持有')
    vol_cn = {'volume surge': '成交量放大', 'volume decline': '成交量萎縮', 'stable': '成交量穩定'}.get(vol_signal, '')
    summary = f"{name}五日走勢{trend_cn}，累積變動{pct:+.2f}%。"
    if vol_cn:
        summary += vol_cn + '。'
    summary += f"技術信號：{signal_cn}。"

    return {
        'signal': signal,
        'summary': summary,
        'trend': trend,
        'volumeSignal': vol_signal,
        'support': support,
        'resistance': resistance,
        'generatedAt': datetime.now().strftime('%Y-%m-%d %H:%M'),
    }


def _empty_analysis():
    return {
        'signal': 'neutral', 'summary': '暂无数据',
        'trend': 'neutral', 'volumeSignal': 'neutral',
        'support': 0, 'resistance': 0,
        'generatedAt': datetime.now().strftime('%Y-%m-%d %H:%M'),
    }


# ── Generate market summary ────────────────────────────────────────────────────
def generate_summary(stocks):
    gainers = [s for s in stocks if s['fiveDayPct'] > 0]
    losers = [s for s in stocks if s['fiveDayPct'] < 0]
    avg_pct = sum(s['fiveDayPct'] for s in stocks) / len(stocks) if stocks else 0
    top_gainer = max(stocks, key=lambda s: s['fiveDayPct']) if stocks else None
    top_loser = min(stocks, key=lambda s: s['fiveDayPct']) if stocks else None

    summary = (
        f"今日追蹤 {len(stocks)} 檔熱門美股，五日整體平均{('上漲' if avg_pct > 0 else '下跌')}"
        f"{abs(avg_pct):.2f}%。"
    )
    if top_gainer:
        summary += f"表現最佳：{top_gainer['name']}（{top_gainer['code']}）{top_gainer['fiveDayPct']:+.2f}%，"
    if top_loser:
        summary += f"表現最弱：{top_loser['name']}（{top_loser['code']}）{top_loser['fiveDayPct']:+.2f}%。"
    summary += f"上漲 {len(gainers)} 檔，下跌 {len(losers)} 檔。"
    return summary


# ── Main ────────────────────────────────────────────────────────────────────────
def main():
    print(f"🚀 US Stock fetcher started at {datetime.now().strftime('%Y-%m-%d %H:%M')}")

    # 1. Get top 10 symbols from ETNet
    etnet_stocks = fetch_etnet_top10()
    if etnet_stocks:
        symbols = [s['code'] for s in etnet_stocks]
        name_map = {s['code']: s['name'] for s in etnet_stocks}
        print(f'📊 Top10 from ETNet: {", ".join(symbols)}')
    else:
        # Fallback symbols
        symbols = ['TSLA', 'NVDA', 'AAPL', 'MSFT', 'META', 'GOOGL', 'AMZN', 'AMD', 'AVGO', 'NFLX']
        name_map = COMPANY_NAMES
        print(f'📊 Using fallback symbols: {", ".join(symbols)}')

    # 2. Fetch prices for each symbol
    results = []
    rate_limit_hit = False

    for i, symbol in enumerate(symbols):
        company_name = name_map.get(symbol, COMPANY_NAMES.get(symbol, symbol))
        print(f'[{i+1}/{len(symbols)}] {symbol} ({company_name})...', end='', flush=True)

        prices = fetch_alpha_vantage_prices(symbol)
        if prices is None:
            print(' ⚠️ Rate limit')
            rate_limit_hit = True
            break

        if not prices:
            print(' ❌ No data')
            continue

        # Calculate metrics (prices[0]=newest, prices[-1]=oldest)
        first_close = prices[-1]['close']
        last_close = prices[0]['close']
        five_day_pct = round((last_close / first_close - 1) * 100, 2)
        high_5 = max(p['high'] for p in prices)
        low_5 = min(p['low'] for p in prices)
        avg_vol = sum(p['volume'] for p in prices) / len(prices)
        vol_trend = '↑' if prices[-1]['volume'] > avg_vol else '↓'

        stock = {
            'code': symbol,
            'symbol': symbol,
            'name': company_name,
            'prices': prices,
            'fiveDayPct': five_day_pct,
            'high5': high_5,
            'low5': low_5,
            'avgVolume': avg_vol,
            'volTrend': vol_trend,
        }
        results.append(stock)
        print(f' ✅ {five_day_pct:+.2f}%')

        # Rate limit protection: Alpha Vantage free tier = 5 req/min
        if i < len(symbols) - 1:
            time.sleep(15)

    if not results:
        print('❌ No stock data fetched')
        sys.exit(1)

    # 3. Run analysis
    print('🤖 Running analysis...')
    for stock in results:
        stock['analysis'] = analyze_stock(stock)
    ai_summary = generate_summary(results)

    # 4. Build output
    output = {
        'generatedAt': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'generatedDate': datetime.now().strftime('%Y-%m-%d'),
        'stockCount': len(results),
        'stocks': results,
        'aiSummary': ai_summary,
    }

    # 5. Write stocks.json
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 6. Write history snapshot
    HISTORY_DIR.mkdir(parents=True, exist_ok=True)
    date_str = datetime.now().strftime('%Y-%m-%d')
    history_file = HISTORY_DIR / f'{date_str}.json'
    with open(history_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    # 7. Update manifest
    manifest_file = HISTORY_DIR / 'manifest.json'
    existing_dates = []
    if manifest_file.exists():
        with open(manifest_file, 'r', encoding='utf-8') as f:
            existing_dates = json.load(f)
    if date_str not in existing_dates:
        existing_dates.append(date_str)
        existing_dates.sort(reverse=True)
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(existing_dates, f, ensure_ascii=False)

    print(f'✅ Done! Written to {OUTPUT_FILE}')
    print(f'   History: {history_file}')
    print(f'   Stocks: {len(results)}')
    print(f'   Summary: {ai_summary[:80]}...')


if __name__ == '__main__':
    main()