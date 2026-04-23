import urllib.request
import re
import time
from datetime import datetime

def get_optimized_list():
    """거래대금이 어느 정도 있는 종목 위주로 200개만 가져와 속도를 높입니다."""
    stock_list = {}
    # 1~4페이지만 훑어도 우량/활발 종목 200개는 충분히 확보됩니다.
    for page in range(1, 5):
        url = f"https://finance.naver.com/sise/sise_market_sum.naver?sosok=0&page={page}"
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req).read().decode('cp949')
            items = re.findall(r'href="/item/main\.naver\?code=(\d{6})".*?>(.*?)</a>', html)
            for code, name in items: stock_list[code] = name
        except: break
        time.sleep(0.1)
    return stock_list

def get_stock_data(symbol):
    url = f"https://fchart.stock.naver.com/sise.nhn?symbol={symbol}&timeframe=day&count=300&requestType=0"
    try:
        req = urllib.request.urlopen(url)
        xml_data = req.read().decode('euc-kr')
        lines = xml_data.split('<item data="')[1:]
        return [{'close': int(val.split('|')[4]), 'high': int(val.split('|')[2]), 'vol': int(val.split('|')[5])} 
                for val in [line.split('"')[0] for line in lines]]
    except: return None

def run_scanner():
    target_stocks = get_optimized_list()
    found_stocks = []
    print(f"🚀 핵심 {len(target_stocks)}개 종목 쾌속 분석 시작...")

    for symbol, name in target_stocks.items():
        data = get_stock_data(symbol)
        if not data or len(data) < 224: continue
        
        curr, prev = data[-1], data[-2]
        ma224 = sum([x['close'] for x in data[-224:]]) / 224
        recent_20_high = max([x['high'] for x in data[-21:-1]])
        
        # 단테 기법: 224일선 위 + 언덕 돌파 + 거래량 1.5배
        if curr['close'] > recent_20_high and curr['close'] > ma224 and curr['vol'] > prev['vol'] * 1.5:
            found_stocks.append({
                'name': name, 'code': symbol, 'price': f"{curr['close']:,}", 
                'ma224': f"{int(ma224):,}", 'vol_ratio': round(curr['vol']/prev['vol'], 1)
            })
    
    # --- UI 디자인 (카드형) ---
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{ background: #111; color: #eee; font-family: sans-serif; padding: 20px; }}
            .grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(280px, 1fr)); gap: 15px; }}
            .card {{ background: #222; border-left: 5px solid #f23645; padding: 15px; border-radius: 8px; }}
            .name {{ font-size: 18px; font-weight: bold; color: #fff; }}
            .price {{ font-size: 22px; color: #f23645; margin: 10px 0; font-weight: bold; }}
            .label {{ font-size: 12px; color: #888; }}
        </style>
    </head>
    <body>
        <h2>🎯 단테 포착 (핵심 종목군)</h2>
        <p class="label">업데이트: {datetime.now().strftime('%m-%d %H:%M')}</p>
        <div class="grid">
    """
    for s in found_stocks:
        html_content += f"""
            <div class="card">
                <div class="name">{s['name']} ({s['code']})</div>
                <div class="price">{s['price']}원</div>
                <div class="label">224일선: {s['ma224']}원 / 거래량: {s['vol_ratio']}배 🔥</div>
            </div>
        """
    html_content += "</div></body></html>"
    with open("index.html", "w", encoding="utf-8") as f: f.write(html_content)

if __name__ == "__main__": run_scanner()
